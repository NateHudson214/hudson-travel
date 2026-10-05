from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import date
from pathlib import Path
import sqlite3
from typing import Literal

from fastapi import FastAPI, HTTPException, Query, Response, status
from pydantic import BaseModel, Field, FiniteFloat, field_validator

from .config import get_geoapify_api_key
from .database import (
    BookingNotFoundError,
    RelatedRecordNotFoundError,
    SavedHotelNotFoundError,
    cancel_booking_record,
    create_booking_record,
    delete_booking_record,
    delete_local_hotel_record,
    initialize_database,
    list_booking_records,
    list_saved_hotel_ids,
    list_saved_hotels_for_zip,
    list_user_records,
    save_local_hotel_record,
    search_trip_records,
)
from .geoapify import (
    GeoapifyConfigurationError,
    GeoapifyProviderError,
    ZipLocationNotFoundError,
    lookup_zip_location,
)
from .places import (
    GEOAPIFY_PLACES_RADIUS_METERS,
    GEOAPIFY_PLACES_RESULT_LIMIT,
    NearbyHotel,
    lookup_nearby_hotels,
)


BACKEND_DIRECTORY = Path(__file__).resolve().parent.parent
DATA_DIRECTORY = BACKEND_DIRECTORY / "data"
DEFAULT_DATABASE_PATH = BACKEND_DIRECTORY / "instance" / "hudson_travel.sqlite3"


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncIterator[None]:
    initialize_database(Path(application.state.database_path), DATA_DIRECTORY)
    yield


app = FastAPI(title="Hudson Travel API", lifespan=lifespan)
app.state.database_path = DEFAULT_DATABASE_PATH
app.state.today_provider = date.today
app.state.geoapify_key_provider = get_geoapify_api_key
app.state.zip_location_lookup = lookup_zip_location
app.state.nearby_hotels_lookup = lookup_nearby_hotels


class HealthResult(BaseModel):
    status: Literal["ok"]
    geoapify: Literal["key is configured", "key is not configured"]


class ZipLocationResult(BaseModel):
    postcode: str
    country_code: str
    latitude: float
    longitude: float
    locality: str | None = None


class NearbyHotelResult(BaseModel):
    place_id: str
    name: str | None
    formatted_address: str | None
    latitude: float
    longitude: float
    distance_meters: float | None


class NearbyHotelSearchResult(BaseModel):
    location: ZipLocationResult
    radius_meters: int
    result_limit: int
    hotels: list[NearbyHotelResult]


class DemoHotelNightResult(BaseModel):
    stay_date: str
    nightly_rate_cents: int
    rooms_available: int


class SavedHotelResult(NearbyHotelResult):
    nights: list[DemoHotelNightResult]


class SavedHotelSearchResult(BaseModel):
    searched_zip_code: str
    location: ZipLocationResult | None
    hotels: list[SavedHotelResult]


class SavedHotelIdsResult(BaseModel):
    place_ids: list[str]


