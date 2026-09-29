import math
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

import httpx

from .config import get_geoapify_api_key
from .geoapify import GeoapifyConfigurationError, GeoapifyProviderError


GEOAPIFY_PLACES_URL = "https://api.geoapify.com/v2/places"
GEOAPIFY_PLACES_CATEGORY = "accommodation.hotel"
GEOAPIFY_PLACES_RADIUS_METERS = 5000
GEOAPIFY_PLACES_RESULT_LIMIT = 20
GEOAPIFY_PLACES_TIMEOUT_SECONDS = 5.0


@dataclass(frozen=True)
class NearbyHotel:
    place_id: str
    name: str | None
    formatted_address: str | None
    latitude: float
    longitude: float
    distance_meters: float | None


def _valid_number(value: Any, minimum: float, maximum: float) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
        and minimum <= value <= maximum
    )


def _optional_text(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    normalized = value.strip()
    return normalized or None


def _optional_distance(value: Any) -> float | None:
    if not _valid_number(value, 0, math.inf):
        return None
    return float(value)


def _parse_hotels(payload: Any) -> list[NearbyHotel]:
    if (
        not isinstance(payload, dict)
        or payload.get("type") != "FeatureCollection"
        or not isinstance(payload.get("features"), list)
    ):
        raise GeoapifyProviderError(
            "Geoapify returned an invalid nearby-hotel response."
        )

    hotels: list[NearbyHotel] = []
    for feature in payload["features"]:
        if not isinstance(feature, dict):
            continue
        properties = feature.get("properties")
        if not isinstance(properties, dict):
            continue

        place_id = _optional_text(properties.get("place_id"))
        latitude = properties.get("lat")
        longitude = properties.get("lon")
        if place_id is None:
            continue
        if not _valid_number(latitude, -90, 90):
            continue
        if not _valid_number(longitude, -180, 180):
            continue

        hotels.append(
            NearbyHotel(
                place_id=place_id,
                name=_optional_text(properties.get("name")),
                formatted_address=_optional_text(properties.get("formatted")),
                latitude=float(latitude),
                longitude=float(longitude),
                distance_meters=_optional_distance(properties.get("distance")),
            )
        )

    return hotels


async def lookup_nearby_hotels(
    latitude: float,
    longitude: float,
    *,
    api_key_provider: Callable[[], str | None] = get_geoapify_api_key,
    client: httpx.AsyncClient | None = None,
) -> list[NearbyHotel]:
    """Return sanitized Geoapify hotel places around a validated point."""
    api_key = api_key_provider()
    if api_key is None:
        raise GeoapifyConfigurationError("Geoapify is not configured.")

    if not _valid_number(latitude, -90, 90) or not _valid_number(
        longitude, -180, 180
    ):
        raise GeoapifyProviderError("The nearby-hotel search center is invalid.")

    circle = f"circle:{longitude},{latitude},{GEOAPIFY_PLACES_RADIUS_METERS}"
    proximity = f"proximity:{longitude},{latitude}"
    request_parameters = {
        "categories": GEOAPIFY_PLACES_CATEGORY,
        "filter": circle,
        "bias": proximity,
        "limit": GEOAPIFY_PLACES_RESULT_LIMIT,
        "apiKey": api_key,
    }

    owns_client = client is None
    http_client = client or httpx.AsyncClient(
        timeout=GEOAPIFY_PLACES_TIMEOUT_SECONDS
    )
    try:
        try:
            response = await http_client.get(
                GEOAPIFY_PLACES_URL,
                params=request_parameters,
                timeout=GEOAPIFY_PLACES_TIMEOUT_SECONDS,
            )
            response.raise_for_status()
            payload = response.json()
        except (httpx.HTTPError, ValueError):
            raise GeoapifyProviderError(
                "Geoapify could not complete the nearby-hotel lookup."
            ) from None
    finally:
        if owns_client:
            await http_client.aclose()

    return _parse_hotels(payload)
