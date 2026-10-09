import sqlite3
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest

from backend.app import advisor_query as advisor_query_module
from backend.app.advisor_query import (
    MAX_SQL_CHARACTERS,
    AdvisorQueryExecutionError,
    AdvisorQueryLimitError,
    AdvisorQueryRejectedError,
    AdvisorQueryResultError,
    execute_read_only_query,
    validate_query_proposal,
)
from backend.app.advisor_contracts import QueryProposal


VALID_MULTI_NIGHT_SQL = """
SELECT
    h.hotel_id,
    h.name,
    COUNT(n.stay_date) AS requested_nights,
    MIN(n.rooms_available) AS minimum_rooms,
    SUM(n.nightly_rate_cents) AS total_cents
FROM saved_hotels AS h
JOIN demo_hotel_nights AS n ON n.hotel_id = h.hotel_id
WHERE n.stay_date >= :check_in
  AND n.stay_date < :check_out
GROUP BY h.hotel_id, h.name
HAVING COUNT(n.stay_date) = :night_count
   AND MIN(n.rooms_available) > :minimum_rooms
ORDER BY total_cents
LIMIT :limit
"""


def proposal(
    sql: str = VALID_MULTI_NIGHT_SQL,
    parameters: dict[str, Any] | None = None,
) -> QueryProposal:
    return QueryProposal(
        sql=sql,
        parameters=parameters
        or {
            "check_in": "2026-10-10",
            "check_out": "2026-10-12",
            "night_count": 2,
            "minimum_rooms": 0,
            "limit": 50,
        },
    )


def snapshot_database(database_path: Path) -> dict[str, list[tuple[Any, ...]]]:
    connection = sqlite3.connect(database_path)
    try:
        return {
            "saved_hotels": list(
                connection.execute(
                    "SELECT * FROM saved_hotels ORDER BY hotel_id"
                )
            ),
            "saved_hotel_searches": list(
                connection.execute(
                    "SELECT * FROM saved_hotel_searches ORDER BY hotel_id, zip_code"
                )
            ),
            "demo_hotel_nights": list(
                connection.execute(
                    "SELECT * FROM demo_hotel_nights ORDER BY hotel_id, stay_date"
                )
            ),
            "private_records": list(
                connection.execute("SELECT * FROM private_records ORDER BY secret")
            ),
        }
    finally:
        connection.close()


