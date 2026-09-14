import csv
import sqlite3
from pathlib import Path


SEED_VERSION = "1"

SCHEMA_STATEMENTS = (
    """
    CREATE TABLE IF NOT EXISTS app_metadata (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS hotels (
        hotel_id TEXT PRIMARY KEY,
        hotel_name TEXT NOT NULL,
        city TEXT NOT NULL,
        state TEXT NOT NULL,
        nightly_rate_usd REAL NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS trips (
        trip_id TEXT PRIMARY KEY,
        hotel_id TEXT NOT NULL REFERENCES hotels(hotel_id),
        trip_name TEXT NOT NULL,
        check_in TEXT NOT NULL,
        check_out TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS users (
        user_id TEXT PRIMARY KEY,
        display_name TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS bookings (
        booking_id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL REFERENCES users(user_id),
        trip_id TEXT NOT NULL REFERENCES trips(trip_id),
        booked_on TEXT NOT NULL,
        status TEXT NOT NULL CHECK (status IN ('confirmed', 'cancelled'))
    )
    """,
)

BOOKING_SELECT = """
    SELECT
        b.booking_id,
        b.user_id,
        u.display_name,
        b.trip_id,
        t.trip_name,
        h.hotel_id,
        h.hotel_name,
        h.city,
        h.state,
        h.nightly_rate_usd,
        t.check_in,
        t.check_out,
        b.booked_on,
        b.status
    FROM bookings AS b
    JOIN users AS u ON u.user_id = b.user_id
    JOIN trips AS t ON t.trip_id = b.trip_id
    JOIN hotels AS h ON h.hotel_id = t.hotel_id
"""


class BookingNotFoundError(Exception):
    pass


class RelatedRecordNotFoundError(Exception):
    pass


def connect_database(database_path: Path) -> sqlite3.Connection:
    database_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(database_path, timeout=5)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute("PRAGMA busy_timeout = 5000")
    connection.create_function(
        "CASEFOLD",
        1,
        lambda value: value.casefold() if isinstance(value, str) else value,
        deterministic=True,
    )
    return connection


def read_csv_rows(data_directory: Path, filename: str) -> list[dict[str, str]]:
    with (data_directory / filename).open(
        encoding="utf-8-sig", newline=""
    ) as csv_file:
        return list(csv.DictReader(csv_file))


