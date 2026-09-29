import asyncio
from collections.abc import Callable

import httpx
import pytest

from backend.app.geoapify import (
    GEOAPIFY_GEOCODING_URL,
    GeoapifyConfigurationError,
    GeoapifyProviderError,
    ZipLocation,
    ZipLocationNotFoundError,
    lookup_zip_location,
)


FAKE_API_KEY = "fake-provider-key-for-tests"


def run_lookup(
    handler: Callable[[httpx.Request], httpx.Response],
    *,
    api_key: str | None = FAKE_API_KEY,
) -> ZipLocation:
    async def run() -> ZipLocation:
        transport = httpx.MockTransport(handler)
        async with httpx.AsyncClient(transport=transport) as client:
            return await lookup_zip_location(
                "16802", api_key_provider=lambda: api_key, client=client
            )

    return asyncio.run(run())


def location_response(**overrides: object) -> dict[str, object]:
    result: dict[str, object] = {
        "postcode": "16802",
        "country_code": "us",
        "lat": 40.7955,
        "lon": -77.8619,
        "city": "University Park",
    }
    result.update(overrides)
    return {"results": [result]}


def test_lookup_resolves_zip_16802_and_sends_required_parameters() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert str(request.url.copy_with(query=None)) == GEOAPIFY_GEOCODING_URL
        assert request.url.params["postcode"] == "16802"
        assert request.url.params["type"] == "postcode"
        assert request.url.params["filter"] == "countrycode:us"
        assert request.url.params["format"] == "json"
        assert request.url.params["apiKey"] == FAKE_API_KEY
        return httpx.Response(200, json=location_response())

    assert run_lookup(handler) == ZipLocation(
        postcode="16802",
        country_code="us",
        latitude=40.7955,
        longitude=-77.8619,
        locality="University Park",
    )


@pytest.mark.parametrize(
    "payload",
    [
        location_response(postcode="16801"),
        location_response(country_code="ca"),
        location_response(lat=None),
        location_response(lat=True),
        location_response(lat=91),
        location_response(lon="-77.8619"),
        location_response(lon=-181),
        {"results": []},
    ],
)
def test_lookup_rejects_unresolved_or_invalid_locations(
    payload: dict[str, object],
) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=payload)

    with pytest.raises(
        ZipLocationNotFoundError,
        match="No U.S. location was found for postcode 16802.",
    ):
        run_lookup(handler)


def test_lookup_rejects_missing_configuration_without_requesting_provider() -> None:
    request_was_made = False

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal request_was_made
        request_was_made = True
        return httpx.Response(200, json=location_response())

    with pytest.raises(GeoapifyConfigurationError, match="not configured"):
        run_lookup(handler, api_key=None)

    assert request_was_made is False


@pytest.mark.parametrize("failure", ["timeout", "http", "invalid_json"])
def test_lookup_sanitizes_provider_failures(failure: str) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if failure == "timeout":
            raise httpx.ReadTimeout(
                f"timeout with credential {FAKE_API_KEY}", request=request
            )
        if failure == "http":
            return httpx.Response(503, json={"message": FAKE_API_KEY})
        return httpx.Response(200, content=b"not-json")

    with pytest.raises(GeoapifyProviderError) as captured_error:
        run_lookup(handler)

    assert str(captured_error.value) == (
        "Geoapify could not complete the location lookup."
    )
    assert FAKE_API_KEY not in str(captured_error.value)


@pytest.mark.parametrize("payload", [None, [], {}, {"results": "invalid"}])
def test_lookup_rejects_malformed_provider_data_without_credentials(
    payload: object,
) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if payload is None:
            return httpx.Response(200, content=b"null")
        return httpx.Response(200, json=payload)

    with pytest.raises(GeoapifyProviderError) as captured_error:
        run_lookup(handler)

    assert str(captured_error.value) == (
        "Geoapify returned an invalid location response."
    )
    assert FAKE_API_KEY not in str(captured_error.value)
