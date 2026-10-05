import sqlite3
from pathlib import Path

import pytest

from backend.app.database import connect_database, initialize_database
from backend.app.main import DATA_DIRECTORY


EXPECTED_SEED_COUNTS = {
    "hotels": 8,
    "trips": 12,
    "users": 6,
    "bookings": 6,
}


def table_names(connection: sqlite3.Connection) -> set[str]:
    return {
        row[0]
        for row in connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table'"
        )
    }


def test_fresh_database_adds_local_hotel_schema_without_demo_rows(
    database_path: Path,
) -> None:
    initialize_database(database_path, DATA_DIRECTORY)

    connection = connect_database(database_path)
    try:
        assert {
            "app_metadata",
            "hotels",
            "trips",
            "users",
            "bookings",
            "saved_hotels",
            "saved_hotel_searches",
            "demo_hotel_nights",
        } <= table_names(connection)
        assert {
            table: connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            for table in EXPECTED_SEED_COUNTS
        } == EXPECTED_SEED_COUNTS
        assert connection.execute("SELECT COUNT(*) FROM saved_hotels").fetchone()[
            0
        ] == 0
        assert connection.execute(
            "SELECT COUNT(*) FROM demo_hotel_nights"
        ).fetchone()[0] == 0

        saved_hotel_columns = {
            row["name"]: row for row in connection.execute("PRAGMA table_info(saved_hotels)")
        }
        assert saved_hotel_columns["hotel_id"]["pk"] == 1
        assert saved_hotel_columns["name"]["notnull"] == 0
        assert saved_hotel_columns["address"]["notnull"] == 0
        assert saved_hotel_columns["latitude"]["notnull"] == 1
        assert saved_hotel_columns["longitude"]["notnull"] == 1

        night_columns = {
            row["name"]: row
            for row in connection.execute("PRAGMA table_info(demo_hotel_nights)")
        }
        assert night_columns["hotel_id"]["pk"] == 1
        assert night_columns["stay_date"]["pk"] == 2
        assert night_columns["nightly_rate_cents"]["dflt_value"] == "10000"
        assert night_columns["rooms_available"]["dflt_value"] == "20"

        foreign_key = connection.execute(
            "PRAGMA foreign_key_list(demo_hotel_nights)"
        ).fetchone()
        assert foreign_key["table"] == "saved_hotels"
        assert foreign_key["from"] == "hotel_id"
        assert foreign_key["to"] == "hotel_id"
        assert foreign_key["on_delete"] == "CASCADE"
    finally:
        connection.close()


def test_existing_seeded_database_receives_repeatable_additive_migration(
    database_path: Path,
) -> None:
    initialize_database(database_path, DATA_DIRECTORY)

    connection = connect_database(database_path)
    try:
        expected_ids = {
            "hotels": [
                row[0]
                for row in connection.execute(
                    "SELECT hotel_id FROM hotels ORDER BY rowid"
                )
            ],
            "trips": [
                row[0]
                for row in connection.execute(
                    "SELECT trip_id FROM trips ORDER BY rowid"
                )
            ],
            "users": [
                row[0]
                for row in connection.execute(
                    "SELECT user_id FROM users ORDER BY rowid"
                )
            ],
            "bookings": [
                row[0]
                for row in connection.execute(
                    "SELECT booking_id FROM bookings ORDER BY rowid"
                )
            ],
        }
        connection.execute("DROP TABLE demo_hotel_nights")
        connection.execute("DROP TABLE saved_hotel_searches")
        connection.execute("DROP TABLE saved_hotels")
        connection.commit()
    finally:
        connection.close()

    initialize_database(database_path, DATA_DIRECTORY)
    initialize_database(database_path, DATA_DIRECTORY)

    connection = connect_database(database_path)
    try:
        assert {
            "saved_hotels",
            "saved_hotel_searches",
            "demo_hotel_nights",
        } <= table_names(connection)
        assert {
            "hotels": [
                row[0]
                for row in connection.execute(
                    "SELECT hotel_id FROM hotels ORDER BY rowid"
                )
            ],
            "trips": [
                row[0]
                for row in connection.execute(
                    "SELECT trip_id FROM trips ORDER BY rowid"
                )
            ],
            "users": [
                row[0]
                for row in connection.execute(
                    "SELECT user_id FROM users ORDER BY rowid"
                )
            ],
            "bookings": [
                row[0]
                for row in connection.execute(
                    "SELECT booking_id FROM bookings ORDER BY rowid"
                )
            ],
        } == expected_ids
        assert dict(connection.execute("SELECT key, value FROM app_metadata")) == {
            "csv_seed_version": "1",
            "next_booking_number": "7",
        }
    finally:
        connection.close()