def initialize_database(database_path: Path, data_directory: Path) -> None:
    connection = connect_database(database_path)
    try:
        connection.execute("BEGIN IMMEDIATE")
        for statement in SCHEMA_STATEMENTS:
            connection.execute(statement)

        seed_marker = connection.execute(
            "SELECT value FROM app_metadata WHERE key = 'csv_seed_version'"
        ).fetchone()
        if seed_marker is not None:
            connection.commit()
            return

        hotels = read_csv_rows(data_directory, "hotels.csv")
        trips = read_csv_rows(data_directory, "trips.csv")
        users = read_csv_rows(data_directory, "users.csv")
        bookings = read_csv_rows(data_directory, "bookings.csv")

        connection.executemany(
            """
            INSERT INTO hotels (
                hotel_id, hotel_name, city, state, nightly_rate_usd
            ) VALUES (?, ?, ?, ?, ?)
            """,
            [
                (
                    hotel["hotel_id"],
                    hotel["hotel_name"],
                    hotel["city"],
                    hotel["state"],
                    float(hotel["nightly_rate_usd"]),
                )
                for hotel in hotels
            ],
        )
        connection.executemany(
            """
            INSERT INTO trips (trip_id, hotel_id, trip_name, check_in, check_out)
            VALUES (?, ?, ?, ?, ?)
            """,
            [
                (
                    trip["trip_id"],
                    trip["hotel_id"],
                    trip["trip_name"],
                    trip["check_in"],
                    trip["check_out"],
                )
                for trip in trips
            ],
        )
        connection.executemany(
            "INSERT INTO users (user_id, display_name) VALUES (?, ?)",
            [(user["user_id"], user["display_name"]) for user in users],
        )
        connection.executemany(
            """
            INSERT INTO bookings (booking_id, user_id, trip_id, booked_on, status)
            VALUES (?, ?, ?, ?, ?)
            """,
            [
                (
                    booking["booking_id"],
                    booking["user_id"],
                    booking["trip_id"],
                    booking["booked_on"],
                    booking["status"],
                )
                for booking in bookings
            ],
        )

        supplied_numbers = [
            int(booking["booking_id"][1:])
            for booking in bookings
            if booking["booking_id"].startswith("B")
            and booking["booking_id"][1:].isdigit()
        ]
        next_booking_number = max(supplied_numbers, default=0) + 1
        connection.executemany(
            "INSERT INTO app_metadata (key, value) VALUES (?, ?)",
            (
                ("next_booking_number", str(next_booking_number)),
                ("csv_seed_version", SEED_VERSION),
            ),
        )
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def search_trip_records(
    database_path: Path, hotel_name: str
) -> list[dict[str, object]]:
    connection = connect_database(database_path)
    try:
        rows = connection.execute(
            """
            SELECT
                t.trip_id,
                t.trip_name,
                h.hotel_id,
                h.hotel_name,
                h.city,
                h.state,
                h.nightly_rate_usd,
                t.check_in,
                t.check_out
            FROM trips AS t
            JOIN hotels AS h ON h.hotel_id = t.hotel_id
            WHERE INSTR(CASEFOLD(h.hotel_name), CASEFOLD(?)) > 0
            ORDER BY t.rowid
            """,
            (hotel_name,),
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        connection.close()


def list_user_records(database_path: Path) -> list[dict[str, object]]:
    connection = connect_database(database_path)
    try:
        rows = connection.execute(
            "SELECT user_id, display_name FROM users ORDER BY rowid"
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        connection.close()


def list_booking_records(database_path: Path) -> list[dict[str, object]]:
    connection = connect_database(database_path)
    try:
        rows = connection.execute(
            BOOKING_SELECT
            + " ORDER BY CAST(SUBSTR(b.booking_id, 2) AS INTEGER), b.booking_id"
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        connection.close()


def get_booking_record(
    connection: sqlite3.Connection, booking_id: str
) -> dict[str, object]:
    row = connection.execute(
        BOOKING_SELECT + " WHERE b.booking_id = ?", (booking_id,)
    ).fetchone()
    if row is None:
        raise BookingNotFoundError(booking_id)
    return dict(row)


def create_booking_record(
    database_path: Path, user_id: str, trip_id: str, booked_on: str
) -> dict[str, object]:
    connection = connect_database(database_path)
    try:
        connection.execute("BEGIN IMMEDIATE")
        if connection.execute(
            "SELECT 1 FROM users WHERE user_id = ?", (user_id,)
        ).fetchone() is None:
            raise RelatedRecordNotFoundError(f"User {user_id} was not found.")
        if connection.execute(
            "SELECT 1 FROM trips WHERE trip_id = ?", (trip_id,)
        ).fetchone() is None:
            raise RelatedRecordNotFoundError(f"Trip {trip_id} was not found.")

        counter_row = connection.execute(
            "SELECT value FROM app_metadata WHERE key = 'next_booking_number'"
        ).fetchone()
        if counter_row is None:
            raise RuntimeError("The booking ID counter is not initialized.")

        next_booking_number = int(counter_row["value"])
        while True:
            booking_id = f"B{next_booking_number:03d}"
            if connection.execute(
                "SELECT 1 FROM bookings WHERE booking_id = ?", (booking_id,)
            ).fetchone() is None:
                break
            next_booking_number += 1

        connection.execute(
            "UPDATE app_metadata SET value = ? WHERE key = 'next_booking_number'",
            (str(next_booking_number + 1),),
        )
        connection.execute(
            """
            INSERT INTO bookings (booking_id, user_id, trip_id, booked_on, status)
            VALUES (?, ?, ?, ?, 'confirmed')
            """,
            (booking_id, user_id, trip_id, booked_on),
        )
        booking = get_booking_record(connection, booking_id)
        connection.commit()
        return booking
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def cancel_booking_record(
    database_path: Path, booking_id: str
) -> dict[str, object]:
    connection = connect_database(database_path)
    try:
        connection.execute("BEGIN IMMEDIATE")
        result = connection.execute(
            "UPDATE bookings SET status = 'cancelled' WHERE booking_id = ?",
            (booking_id,),
        )
        if result.rowcount == 0:
            raise BookingNotFoundError(booking_id)
        booking = get_booking_record(connection, booking_id)
        connection.commit()
        return booking
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def delete_booking_record(database_path: Path, booking_id: str) -> None:
    connection = connect_database(database_path)
    try:
        connection.execute("BEGIN IMMEDIATE")
        result = connection.execute(
            "DELETE FROM bookings WHERE booking_id = ?", (booking_id,)
        )
        if result.rowcount == 0:
            raise BookingNotFoundError(booking_id)
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()