@pytest.fixture
def advisor_database(tmp_path: Path) -> Iterator[Path]:
    database_path = tmp_path / "advisor.sqlite3"
    connection = sqlite3.connect(database_path)
    try:
        connection.executescript(
            """
            PRAGMA foreign_keys = ON;
            CREATE TABLE saved_hotels (
                hotel_id TEXT PRIMARY KEY,
                name TEXT,
                address TEXT,
                latitude REAL NOT NULL,
                longitude REAL NOT NULL
            );
            CREATE TABLE saved_hotel_searches (
                hotel_id TEXT NOT NULL,
                zip_code TEXT NOT NULL,
                postcode TEXT NOT NULL,
                country_code TEXT NOT NULL,
                latitude REAL NOT NULL,
                longitude REAL NOT NULL,
                locality TEXT,
                PRIMARY KEY (hotel_id, zip_code)
            );
            CREATE TABLE demo_hotel_nights (
                hotel_id TEXT NOT NULL,
                stay_date TEXT NOT NULL,
                nightly_rate_cents INTEGER NOT NULL,
                rooms_available INTEGER NOT NULL,
                PRIMARY KEY (hotel_id, stay_date)
            );
            CREATE TABLE private_records (secret TEXT NOT NULL);
            """
        )
        connection.executemany(
            """
            INSERT INTO saved_hotels (
                hotel_id, name, address, latitude, longitude
            ) VALUES (?, ?, ?, ?, ?)
            """,
            [
                (
                    "provider-hotel-1",
                    "Hotel State College",
                    None,
                    40.803,
                    -77.861,
                ),
                (
                    "provider-hotel-2",
                    "Other Hotel",
                    "2 Example Road",
                    40.804,
                    -77.862,
                ),
                *[
                    (
                        f"provider-extra-{number:02d}",
                        f"Extra Hotel {number:02d}",
                        None,
                        40.7 + number / 1000,
                        -77.8,
                    )
                    for number in range(10)
                ],
            ],
        )
        connection.executemany(
            """
            INSERT INTO saved_hotel_searches (
                hotel_id, zip_code, postcode, country_code,
                latitude, longitude, locality
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    "provider-hotel-1",
                    "16802",
                    "16802",
                    "us",
                    40.803,
                    -77.861,
                    "State College",
                ),
                (
                    "provider-hotel-1",
                    "02113",
                    "02113",
                    "us",
                    42.365,
                    -71.055,
                    "Boston",
                ),
                (
                    "provider-hotel-2",
                    "16802",
                    "16802",
                    "us",
                    40.803,
                    -77.861,
                    "State College",
                ),
            ],
        )
        connection.executemany(
            """
            INSERT INTO demo_hotel_nights (
                hotel_id, stay_date, nightly_rate_cents, rooms_available
            ) VALUES (?, ?, ?, ?)
            """,
            [
                ("provider-hotel-1", "2026-10-10", 10000, 20),
                ("provider-hotel-1", "2026-10-11", 10000, 20),
                ("provider-hotel-1", "2026-10-12", 12550, 7),
                ("provider-hotel-1", "2026-10-13", 10000, 20),
                ("provider-hotel-1", "2026-10-14", 10000, 20),
                ("provider-hotel-2", "2026-10-10", 9000, 0),
                ("provider-hotel-2", "2026-10-11", 9000, 0),
            ],
        )
        connection.execute("INSERT INTO private_records VALUES ('private')")
        connection.commit()
    finally:
        connection.close()

    expected_snapshot = snapshot_database(database_path)
    yield database_path
    assert snapshot_database(database_path) == expected_snapshot


def test_multi_night_query_uses_inclusive_check_in_exclusive_check_out(
    advisor_database: Path,
) -> None:
    records = execute_read_only_query(advisor_database, proposal())

    assert records == [
        {
            "hotel_id": "provider-hotel-1",
            "name": "Hotel State College",
            "requested_nights": 2,
            "minimum_rooms": 20,
            "total_cents": 20000,
        }
    ]


def test_query_can_include_checkout_night_only_when_requested(
    advisor_database: Path,
) -> None:
    records = execute_read_only_query(
        advisor_database,
        proposal(
            parameters={
                "check_in": "2026-10-10",
                "check_out": "2026-10-13",
                "night_count": 3,
                "minimum_rooms": 0,
                "limit": 50,
            }
        ),
    )

    assert records[0]["requested_nights"] == 3
    assert records[0]["minimum_rooms"] == 7
    assert records[0]["total_cents"] == 32550


def test_valid_empty_query_returns_empty_records(advisor_database: Path) -> None:
    records = execute_read_only_query(
        advisor_database,
        proposal(
            parameters={
                "check_in": "2027-01-01",
                "check_out": "2027-01-03",
                "night_count": 2,
                "minimum_rooms": 0,
                "limit": 50,
            }
        ),
    )

    assert records == []


def test_all_approved_tables_columns_leading_zero_and_null_are_preserved(
    advisor_database: Path,
) -> None:
    sql = """
    SELECT
        h.hotel_id, h.name, h.address,
        h.latitude AS hotel_latitude, h.longitude AS hotel_longitude,
        s.zip_code, s.postcode, s.country_code,
        s.latitude AS search_latitude, s.longitude AS search_longitude,
        s.locality, n.stay_date, n.nightly_rate_cents, n.rooms_available
    FROM saved_hotels AS h
    JOIN saved_hotel_searches AS s ON s.hotel_id = h.hotel_id
    JOIN demo_hotel_nights AS n ON n.hotel_id = h.hotel_id
    WHERE s.zip_code = :zip_code AND n.stay_date = :stay_date
    LIMIT :limit
    """

    records = execute_read_only_query(
        advisor_database,
        proposal(
            sql,
            {
                "zip_code": "02113",
                "stay_date": "2026-10-12",
                "limit": 10,
            },
        ),
    )

    assert records == [
        {
            "hotel_id": "provider-hotel-1",
            "name": "Hotel State College",
            "address": None,
            "hotel_latitude": 40.803,
            "hotel_longitude": -77.861,
            "zip_code": "02113",
            "postcode": "02113",
            "country_code": "us",
            "search_latitude": 42.365,
            "search_longitude": -71.055,
            "locality": "Boston",
            "stay_date": "2026-10-12",
            "nightly_rate_cents": 12550,
            "rooms_available": 7,
        }
    ]


def test_parameter_values_are_bound_and_not_interpolated(
    advisor_database: Path,
) -> None:
    sql = """
    SELECT h.hotel_id
    FROM saved_hotels AS h
    JOIN saved_hotel_searches AS s ON s.hotel_id = h.hotel_id
    WHERE s.zip_code = :zip_code
    LIMIT :limit
    """
    records = execute_read_only_query(
        advisor_database,
        proposal(
            sql,
            {"zip_code": "16802' OR 1=1 --", "limit": 50},
        ),
    )

    assert records == []


def test_non_recursive_cte_is_permitted(advisor_database: Path) -> None:
    sql = """
    WITH selected_hotel AS (
        SELECT hotel_id, name
        FROM saved_hotels
        WHERE hotel_id = :hotel_id
    )
    SELECT hotel_id, name FROM selected_hotel LIMIT :limit
    """

    assert execute_read_only_query(
        advisor_database,
        proposal(sql, {"hotel_id": "provider-hotel-1", "limit": 10}),
    ) == [
        {"hotel_id": "provider-hotel-1", "name": "Hotel State College"}
    ]


@pytest.mark.parametrize(
    ("sql", "parameters"),
    [
        ("DELETE FROM saved_hotels WHERE hotel_id = :hotel_id", {"hotel_id": "x"}),
        ("DROP TABLE saved_hotels", {}),
        ("PRAGMA table_info(saved_hotels)", {}),
        ("ATTACH DATABASE :path AS private", {"path": "private.sqlite3"}),
        ("BEGIN TRANSACTION", {}),
        (
            "SELECT hotel_id FROM saved_hotels WHERE hotel_id = :id -- hidden\nLIMIT :limit",
            {"id": "x", "limit": 10},
        ),
        (
            "SELECT hotel_id FROM saved_hotels WHERE hotel_id = :id; DELETE FROM saved_hotels",
            {"id": "x"},
        ),
        (
            "WITH RECURSIVE x AS (SELECT 1) SELECT hotel_id FROM saved_hotels WHERE hotel_id = :id LIMIT :limit",
            {"id": "x", "limit": 10},
        ),
        (
            "SELECT hotel_id FROM saved_hotels WHERE hotel_id = :id UNION SELECT hotel_id FROM saved_hotels LIMIT :limit",
            {"id": "x", "limit": 10},
        ),
        (
            "SELECT secret FROM private_records WHERE secret = :secret LIMIT :limit",
            {"secret": "private", "limit": 10},
        ),
        (
            "SELECT h.hotel_id FROM saved_hotels h JOIN saved_hotel_searches s ON s.hotel_id=h.hotel_id JOIN demo_hotel_nights n ON n.hotel_id=h.hotel_id JOIN saved_hotels h2 ON h2.hotel_id=h.hotel_id WHERE h.hotel_id=:id LIMIT :limit",
            {"id": "x", "limit": 10},
        ),
        (
            "SELECT a.hotel_id FROM saved_hotels a JOIN saved_hotels b ON b.hotel_id=a.hotel_id WHERE a.hotel_id=:id LIMIT :limit",
            {"id": "x", "limit": 10},
        ),
        (
            "SELECT hotel_id FROM saved_hotels WHERE hotel_id = :id",
            {"id": "x"},
        ),
        (
            "SELECT hotel_id FROM saved_hotels WHERE hotel_id = :id LIMIT 51",
            {"id": "x"},
        ),
        (
            "SELECT hotel_id FROM saved_hotels WHERE hotel_id = ? LIMIT 10",
            {},
        ),
        (
            "SELECT hotel_id FROM saved_hotels WHERE hotel_id = :id LIMIT :limit",
            {"wrong": "x", "limit": 10},
        ),
        (
            "SELECT hotel_id FROM sqlite_master WHERE name = :name LIMIT :limit",
            {"name": "saved_hotels", "limit": 10},
        ),
    ],
)
def test_unsafe_query_shapes_are_rejected_before_execution(
    advisor_database: Path,
    sql: str,
    parameters: dict[str, Any],
) -> None:
    with pytest.raises(AdvisorQueryRejectedError):
        execute_read_only_query(
            advisor_database, QueryProposal(sql=sql, parameters=parameters)
        )


@pytest.mark.parametrize(
    "parameters",
    [
        {"id": True, "limit": 10},
        {"id": ["x"], "limit": 10},
        {"id": {"value": "x"}, "limit": 10},
        {"id": float("nan"), "limit": 10},
        {"id": float("inf"), "limit": 10},
        {"id": "x" * 501, "limit": 10},
    ],
)
def test_invalid_parameter_values_are_rejected(
    advisor_database: Path, parameters: dict[str, Any]
) -> None:
    sql = """
    SELECT hotel_id FROM saved_hotels
    WHERE hotel_id = :id
    LIMIT :limit
    """
    with pytest.raises(AdvisorQueryRejectedError):
        execute_read_only_query(
            advisor_database, QueryProposal(sql=sql, parameters=parameters)
        )


def test_oversized_sql_parameter_names_and_parameter_count_are_rejected(
    advisor_database: Path,
) -> None:
    oversized_sql = (
        "SELECT hotel_id FROM saved_hotels WHERE hotel_id = :id LIMIT :limit "
        + " " * MAX_SQL_CHARACTERS
    )
    with pytest.raises(AdvisorQueryRejectedError):
        validate_query_proposal(
            QueryProposal(sql=oversized_sql, parameters={"id": "x", "limit": 10})
        )

    long_name = "a" * 65
    with pytest.raises(AdvisorQueryRejectedError):
        validate_query_proposal(
            QueryProposal(
                sql=f"SELECT hotel_id FROM saved_hotels WHERE hotel_id = :{long_name} LIMIT :limit",
                parameters={long_name: "x", "limit": 10},
            )
        )

    parameter_names = [f"p{number}" for number in range(21)]
    conditions = " OR ".join(
        f"hotel_id = :{name}" for name in parameter_names
    )
    with pytest.raises(AdvisorQueryRejectedError):
        validate_query_proposal(
            QueryProposal(
                sql=f"SELECT hotel_id FROM saved_hotels WHERE {conditions} LIMIT 10",
                parameters={name: "x" for name in parameter_names},
            )
        )


@pytest.mark.parametrize(
    "sql",
    [
        "SELECT secret FROM saved_hotels WHERE hotel_id = :id LIMIT :limit",
        "SELECT hex(name) AS encoded FROM saved_hotels WHERE hotel_id = :id LIMIT :limit",
    ],
)
def test_authorizer_denies_unknown_columns_and_functions(
    advisor_database: Path, sql: str
) -> None:
    with pytest.raises(AdvisorQueryRejectedError) as captured_error:
        execute_read_only_query(
            advisor_database,
            QueryProposal(sql=sql, parameters={"id": "x", "limit": 10}),
        )

    assert str(captured_error.value) == "The proposed hotel query is not allowed."


def test_progress_handler_interrupts_excessive_work(
    advisor_database: Path,
) -> None:
    sql = """
    SELECT hotel_id, name FROM saved_hotels
    WHERE latitude > :minimum_latitude
    ORDER BY hotel_id
    LIMIT :limit
    """
    with pytest.raises(AdvisorQueryLimitError):
        execute_read_only_query(
            advisor_database,
            QueryProposal(
                sql=sql, parameters={"minimum_latitude": 0.0, "limit": 50}
            ),
            progress_operation_limit=0,
            progress_handler_interval=1,
        )


def test_row_and_serialized_output_limits_are_enforced(
    advisor_database: Path,
) -> None:
    sql = """
    SELECT hotel_id, name FROM saved_hotels
    WHERE latitude > :minimum_latitude
    ORDER BY hotel_id
    LIMIT :limit
    """
    query = QueryProposal(
        sql=sql, parameters={"minimum_latitude": 0.0, "limit": 50}
    )

    with pytest.raises(AdvisorQueryLimitError):
        execute_read_only_query(advisor_database, query, max_result_rows=2)
    with pytest.raises(AdvisorQueryLimitError):
        execute_read_only_query(advisor_database, query, max_result_bytes=10)


def test_text_and_non_scalar_result_values_are_rejected(
    advisor_database: Path,
) -> None:
    text_query = QueryProposal(
        sql="SELECT name FROM saved_hotels WHERE hotel_id = :id LIMIT :limit",
        parameters={"id": "provider-hotel-1", "limit": 10},
    )
    with pytest.raises(AdvisorQueryResultError):
        execute_read_only_query(
            advisor_database, text_query, max_text_characters=5
        )

    blob_query = QueryProposal(
        sql="SELECT CAST(name AS BLOB) AS name_blob FROM saved_hotels WHERE hotel_id = :id LIMIT :limit",
        parameters={"id": "provider-hotel-1", "limit": 10},
    )
    with pytest.raises(AdvisorQueryResultError):
        execute_read_only_query(advisor_database, blob_query)


def test_validation_failure_opens_no_database_connection(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    connection_was_opened = False

    def fail_if_called(*args: object, **kwargs: object) -> None:
        nonlocal connection_was_opened
        connection_was_opened = True
        raise AssertionError("validation must happen before connecting")

    monkeypatch.setattr(advisor_query_module.sqlite3, "connect", fail_if_called)
    with pytest.raises(AdvisorQueryRejectedError):
        execute_read_only_query(
            Path("unused.sqlite3"),
            QueryProposal(sql="DELETE FROM saved_hotels", parameters={}),
        )

    assert connection_was_opened is False


def test_execution_errors_do_not_expose_database_or_query_details(
    tmp_path: Path,
) -> None:
    private_path = tmp_path / "private-secret-name.sqlite3"
    query = QueryProposal(
        sql="SELECT hotel_id FROM saved_hotels WHERE hotel_id = :credential LIMIT :limit",
        parameters={"credential": "credential-fragment", "limit": 10},
    )

    with pytest.raises(AdvisorQueryExecutionError) as captured_error:
        execute_read_only_query(private_path, query)

    error_text = str(captured_error.value)
    assert "private-secret-name" not in error_text
    assert "credential-fragment" not in error_text
    assert "SELECT" not in error_text
    assert "sqlite" not in error_text.lower()
    assert "openrouter.ai" not in error_text
