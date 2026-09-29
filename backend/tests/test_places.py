import asyncio
from collections.abc import Callable

import httpx
import pytest

from backend.app.geoapify import (
    GeoapifyConfigurationError,
    GeoapifyProviderError,
)
from backend.app.places import (
    GEOAPIFY_PLACES_URL,
    NearbyHotel,
    lookup_nearby_hotels,
)


FAKE_API_KEY = "fake-places-key-for-tests"
SEARCH_LATITUDE = 40.803167822
SEARCH_LONGITUDE = -77.861384958


def places_response(*features: object) -> dict[str, object]:
    return {"type": "FeatureCollection", "features": list(features)}


def hotel_feature(**overrides: object) -> dict[str, object]:
    properties: dict[str, object] = {
        "place_id": "provider-place-1",
        "name": "Example Hotel",
        "formatted": "100 Example Street, State College, PA",
        "lat": 40.8,
        "lon": -77.86,
        "distance": 420,
    }
    properties.update(overrides)
    return {"type": "Feature", "properties": properties}


def run_lookup(
    handler: Callable[[httpx.Request], httpx.Response],
    *,
    api_key: str | None = FAKE_API_KEY,
) -> list[NearbyHotel]:
    async def run() -> list[NearbyHotel]:
        transport = httpx.MockTransport(handler)
        async with httpx.AsyncClient(transport=transport) as client:
            return await lookup_nearby_hotels(
                SEARCH_LATITUDE,
                SEARCH_LONGITUDE,
                api_key_provider=lambda: api_key,
                client=client,
            )

    return asyncio.run(run())


def test_lookup_sends_exact_places_parameters_and_sanitizes_fields() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert str(request.url.copy_with(query=None)) == GEOAPIFY_PLACES_URL
        assert request.url.params["categories"] == "accommodation.hotel"
        assert request.url.params["filter"] == (
            "circle:-77.861384958,40.803167822,5000"
        )
        assert request.url.params["bias"] == (
            "proximity:-77.861384958,40.803167822"
        )
        assert request.url.params["limit"] == "20"
        assert request.url.params["apiKey"] == FAKE_API_KEY
        return httpx.Response(200, json=places_response(hotel_feature()))

    assert run_lookup(handler) == [
        NearbyHotel(
            place_id="provider-place-1",
            name="Example Hotel",
            formatted_address="100 Example Street, State College, PA",
            latitude=40.8,
            longitude=-77.86,
            distance_meters=420.0,
        )
    ]


def test_lookup_preserves_honest_optional_fields() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json=places_response(
                hotel_feature(name=None, formatted="   ", distance="nearby")
            ),
        )

    hotel = run_lookup(handler)[0]
    assert hotel.name is None
    assert hotel.formatted_address is None
    assert hotel.distance_meters is None


@pytest.mark.parametrize(
    "invalid_feature",
    [
        None,
        [],
        {},
        {"properties": "invalid"},
        hotel_feature(place_id="   "),
        hotel_feature(lat=None),
        hotel_feature(lat=True),
        hotel_feature(lat=91),
        hotel_feature(lon="-77.86"),
        hotel_feature(lon=-181),
    ],
)
def test_lookup_excludes_features_without_identity_or_valid_coordinates(
    invalid_feature: object,
) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json=places_response(invalid_feature, hotel_feature()),
        )

    assert [hotel.place_id for hotel in run_lookup(handler)] == [
        "provider-place-1"
    ]


def test_lookup_accepts_a_successful_empty_feature_collection() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=places_response())

    assert run_lookup(handler) == []


def test_lookup_rejects_missing_configuration_without_provider_request() -> None:
    request_was_made = False

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal request_was_made
        request_was_made = True
        return httpx.Response(200, json=places_response())

    with pytest.raises(GeoapifyConfigurationError, match="not configured"):
        run_lookup(handler, api_key=None)

    assert request_was_made is False


@pytest.mark.parametrize("failure", ["timeout", "network", "http", "json"])
def test_lookup_sanitizes_provider_failures(failure: str) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if failure == "timeout":
            raise httpx.ReadTimeout(
                f"timeout with {FAKE_API_KEY} at {GEOAPIFY_PLACES_URL}",
                request=request,
            )
        if failure == "network":
            raise httpx.ConnectError(
                f"network error with {FAKE_API_KEY}", request=request
            )
        if failure == "http":
            return httpx.Response(429, json={"message": FAKE_API_KEY})
        return httpx.Response(200, content=b"not-json")

    with pytest.raises(GeoapifyProviderError) as captured_error:
        run_lookup(handler)

    assert str(captured_error.value) == (
        "Geoapify could not complete the nearby-hotel lookup."
    )
    assert FAKE_API_KEY not in str(captured_error.value)
    assert GEOAPIFY_PLACES_URL not in str(captured_error.value)


@pytest.mark.parametrize(
    "payload",
    [
        None,
        [],
        {},
        {"type": "FeatureCollection", "features": "invalid"},
        {"type": "invalid", "features": []},
    ],
)
def test_lookup_rejects_malformed_top_level_data_without_credentials(
    payload: object,
) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if payload is None:
            return httpx.Response(200, content=b"null")
        return httpx.Response(200, json=payload)

    with pytest.raises(GeoapifyProviderError) as captured_error:
        run_lookup(handler)

    assert str(captured_error.value) == (
        "Geoapify returned an invalid nearby-hotel response."
    )
    assert FAKE_API_KEY not in str(captured_error.value)
    assert GEOAPIFY_PLACES_URL not in str(captured_error.value)
