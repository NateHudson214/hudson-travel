import pytest
from fastapi.testclient import TestClient

from backend.app.geoapify import (
    GeoapifyConfigurationError,
    GeoapifyProviderError,
    ZipLocation,
    ZipLocationNotFoundError,
)
from backend.app.main import app
from backend.app.places import NearbyHotel


FAKE_SECRET = "nearby-route-secret-that-must-not-appear"


def test_nearby_hotels_route_preserves_zip_and_uses_resolved_coordinates(
    client: TestClient,
) -> None:
    async def successful_location_lookup(postcode: str) -> ZipLocation:
        assert postcode == "02113"
        return ZipLocation(
            postcode="02113",
            country_code="us",
            latitude=42.365,
            longitude=-71.055,
            locality="Boston",
        )

    async def successful_hotels_lookup(
        latitude: float, longitude: float
    ) -> list[NearbyHotel]:
        assert latitude == 42.365
        assert longitude == -71.055
        return [
            NearbyHotel(
                place_id="provider-place-1",
                name="Example Hotel",
                formatted_address=None,
                latitude=42.366,
                longitude=-71.054,
                distance_meters=150.0,
            )
        ]

    app.state.zip_location_lookup = successful_location_lookup
    app.state.nearby_hotels_lookup = successful_hotels_lookup

    response = client.get(
        "/api/hotels/nearby", params={"zip_code": "  02113  "}
    )

    assert response.status_code == 200
    assert response.json() == {
        "location": {
            "postcode": "02113",
            "country_code": "us",
            "latitude": 42.365,
            "longitude": -71.055,
            "locality": "Boston",
        },
        "radius_meters": 5000,
        "result_limit": 20,
        "hotels": [
            {
                "place_id": "provider-place-1",
                "name": "Example Hotel",
                "formatted_address": None,
                "latitude": 42.366,
                "longitude": -71.054,
                "distance_meters": 150.0,
            }
        ],
    }


def test_nearby_hotels_route_returns_successful_empty_result(
    client: TestClient,
) -> None:
    async def successful_location_lookup(postcode: str) -> ZipLocation:
        return ZipLocation(postcode, "us", 40.8, -77.86, "State College")

    async def empty_hotels_lookup(
        latitude: float, longitude: float
    ) -> list[NearbyHotel]:
        return []

    app.state.zip_location_lookup = successful_location_lookup
    app.state.nearby_hotels_lookup = empty_hotels_lookup

    response = client.get(
        "/api/hotels/nearby", params={"zip_code": "16802"}
    )

    assert response.status_code == 200
    assert response.json()["hotels"] == []


@pytest.mark.parametrize(
    "submitted_zip",
    [None, "", "   ", "1234", "123456", "12a45", "12-45", "１２３４５"],
)
def test_nearby_hotels_route_rejects_invalid_zip_before_provider_calls(
    client: TestClient, submitted_zip: str | None
) -> None:
    provider_was_called = False

    async def unexpected_location_lookup(postcode: str) -> ZipLocation:
        nonlocal provider_was_called
        provider_was_called = True
        raise AssertionError("Provider must not run for invalid ZIP input.")

    app.state.zip_location_lookup = unexpected_location_lookup
    params = {} if submitted_zip is None else {"zip_code": submitted_zip}

    response = client.get("/api/hotels/nearby", params=params)

    assert response.status_code == 400
    assert response.json() == {"detail": "Enter a five-digit U.S. ZIP code."}
    assert provider_was_called is False


@pytest.mark.parametrize(
    ("controller_error", "expected_status", "expected_detail"),
    [
        (
            ZipLocationNotFoundError(FAKE_SECRET),
            404,
            "ZIP 16802 could not be resolved.",
        ),
        (
            GeoapifyConfigurationError(FAKE_SECRET),
            503,
            "Geoapify is not configured.",
        ),
        (
            GeoapifyProviderError(FAKE_SECRET),
            502,
            "The location service is temporarily unavailable.",
        ),
    ],
)
def test_nearby_hotels_route_maps_location_errors_safely(
    client: TestClient,
    controller_error: Exception,
    expected_status: int,
    expected_detail: str,
) -> None:
    async def failed_location_lookup(postcode: str) -> ZipLocation:
        raise controller_error

    app.state.zip_location_lookup = failed_location_lookup

    response = client.get(
        "/api/hotels/nearby", params={"zip_code": "16802"}
    )

    assert response.status_code == expected_status
    assert response.json() == {"detail": expected_detail}
    assert FAKE_SECRET not in response.text


@pytest.mark.parametrize(
    ("controller_error", "expected_status", "expected_detail"),
    [
        (
            GeoapifyConfigurationError(FAKE_SECRET),
            503,
            "Geoapify is not configured.",
        ),
        (
            GeoapifyProviderError(FAKE_SECRET),
            502,
            "The nearby hotel service is temporarily unavailable.",
        ),
    ],
)
def test_nearby_hotels_route_maps_places_errors_safely(
    client: TestClient,
    controller_error: Exception,
    expected_status: int,
    expected_detail: str,
) -> None:
    async def successful_location_lookup(postcode: str) -> ZipLocation:
        return ZipLocation(postcode, "us", 40.8, -77.86, "State College")

    async def failed_hotels_lookup(
        latitude: float, longitude: float
    ) -> list[NearbyHotel]:
        raise controller_error

    app.state.zip_location_lookup = successful_location_lookup
    app.state.nearby_hotels_lookup = failed_hotels_lookup

    response = client.get(
        "/api/hotels/nearby", params={"zip_code": "16802"}
    )

    assert response.status_code == expected_status
    assert response.json() == {"detail": expected_detail}
    assert FAKE_SECRET not in response.text
