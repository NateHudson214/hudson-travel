from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import date
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException, Query, Response, status
from pydantic import BaseModel

from .database import (
    BookingNotFoundError,
    RelatedRecordNotFoundError,
    cancel_booking_record,
    create_booking_record,
    delete_booking_record,
    initialize_database,
    list_booking_records,
    list_user_records,
    search_trip_records,
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