def test_saved_hotel_schema_preserves_provider_identity_and_honest_optional_data(
    database_path: Path,
) -> None:
    initialize_database(database_path, DATA_DIRECTORY)

    connection = connect_database(database_path)
    try:
        connection.execute(
            """
            INSERT INTO saved_hotels (
                hotel_id, name, address, latitude, longitude
            ) VALUES (?, ?, ?, ?, ?)
            """,
            ("provider:hotel-001", None, None, 40.803, -77.861),
        )
        saved_hotel = connection.execute(
            """
            SELECT hotel_id, name, address, latitude, longitude
            FROM saved_hotels
            """
        ).fetchone()
        assert tuple(saved_hotel) == (
            "provider:hotel-001",
            None,
            None,
            40.803,
            -77.861,
        )
        connection.commit()

        with pytest.raises(sqlite3.IntegrityError):
            connection.execute(
                """
                INSERT INTO saved_hotels (
                    hotel_id, name, address, latitude, longitude
                ) VALUES (?, ?, ?, ?, ?)
                """,
                ("provider:hotel-001", "Duplicate", None, 40.0, -77.0),
            )
        connection.rollback()

        with pytest.raises(sqlite3.IntegrityError):
            connection.execute(
                """
                INSERT INTO saved_hotels (
                    hotel_id, name, address, latitude, longitude
                ) VALUES (?, ?, ?, ?, ?)
                """,
                (None, "Missing provider ID", None, 40.0, -77.0),
            )
        connection.rollback()

        for latitude, longitude in (
            (None, -77.0),
            (40.0, None),
            (91.0, -77.0),
            (40.0, -181.0),
        ):
            with pytest.raises(sqlite3.IntegrityError):
                connection.execute(
                    """
                    INSERT INTO saved_hotels (
                        hotel_id, name, address, latitude, longitude
                    ) VALUES (?, ?, ?, ?, ?)
                    """,
                    (f"invalid:{latitude}:{longitude}", None, None, latitude, longitude),
                )
            connection.rollback()
    finally:
        connection.close()


def test_demo_nights_enforce_defaults_keys_constraints_and_foreign_key(
    database_path: Path,
) -> None:
    initialize_database(database_path, DATA_DIRECTORY)

    connection = connect_database(database_path)
    try:
        connection.execute(
            """
            INSERT INTO saved_hotels (
                hotel_id, name, address, latitude, longitude
            ) VALUES ('provider:hotel-001', 'Demo Hotel', NULL, 40.803, -77.861)
            """
        )
        connection.execute(
            """
            INSERT INTO demo_hotel_nights (hotel_id, stay_date)
            VALUES ('provider:hotel-001', '2026-10-10')
            """
        )
        night = connection.execute(
            """
            SELECT hotel_id, stay_date, nightly_rate_cents, rooms_available
            FROM demo_hotel_nights
            """
        ).fetchone()
        assert tuple(night) == (
            "provider:hotel-001",
            "2026-10-10",
            10000,
            20,
        )
        connection.commit()

        with pytest.raises(sqlite3.IntegrityError):
            connection.execute(
                """
                INSERT INTO demo_hotel_nights (hotel_id, stay_date)
                VALUES ('provider:hotel-001', '2026-10-10')
                """
            )
        connection.rollback()

        invalid_rows = (
            ("provider:hotel-001", "10/11/2026", 10000, 20),
            ("provider:hotel-001", "2026-10-11", -1, 20),
            ("provider:hotel-001", "2026-10-11", 10000, -1),
            ("missing-provider", "2026-10-11", 10000, 20),
        )
        for invalid_row in invalid_rows:
            with pytest.raises(sqlite3.IntegrityError):
                connection.execute(
                    """
                    INSERT INTO demo_hotel_nights (
                        hotel_id,
                        stay_date,
                        nightly_rate_cents,
                        rooms_available
                    ) VALUES (?, ?, ?, ?)
                    """,
                    invalid_row,
                )
            connection.rollback()
    finally:
        connection.close()


def test_deleting_saved_hotel_cascades_only_its_demo_nights(
    database_path: Path,
) -> None:
    initialize_database(database_path, DATA_DIRECTORY)

    connection = connect_database(database_path)
    try:
        connection.executemany(
            """
            INSERT INTO saved_hotels (
                hotel_id, name, address, latitude, longitude
            ) VALUES (?, ?, NULL, 40.803, -77.861)
            """,
            (("provider:hotel-001", "First"), ("provider:hotel-002", "Second")),
        )
        connection.executemany(
            """
            INSERT INTO demo_hotel_nights (hotel_id, stay_date)
            VALUES (?, '2026-10-10')
            """,
            (("provider:hotel-001",), ("provider:hotel-002",)),
        )
        connection.execute(
            "DELETE FROM saved_hotels WHERE hotel_id = 'provider:hotel-001'"
        )

        assert [
            row[0]
            for row in connection.execute(
                "SELECT hotel_id FROM saved_hotels ORDER BY hotel_id"
            )
        ] == ["provider:hotel-002"]
        assert [
            row[0]
            for row in connection.execute(
                "SELECT hotel_id FROM demo_hotel_nights ORDER BY hotel_id"
            )
        ] == ["provider:hotel-002"]
    finally:
        connection.close()
