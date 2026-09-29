import pytest
from fastapi.testclient import TestClient

from backend.app.geoapify import (
    GeoapifyConfigurationError,
    GeoapifyProviderError,
    ZipLocation,
    ZipLocationNotFoundError,
)
from backend.app.main import app


FAKE_SECRET = "dynamic-route-secret-that-must-not-appear"


@pytest.mark.parametrize(
    ("submitted_zip", "expected_zip"),
    [("16802", "16802"), ("02113", "02113"), ("  16802  ", "16802")],
)
def test_dynamic_zip_route_passes_the_validated_string_to_the_controller(
    client: TestClient, submitted_zip: str, expected_zip: str
) -> None:
    async def successful_lookup(postcode: str) -> ZipLocation:
        assert postcode == expected_zip
        return ZipLocation(
            postcode=postcode,
            country_code="us",
            latitude=40.0,
            longitude=-77.0,
            locality="Test Locality",
        )

    app.state.zip_location_lookup = successful_lookup

    response = client.get("/api/zip-location", params={"zip_code": submitted_zip})

    assert response.status_code == 200
    assert response.json() == {
        "postcode": expected_zip,
        "country_code": "us",
        "latitude": 40.0,
        "longitude": -77.0,
        "locality": "Test Locality",
    }


@pytest.mark.parametrize(
    "submitted_zip",
    [None, "", "   ", "1234", "123456", "12a45", "12-45", "１２３４５", "123 4"],
)
def test_dynamic_zip_route_rejects_invalid_input_without_calling_controller(
    client: TestClient, submitted_zip: str | None
) -> None:
    controller_was_called = False

    async def unexpected_lookup(postcode: str) -> ZipLocation:
        nonlocal controller_was_called
        controller_was_called = True
        raise AssertionError("Controller must not run for invalid input.")

    app.state.zip_location_lookup = unexpected_lookup
    params = {} if submitted_zip is None else {"zip_code": submitted_zip}

    response = client.get("/api/zip-location", params=params)

    assert response.status_code == 400
    assert response.json() == {"detail": "Enter a five-digit U.S. ZIP code."}
    assert controller_was_called is False


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
def test_dynamic_zip_route_maps_safe_controller_errors(
    client: TestClient,
    controller_error: Exception,
    expected_status: int,
    expected_detail: str,
) -> None:
    async def failed_lookup(postcode: str) -> ZipLocation:
        assert postcode == "16802"
        raise controller_error

    app.state.zip_location_lookup = failed_lookup

    response = client.get("/api/zip-location", params={"zip_code": "16802"})

    assert response.status_code == expected_status
    assert response.json() == {"detail": expected_detail}
    assert FAKE_SECRET not in response.text
