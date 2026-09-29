import math
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

import httpx

from .config import get_geoapify_api_key


GEOAPIFY_GEOCODING_URL = "https://api.geoapify.com/v1/geocode/search"
GEOAPIFY_TIMEOUT_SECONDS = 5.0


class GeoapifyConfigurationError(Exception):
    """Raised when the backend Geoapify credential is unavailable."""


class ZipLocationNotFoundError(Exception):
    """Raised when Geoapify does not resolve the requested U.S. postcode."""


class GeoapifyProviderError(Exception):
    """Raised when Geoapify cannot provide a usable response."""


@dataclass(frozen=True)
class ZipLocation:
    postcode: str
    country_code: str
    latitude: float
    longitude: float
    locality: str | None = None


def _valid_coordinate(value: Any, minimum: float, maximum: float) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
        and minimum <= value <= maximum
    )


def _locality_from_result(result: dict[str, Any]) -> str | None:
    for field in ("city", "town", "village", "municipality", "suburb", "county"):
        value = result.get(field)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def _parse_location(payload: Any, postcode: str) -> ZipLocation:
    if not isinstance(payload, dict) or not isinstance(payload.get("results"), list):
        raise GeoapifyProviderError("Geoapify returned an invalid location response.")

    for result in payload["results"]:
        if not isinstance(result, dict):
            continue
        if result.get("postcode") != postcode:
            continue
        country_code = result.get("country_code")
        if not isinstance(country_code, str) or country_code.lower() != "us":
            continue

        latitude = result.get("lat")
        longitude = result.get("lon")
        if not _valid_coordinate(latitude, -90, 90):
            continue
        if not _valid_coordinate(longitude, -180, 180):
            continue

        return ZipLocation(
            postcode=postcode,
            country_code="us",
            latitude=float(latitude),
            longitude=float(longitude),
            locality=_locality_from_result(result),
        )

    raise ZipLocationNotFoundError(
        f"No U.S. location was found for postcode {postcode}."
    )


async def lookup_zip_location(
    postcode: str,
    *,
    api_key_provider: Callable[[], str | None] = get_geoapify_api_key,
    client: httpx.AsyncClient | None = None,
) -> ZipLocation:
    """Resolve a U.S. postcode through Geoapify without exposing credentials."""
    api_key = api_key_provider()
    if api_key is None:
        raise GeoapifyConfigurationError("Geoapify is not configured.")

    request_parameters = {
        "postcode": postcode,
        "type": "postcode",
        "filter": "countrycode:us",
        "format": "json",
        "apiKey": api_key,
    }

    owns_client = client is None
    http_client = client or httpx.AsyncClient(timeout=GEOAPIFY_TIMEOUT_SECONDS)
    try:
        try:
            response = await http_client.get(
                GEOAPIFY_GEOCODING_URL,
                params=request_parameters,
                timeout=GEOAPIFY_TIMEOUT_SECONDS,
            )
            response.raise_for_status()
            payload = response.json()
        except (httpx.HTTPError, ValueError):
            raise GeoapifyProviderError(
                "Geoapify could not complete the location lookup."
            ) from None
    finally:
        if owns_client:
            await http_client.aclose()

    return _parse_location(payload, postcode)
