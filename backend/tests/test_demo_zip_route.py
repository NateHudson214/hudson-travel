import pytest
from fastapi.testclient import TestClient

from backend.app.geoapify import (
    GeoapifyConfigurationError,
    GeoapifyProviderError,
    ZipLocation,
    ZipLocationNotFoundError,
)
from backend.app.main import app


FAKE_SECRET = "credential-that-must-not-appear"


def test_demo_zip_route_returns_only_the_small_location_response(
    client: TestClient,
) -> None:
    async def successful_lookup(postcode: str) -> ZipLocation:
        assert postcode == "16802"
        return ZipLocation(
            postcode="16802",
            country_code="us",
            latitude=40.7955,
            longitude=-77.8619,
            locality="University Park",
        )

    app.state.zip_location_lookup = successful_lookup

    response = client.get("/api/demo/zip-location")

    assert response.status_code == 200
    assert response.json() == {
        "postcode": "16802",
        "country_code": "us",
        "latitude": 40.7955,
        "longitude": -77.8619,
        "locality": "University Park",
    }


@pytest.mark.parametrize(
    ("controller_error", "expected_status", "expected_detail"),
    [
        (
            GeoapifyConfigurationError(FAKE_SECRET),
            503,
            "Geoapify is not configured.",
        ),
        (
            ZipLocationNotFoundError(FAKE_SECRET),
            404,
            "ZIP 16802 could not be resolved.",
        ),
        (
            GeoapifyProviderError(FAKE_SECRET),
            502,
            "The location service is temporarily unavailable.",
        ),
    ],
)
def test_demo_zip_route_maps_controller_errors_without_exposing_details(
    client: TestClient,
    controller_error: Exception,
    expected_status: int,
    expected_detail: str,
) -> None:
    async def failed_lookup(postcode: str) -> ZipLocation:
        assert postcode == "16802"
        raise controller_error

    app.state.zip_location_lookup = failed_lookup

    response = client.get("/api/demo/zip-location")

    assert response.status_code == expected_status
    assert response.json() == {"detail": expected_detail}
    assert FAKE_SECRET not in response.text
