import csv
import sqlite3
from datetime import date, timedelta
from pathlib import Path


SEED_VERSION = "1"
DEMO_STAY_START = date(2026, 10, 10)
DEMO_STAY_DATES = tuple(
    (DEMO_STAY_START + timedelta(days=offset)).isoformat() for offset in range(5)
)

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
    """
    CREATE TABLE IF NOT EXISTS saved_hotels (
        hotel_id TEXT PRIMARY KEY NOT NULL CHECK (LENGTH(hotel_id) > 0),
        name TEXT,
        address TEXT,
        latitude REAL NOT NULL CHECK (
            TYPEOF(latitude) IN ('integer', 'real')
            AND latitude BETWEEN -90.0 AND 90.0
        ),
        longitude REAL NOT NULL CHECK (
            TYPEOF(longitude) IN ('integer', 'real')
            AND longitude BETWEEN -180.0 AND 180.0
        )
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS saved_hotel_searches (
        hotel_id TEXT NOT NULL
            REFERENCES saved_hotels(hotel_id) ON DELETE CASCADE,
        zip_code TEXT NOT NULL CHECK (
            LENGTH(zip_code) = 5
            AND zip_code NOT GLOB '*[^0-9]*'
        ),
        postcode TEXT NOT NULL CHECK (
            LENGTH(postcode) = 5
            AND postcode NOT GLOB '*[^0-9]*'
        ),
        country_code TEXT NOT NULL,
        latitude REAL NOT NULL CHECK (
            TYPEOF(latitude) IN ('integer', 'real')
            AND latitude BETWEEN -90.0 AND 90.0
        ),
        longitude REAL NOT NULL CHECK (
            TYPEOF(longitude) IN ('integer', 'real')
            AND longitude BETWEEN -180.0 AND 180.0
        ),
        locality TEXT,
        PRIMARY KEY (hotel_id, zip_code)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS demo_hotel_nights (
        hotel_id TEXT NOT NULL
            REFERENCES saved_hotels(hotel_id) ON DELETE CASCADE,
        stay_date TEXT NOT NULL CHECK (
            LENGTH(stay_date) = 10
            AND stay_date GLOB
                '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]'
        ),
        nightly_rate_cents INTEGER NOT NULL DEFAULT 10000 CHECK (
            TYPEOF(nightly_rate_cents) = 'integer'
            AND nightly_rate_cents >= 0
        ),
        rooms_available INTEGER NOT NULL DEFAULT 20 CHECK (
            TYPEOF(rooms_available) = 'integer'
            AND rooms_available >= 0
        ),
        PRIMARY KEY (hotel_id, stay_date)
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


class SavedHotelNotFoundError(Exception):
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


def _saved_hotel_from_row(
    connection: sqlite3.Connection, row: sqlite3.Row
) -> dict[str, object]:
    nights = connection.execute(
        """
        SELECT stay_date, nightly_rate_cents, rooms_available
        FROM demo_hotel_nights
        WHERE hotel_id = ?
        ORDER BY stay_date
        """,
        (row["hotel_id"],),
    ).fetchall()
    return {
        "place_id": row["hotel_id"],
        "name": row["name"],
        "formatted_address": row["address"],
        "latitude": row["hotel_latitude"],
        "longitude": row["hotel_longitude"],
        "distance_meters": None,
        "nights": [dict(night) for night in nights],
    }


def save_local_hotel_record(
    database_path: Path,
    *,
    place_id: str,
    name: str | None,
    formatted_address: str | None,
    latitude: float,
    longitude: float,
    zip_code: str,
    postcode: str,
    country_code: str,
    search_latitude: float,
    search_longitude: float,
    locality: str | None,
) -> dict[str, object]:
    connection = connect_database(database_path)
    try:
        connection.execute("BEGIN IMMEDIATE")
        connection.execute(
            """
            INSERT OR IGNORE INTO saved_hotels (
                hotel_id, name, address, latitude, longitude
            ) VALUES (?, ?, ?, ?, ?)
            """,
            (place_id, name, formatted_address, latitude, longitude),
        )
        connection.execute(
            """
            INSERT OR IGNORE INTO saved_hotel_searches (
                hotel_id,
                zip_code,
                postcode,
                country_code,
                latitude,
                longitude,
                locality
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                place_id,
                zip_code,
                postcode,
                country_code,
                search_latitude,
                search_longitude,
                locality,
            ),
        )
        connection.executemany(
            """
            INSERT OR IGNORE INTO demo_hotel_nights (hotel_id, stay_date)
            VALUES (?, ?)
            """,
            [(place_id, stay_date) for stay_date in DEMO_STAY_DATES],
        )
        row = connection.execute(
            """
            SELECT
                h.hotel_id,
                h.name,
                h.address,
                h.latitude AS hotel_latitude,
                h.longitude AS hotel_longitude,
                s.zip_code,
                s.postcode,
                s.country_code,
                s.latitude AS search_latitude,
                s.longitude AS search_longitude,
                s.locality
            FROM saved_hotels AS h
            JOIN saved_hotel_searches AS s ON s.hotel_id = h.hotel_id
            WHERE h.hotel_id = ? AND s.zip_code = ?
            """,
            (place_id, zip_code),
        ).fetchone()
        if row is None:
            raise RuntimeError("The saved hotel could not be read after saving.")
        hotel = _saved_hotel_from_row(connection, row)
        connection.commit()
        return {
            "searched_zip_code": row["zip_code"],
            "location": {
                "postcode": row["postcode"],
                "country_code": row["country_code"],
                "latitude": row["search_latitude"],
                "longitude": row["search_longitude"],
                "locality": row["locality"],
            },
            "hotel": hotel,
        }
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def list_saved_hotel_ids(database_path: Path) -> list[str]:
    connection = connect_database(database_path)
    try:
        return [
            row["hotel_id"]
            for row in connection.execute(
                "SELECT hotel_id FROM saved_hotels ORDER BY hotel_id"
            )
        ]
    finally:
        connection.close()