class ProviderHotelCreate(BaseModel):
    place_id: str = Field(min_length=1)
    name: str | None = None
    formatted_address: str | None = None
    latitude: FiniteFloat = Field(ge=-90, le=90)
    longitude: FiniteFloat = Field(ge=-180, le=180)

    @field_validator("place_id")
    @classmethod
    def reject_blank_place_id(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("place_id must not be blank")
        return value


class SavedHotelCreate(BaseModel):
    zip_code: str
    location: ZipLocationResult
    hotel: ProviderHotelCreate


class SavedHotelCreateResult(BaseModel):
    searched_zip_code: str
    location: ZipLocationResult
    hotel: SavedHotelResult


class TripSearchResult(BaseModel):
    trip_id: str
    trip_name: str
    hotel_id: str
    hotel_name: str
    city: str
    state: str
    nightly_rate_usd: float
    check_in: str
    check_out: str


class UserResult(BaseModel):
    user_id: str
    display_name: str


class BookingResult(BaseModel):
    booking_id: str
    user_id: str
    display_name: str
    trip_id: str
    trip_name: str
    hotel_id: str
    hotel_name: str
    city: str
    state: str
    nightly_rate_usd: float
    check_in: str
    check_out: str
    booked_on: str
    status: Literal["confirmed", "cancelled"]


class BookingCreate(BaseModel):
    user_id: str
    trip_id: str


class BookingStatusUpdate(BaseModel):
    status: Literal["cancelled"]


def prepare_database() -> Path:
    return Path(app.state.database_path)


def booking_not_found(booking_id: str) -> HTTPException:
    return HTTPException(
        status_code=404, detail=f"Booking {booking_id} was not found."
    )


def local_hotel_storage_error() -> HTTPException:
    return HTTPException(
        status_code=500,
        detail="Local hotel storage is temporarily unavailable.",
    )


@app.get("/api/health", response_model=HealthResult)
async def health_check() -> HealthResult:
    key_status = (
        "key is configured"
        if app.state.geoapify_key_provider() is not None
        else "key is not configured"
    )
    return HealthResult(status="ok", geoapify=key_status)


async def resolve_zip_location(postcode: str) -> ZipLocationResult:
    try:
        location = await app.state.zip_location_lookup(postcode)
    except GeoapifyConfigurationError as error:
        raise HTTPException(
            status_code=503, detail="Geoapify is not configured."
        ) from error
    except ZipLocationNotFoundError as error:
        raise HTTPException(
            status_code=404, detail=f"ZIP {postcode} could not be resolved."
        ) from error
    except GeoapifyProviderError as error:
        raise HTTPException(
            status_code=502,
            detail="The location service is temporarily unavailable.",
        ) from error

    return ZipLocationResult(
        postcode=location.postcode,
        country_code=location.country_code,
        latitude=location.latitude,
        longitude=location.longitude,
        locality=location.locality,
    )


def normalize_zip_code(zip_code: str | None) -> str:
    normalized_zip_code = zip_code.strip() if zip_code is not None else ""
    if len(normalized_zip_code) != 5 or not all(
        "0" <= character <= "9" for character in normalized_zip_code
    ):
        raise HTTPException(
            status_code=400,
            detail="Enter a five-digit U.S. ZIP code.",
        )
    return normalized_zip_code


@app.get("/api/demo/zip-location", response_model=ZipLocationResult)
async def demo_zip_location() -> ZipLocationResult:
    return await resolve_zip_location("16802")


@app.get("/api/zip-location", response_model=ZipLocationResult)
async def zip_location(
    zip_code: str | None = Query(default=None),
) -> ZipLocationResult:
    return await resolve_zip_location(normalize_zip_code(zip_code))


@app.get("/api/hotels/nearby", response_model=NearbyHotelSearchResult)
async def nearby_hotels(
    zip_code: str | None = Query(default=None),
) -> NearbyHotelSearchResult:
    normalized_zip_code = normalize_zip_code(zip_code)
    location = await resolve_zip_location(normalized_zip_code)

    try:
        hotels: list[NearbyHotel] = await app.state.nearby_hotels_lookup(
            location.latitude, location.longitude
        )
    except GeoapifyConfigurationError as error:
        raise HTTPException(
            status_code=503, detail="Geoapify is not configured."
        ) from error
    except GeoapifyProviderError as error:
        raise HTTPException(
            status_code=502,
            detail="The nearby hotel service is temporarily unavailable.",
        ) from error

    return NearbyHotelSearchResult(
        location=location,
        radius_meters=GEOAPIFY_PLACES_RADIUS_METERS,
        result_limit=GEOAPIFY_PLACES_RESULT_LIMIT,
        hotels=[NearbyHotelResult(**hotel.__dict__) for hotel in hotels],
    )


@app.get("/api/saved-hotels/ids", response_model=SavedHotelIdsResult)
async def saved_hotel_ids() -> SavedHotelIdsResult:
    try:
        place_ids = list_saved_hotel_ids(prepare_database())
    except sqlite3.Error as error:
        raise local_hotel_storage_error() from error
    return SavedHotelIdsResult(place_ids=place_ids)


@app.get("/api/saved-hotels", response_model=SavedHotelSearchResult)
async def saved_hotels(
    zip_code: str | None = Query(default=None),
) -> SavedHotelSearchResult:
    normalized_zip_code = normalize_zip_code(zip_code)
    try:
        record = list_saved_hotels_for_zip(
            prepare_database(), normalized_zip_code
        )
    except sqlite3.Error as error:
        raise local_hotel_storage_error() from error
    return SavedHotelSearchResult(**record)


@app.post(
    "/api/saved-hotels",
    response_model=SavedHotelCreateResult,
    status_code=status.HTTP_201_CREATED,
)
async def save_hotel(payload: SavedHotelCreate) -> SavedHotelCreateResult:
    normalized_zip_code = normalize_zip_code(payload.zip_code)
    normalized_postcode = normalize_zip_code(payload.location.postcode)
    if payload.location.country_code.casefold() != "us":
        raise HTTPException(
            status_code=400,
            detail="Saved hotel location must be a U.S. ZIP code.",
        )
    try:
        record = save_local_hotel_record(
            prepare_database(),
            place_id=payload.hotel.place_id,
            name=payload.hotel.name,
            formatted_address=payload.hotel.formatted_address,
            latitude=payload.hotel.latitude,
            longitude=payload.hotel.longitude,
            zip_code=normalized_zip_code,
            postcode=normalized_postcode,
            country_code=payload.location.country_code,
            search_latitude=payload.location.latitude,
            search_longitude=payload.location.longitude,
            locality=payload.location.locality,
        )
    except sqlite3.Error as error:
        raise local_hotel_storage_error() from error
    return SavedHotelCreateResult(**record)


@app.delete(
    "/api/saved-hotels/{hotel_id:path}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_saved_hotel(hotel_id: str) -> Response:
    try:
        delete_local_hotel_record(prepare_database(), hotel_id)
    except SavedHotelNotFoundError as error:
        raise HTTPException(
            status_code=404,
            detail="Saved hotel was not found.",
        ) from error
    except sqlite3.Error as error:
        raise local_hotel_storage_error() from error
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.get("/api/trips", response_model=list[TripSearchResult])
async def search_trips(
    hotel_name: str | None = Query(default=None),
) -> list[TripSearchResult]:
    normalized_hotel_name = hotel_name.strip() if hotel_name is not None else ""
    if not normalized_hotel_name:
        raise HTTPException(status_code=400, detail="Enter a hotel name to search.")

    return [
        TripSearchResult(**record)
        for record in search_trip_records(prepare_database(), normalized_hotel_name)
    ]


@app.get("/api/users", response_model=list[UserResult])
async def list_users() -> list[UserResult]:
    return [UserResult(**record) for record in list_user_records(prepare_database())]


@app.get("/api/bookings", response_model=list[BookingResult])
async def list_bookings() -> list[BookingResult]:
    return [
        BookingResult(**record)
        for record in list_booking_records(prepare_database())
    ]


@app.post(
    "/api/bookings",
    response_model=BookingResult,
    status_code=status.HTTP_201_CREATED,
)
async def create_booking(booking: BookingCreate) -> BookingResult:
    database_path = prepare_database()
    try:
        record = create_booking_record(
            database_path,
            booking.user_id,
            booking.trip_id,
            app.state.today_provider().isoformat(),
        )
    except RelatedRecordNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    return BookingResult(**record)


@app.patch("/api/bookings/{booking_id}", response_model=BookingResult)
async def cancel_booking(
    booking_id: str, booking: BookingStatusUpdate
) -> BookingResult:
    database_path = prepare_database()
    try:
        record = cancel_booking_record(database_path, booking_id)
    except BookingNotFoundError as error:
        raise booking_not_found(booking_id) from error
    return BookingResult(**record)


@app.delete(
    "/api/bookings/{booking_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_booking(booking_id: str) -> Response:
    database_path = prepare_database()
    try:
        delete_booking_record(database_path, booking_id)
    except BookingNotFoundError as error:
        raise booking_not_found(booking_id) from error
    return Response(status_code=status.HTTP_204_NO_CONTENT)
