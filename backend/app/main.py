import csv
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel


DATA_DIRECTORY = Path(__file__).resolve().parent.parent / "data"

app = FastAPI(title="Hudson Travel API")


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


def read_csv(filename: str) -> list[dict[str, str]]:
    with (DATA_DIRECTORY / filename).open(
        encoding="utf-8-sig", newline=""
    ) as csv_file:
        return list(csv.DictReader(csv_file))


@app.get("/api/trips", response_model=list[TripSearchResult])
async def search_trips(
    hotel_name: str | None = Query(default=None),
) -> list[TripSearchResult]:
    normalized_hotel_name = hotel_name.strip() if hotel_name is not None else ""
    if not normalized_hotel_name:
        raise HTTPException(status_code=400, detail="Enter a hotel name to search.")

    hotels_by_id = {hotel["hotel_id"]: hotel for hotel in read_csv("hotels.csv")}
    matching_trips: list[TripSearchResult] = []

    for trip in read_csv("trips.csv"):
        hotel = hotels_by_id.get(trip["hotel_id"])
        if (
            hotel is None
            or normalized_hotel_name.casefold() not in hotel["hotel_name"].casefold()
        ):
            continue

        matching_trips.append(
            TripSearchResult(
                trip_id=trip["trip_id"],
                trip_name=trip["trip_name"],
                hotel_id=hotel["hotel_id"],
                hotel_name=hotel["hotel_name"],
                city=hotel["city"],
                state=hotel["state"],
                nightly_rate_usd=float(hotel["nightly_rate_usd"]),
                check_in=trip["check_in"],
                check_out=trip["check_out"],
            )
        )

    return matching_trips