def list_saved_hotels_for_zip(
    database_path: Path, zip_code: str
) -> dict[str, object]:
    connection = connect_database(database_path)
    try:
        rows = connection.execute(
            """
            SELECT
                h.hotel_id,
                h.name,
                h.address,
                h.latitude AS hotel_latitude,
                h.longitude AS hotel_longitude,
                s.zip_code,
                s.postcode,
                s.country_code,
                s.latitude AS search_latitude,
                s.longitude AS search_longitude,
                s.locality
            FROM saved_hotel_searches AS s
            JOIN saved_hotels AS h ON h.hotel_id = s.hotel_id
            WHERE s.zip_code = ?
            ORDER BY h.name IS NULL, CASEFOLD(h.name), h.hotel_id
            """,
            (zip_code,),
        ).fetchall()
        if not rows:
            return {
                "searched_zip_code": zip_code,
                "location": None,
                "hotels": [],
            }

        first = rows[0]
        return {
            "searched_zip_code": zip_code,
            "location": {
                "postcode": first["postcode"],
                "country_code": first["country_code"],
                "latitude": first["search_latitude"],
                "longitude": first["search_longitude"],
                "locality": first["locality"],
            },
            "hotels": [
                _saved_hotel_from_row(connection, row) for row in rows
            ],
        }
    finally:
        connection.close()


def delete_local_hotel_record(database_path: Path, hotel_id: str) -> None:
    connection = connect_database(database_path)
    try:
        connection.execute("BEGIN IMMEDIATE")
        result = connection.execute(
            "DELETE FROM saved_hotels WHERE hotel_id = ?", (hotel_id,)
        )
        if result.rowcount == 0:
            raise SavedHotelNotFoundError(hotel_id)
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()
