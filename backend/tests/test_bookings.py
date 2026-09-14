import sqlite3
from pathlib import Path

from fastapi.testclient import TestClient

from backend.app.database import connect_database, initialize_database
from backend.app.main import DATA_DIRECTORY


def fetch_ids(database_path: Path, table: str, id_column: str) -> list[str]:
    with sqlite3.connect(database_path) as connection:
        return [
            row[0]
            for row in connection.execute(
                f"SELECT {id_column} FROM {table} ORDER BY rowid"
            ).fetchall()
        ]


def test_seed_preserves_all_records_and_repeated_initialization_is_safe(
    database_path: Path,
) -> None:
    initialize_database(database_path, DATA_DIRECTORY)
    initialize_database(database_path, DATA_DIRECTORY)

    assert fetch_ids(database_path, "hotels", "hotel_id") == [
        "H001",
        "H002",
        "H003",
        "H004",
        "H005",
        "H006",
        "H007",
        "H008",
    ]
    assert fetch_ids(database_path, "trips", "trip_id") == [
        f"T{number:03d}" for number in range(1, 13)
    ]
    assert fetch_ids(database_path, "users", "user_id") == [
        f"U{number:03d}" for number in range(1, 7)
    ]
    assert fetch_ids(database_path, "bookings", "booking_id") == [
        f"B{number:03d}" for number in range(1, 7)
    ]

    connection = connect_database(database_path)
    try:
        metadata = dict(connection.execute("SELECT key, value FROM app_metadata"))
        foreign_keys_enabled = connection.execute("PRAGMA foreign_keys").fetchone()[0]
    finally:
        connection.close()

    assert metadata == {"csv_seed_version": "1", "next_booking_number": "7"}
    assert foreign_keys_enabled == 1


def test_search_reads_persisted_sqlite_records_after_seed(
    client: TestClient, database_path: Path
) -> None:
    first_response = client.get(
        "/api/trips", params={"hotel_name": "Harbor Lantern Hotel"}
    )
    assert [result["trip_id"] for result in first_response.json()] == [
        "T001",
        "T009",
    ]

    connection = connect_database(database_path)
    try:
        connection.execute("DELETE FROM trips WHERE trip_id = 'T009'")
        connection.commit()
    finally:
        connection.close()

    initialize_database(database_path, DATA_DIRECTORY)
    response = client.get(
        "/api/trips", params={"hotel_name": "Harbor Lantern Hotel"}
    )
    assert response.status_code == 200
    assert [result["trip_id"] for result in response.json()] == ["T001"]


def test_create_booking_assigns_id_and_persists_after_reinitialization(
    client: TestClient, database_path: Path
) -> None:
    response = client.post(
        "/api/bookings", json={"user_id": "U006", "trip_id": "T001"}
    )

    assert response.status_code == 201
    assert response.json() == {
        "booking_id": "B007",
        "user_id": "U006",
        "display_name": "Demo Traveler 6",
        "trip_id": "T001",
        "trip_name": "Boston Harbor Weekend",
        "hotel_id": "H001",
        "hotel_name": "Harbor Lantern Hotel",
        "city": "Boston",
        "state": "MA",
        "nightly_rate_usd": 150.0,
        "check_in": "2026-09-18",
        "check_out": "2026-09-20",
        "booked_on": "2026-09-14",
        "status": "confirmed",
    }

    initialize_database(database_path, DATA_DIRECTORY)
    bookings = client.get("/api/bookings").json()
    assert bookings[-1]["booking_id"] == "B007"


def test_deleted_booking_id_is_not_reused(
    client: TestClient, database_path: Path
) -> None:
    first = client.post(
        "/api/bookings", json={"user_id": "U006", "trip_id": "T001"}
    ).json()
    assert client.delete(f"/api/bookings/{first['booking_id']}").status_code == 204

    initialize_database(database_path, DATA_DIRECTORY)
    second = client.post(
        "/api/bookings", json={"user_id": "U006", "trip_id": "T009"}
    )
    assert second.status_code == 201
    assert second.json()["booking_id"] == "B008"


def test_cancellation_retains_booking_and_persists(
    client: TestClient, database_path: Path
) -> None:
    booking_id = client.post(
        "/api/bookings", json={"user_id": "U006", "trip_id": "T001"}
    ).json()["booking_id"]

    response = client.patch(
        f"/api/bookings/{booking_id}", json={"status": "cancelled"}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "cancelled"

    initialize_database(database_path, DATA_DIRECTORY)
    persisted = {
        booking["booking_id"]: booking
        for booking in client.get("/api/bookings").json()
    }
    assert persisted[booking_id]["status"] == "cancelled"


def test_deleting_seed_booking_persists_without_reseeding(
    client: TestClient, database_path: Path
) -> None:
    assert client.delete("/api/bookings/B001").status_code == 204
    initialize_database(database_path, DATA_DIRECTORY)

    booking_ids = [
        booking["booking_id"] for booking in client.get("/api/bookings").json()
    ]
    assert "B001" not in booking_ids
    assert len(booking_ids) == 5


def test_booking_errors_are_clear(client: TestClient) -> None:
    missing_user = client.post(
        "/api/bookings", json={"user_id": "U999", "trip_id": "T001"}
    )
    assert missing_user.status_code == 404
    assert missing_user.json() == {"detail": "User U999 was not found."}

    missing_trip = client.post(
        "/api/bookings", json={"user_id": "U001", "trip_id": "T999"}
    )
    assert missing_trip.status_code == 404
    assert missing_trip.json() == {"detail": "Trip T999 was not found."}

    missing_update = client.patch(
        "/api/bookings/B999", json={"status": "cancelled"}
    )
    assert missing_update.status_code == 404
    assert missing_update.json() == {"detail": "Booking B999 was not found."}

    missing_delete = client.delete("/api/bookings/B999")
    assert missing_delete.status_code == 404
    assert missing_delete.json() == {"detail": "Booking B999 was not found."}


def test_users_and_seed_booking_history_are_joined(client: TestClient) -> None:
    users = client.get("/api/users")
    assert users.status_code == 200
    assert len(users.json()) == 6
    assert users.json()[0] == {
        "user_id": "U001",
        "display_name": "Demo Traveler 1",
    }

    bookings = client.get("/api/bookings")
    assert bookings.status_code == 200
    assert len(bookings.json()) == 6
    assert bookings.json()[0] == {
        "booking_id": "B001",
        "user_id": "U001",
        "display_name": "Demo Traveler 1",
        "trip_id": "T001",
        "trip_name": "Boston Harbor Weekend",
        "hotel_id": "H001",
        "hotel_name": "Harbor Lantern Hotel",
        "city": "Boston",
        "state": "MA",
        "nightly_rate_usd": 150.0,
        "check_in": "2026-09-18",
        "check_out": "2026-09-20",
        "booked_on": "2026-09-01",
        "status": "confirmed",
    }
