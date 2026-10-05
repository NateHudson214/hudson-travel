import sqlite3
from pathlib import Path
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

from backend.app import main as main_module
from backend.app.database import connect_database, initialize_database
from backend.app.main import DATA_DIRECTORY


def save_payload(
    place_id: str = "provider-place-1", zip_code: str = "16802"
) -> dict[str, object]:
    return {
        "zip_code": zip_code,
        "location": {
            "postcode": zip_code,
            "country_code": "us",
            "latitude": 40.803167822,
            "longitude": -77.861384958,
            "locality": "State College",
        },
        "hotel": {
            "place_id": place_id,
            "name": "Example Hotel",
            "formatted_address": None,
            "latitude": 40.8,
            "longitude": -77.86,
        },
    }


def test_save_is_idempotent_and_preserves_changed_demo_values(
    client: TestClient, database_path: Path
) -> None:
    first = client.post("/api/saved-hotels", json=save_payload())

    assert first.status_code == 201
    assert first.json()["hotel"]["place_id"] == "provider-place-1"
    assert first.json()["hotel"]["name"] == "Example Hotel"
    assert first.json()["hotel"]["formatted_address"] is None
    assert first.json()["searched_zip_code"] == "16802"
    assert [night["stay_date"] for night in first.json()["hotel"]["nights"]] == [
        f"2026-10-{day:02d}" for day in range(10, 15)
    ]
    assert all(
        night["nightly_rate_cents"] == 10000
        and night["rooms_available"] == 20
        for night in first.json()["hotel"]["nights"]
    )

    connection = connect_database(database_path)
    try:
        connection.execute(
            """
            UPDATE demo_hotel_nights
            SET nightly_rate_cents = 12550, rooms_available = 7
            WHERE hotel_id = 'provider-place-1' AND stay_date = '2026-10-12'
            """
        )
        connection.commit()
    finally:
        connection.close()

    repeated_payload = save_payload()
    repeated_payload["hotel"]["name"] = "Changed provider name"
    repeated = client.post("/api/saved-hotels", json=repeated_payload)

    assert repeated.status_code == 201
    assert repeated.json()["hotel"]["name"] == "Example Hotel"
    changed_night = next(
        night
        for night in repeated.json()["hotel"]["nights"]
        if night["stay_date"] == "2026-10-12"
    )
    assert changed_night == {
        "stay_date": "2026-10-12",
        "nightly_rate_cents": 12550,
        "rooms_available": 7,
    }

    initialize_database(database_path, DATA_DIRECTORY)
    persisted = client.get(
        "/api/saved-hotels", params={"zip_code": "16802"}
    ).json()["hotels"][0]
    assert next(
        night
        for night in persisted["nights"]
        if night["stay_date"] == "2026-10-12"
    ) == changed_night

    connection = connect_database(database_path)
    try:
        assert connection.execute("SELECT COUNT(*) FROM saved_hotels").fetchone()[
            0
        ] == 1
        assert connection.execute(
            "SELECT COUNT(*) FROM saved_hotel_searches"
        ).fetchone()[0] == 1
        assert connection.execute(
            "SELECT COUNT(*) FROM demo_hotel_nights"
        ).fetchone()[0] == 5
    finally:
        connection.close()


def test_same_provider_hotel_can_be_associated_with_multiple_zips(
    client: TestClient, database_path: Path
) -> None:
    assert client.post("/api/saved-hotels", json=save_payload()).status_code == 201
    second_payload = save_payload(zip_code="02113")
    second_payload["location"] = {
        "postcode": "02113",
        "country_code": "us",
        "latitude": 42.365,
        "longitude": -71.055,
        "locality": "Boston",
    }
    assert client.post("/api/saved-hotels", json=second_payload).status_code == 201

    connection = connect_database(database_path)
    try:
        assert connection.execute("SELECT COUNT(*) FROM saved_hotels").fetchone()[
            0
        ] == 1
        assert [
            row[0]
            for row in connection.execute(
                "SELECT zip_code FROM saved_hotel_searches ORDER BY zip_code"
            )
        ] == ["02113", "16802"]
        assert connection.execute(
            "SELECT COUNT(*) FROM demo_hotel_nights"
        ).fetchone()[0] == 5
    finally:
        connection.close()


def test_saved_hotel_ids_and_local_zip_retrieval_include_context_and_nights(
    client: TestClient,
) -> None:
    assert client.post("/api/saved-hotels", json=save_payload()).status_code == 201
    assert client.post(
        "/api/saved-hotels", json=save_payload("provider-place-2")
    ).status_code == 201

    ids = client.get("/api/saved-hotels/ids")
    local = client.get("/api/saved-hotels", params={"zip_code": " 16802 "})

    assert ids.status_code == 200
    assert ids.json() == {
        "place_ids": ["provider-place-1", "provider-place-2"]
    }
    assert local.status_code == 200
    assert local.json()["searched_zip_code"] == "16802"
    assert local.json()["location"] == save_payload()["location"]
    assert [hotel["place_id"] for hotel in local.json()["hotels"]] == [
        "provider-place-1",
        "provider-place-2",
    ]
    assert all(len(hotel["nights"]) == 5 for hotel in local.json()["hotels"])


def test_local_zip_lookup_returns_http_200_empty_without_provider_calls(
    client: TestClient,
) -> None:
    response = client.get("/api/saved-hotels", params={"zip_code": "02113"})

    assert response.status_code == 200
    assert response.json() == {
        "searched_zip_code": "02113",
        "location": None,
        "hotels": [],
    }


def test_delete_removes_one_hotel_associations_and_nights_transactionally(
    client: TestClient, database_path: Path
) -> None:
    assert client.post("/api/saved-hotels", json=save_payload()).status_code == 201
    assert client.post(
        "/api/saved-hotels", json=save_payload("provider-place-2")
    ).status_code == 201

    response = client.delete("/api/saved-hotels/provider-place-1")

    assert response.status_code == 204
    connection = connect_database(database_path)
    try:
        assert connection.execute(
            "SELECT COUNT(*) FROM saved_hotels WHERE hotel_id = 'provider-place-1'"
        ).fetchone()[0] == 0
        assert connection.execute(
            """
            SELECT COUNT(*) FROM saved_hotel_searches
            WHERE hotel_id = 'provider-place-1'
            """
        ).fetchone()[0] == 0
        assert connection.execute(
            """
            SELECT COUNT(*) FROM demo_hotel_nights
            WHERE hotel_id = 'provider-place-1'
            """
        ).fetchone()[0] == 0
        assert connection.execute(
            "SELECT COUNT(*) FROM saved_hotels WHERE hotel_id = 'provider-place-2'"
        ).fetchone()[0] == 1
        assert connection.execute(
            """
            SELECT COUNT(*) FROM demo_hotel_nights
            WHERE hotel_id = 'provider-place-2'
            """
        ).fetchone()[0] == 5
        assert connection.execute("SELECT COUNT(*) FROM hotels").fetchone()[0] == 8
        assert connection.execute("SELECT COUNT(*) FROM bookings").fetchone()[0] == 6
    finally:
        connection.close()

    missing = client.delete("/api/saved-hotels/provider-place-1")
    assert missing.status_code == 404
    assert missing.json() == {"detail": "Saved hotel was not found."}


@pytest.mark.parametrize(
    "submitted_zip",
    [None, "", "   ", "1234", "123456", "12a45", "12-45", "１２３４５"],
)
def test_local_lookup_reuses_strict_zip_validation(
    client: TestClient, submitted_zip: str | None
) -> None:
    params = {} if submitted_zip is None else {"zip_code": submitted_zip}

    response = client.get("/api/saved-hotels", params=params)

    assert response.status_code == 400
    assert response.json() == {"detail": "Enter a five-digit U.S. ZIP code."}


@pytest.mark.parametrize(
    "operation",
    ["list_saved_hotels_for_zip", "list_saved_hotel_ids", "save_local_hotel_record"],
)
def test_database_failures_are_safe_errors(
    client: TestClient, monkeypatch: pytest.MonkeyPatch, operation: str
) -> None:
    def fail(*args: object, **kwargs: object) -> object:
        raise sqlite3.OperationalError("private database path must stay hidden")

    monkeypatch.setattr(main_module, operation, fail)
    if operation == "list_saved_hotels_for_zip":
        response = client.get("/api/saved-hotels", params={"zip_code": "16802"})
    elif operation == "list_saved_hotel_ids":
        response = client.get("/api/saved-hotels/ids")
    else:
        response = client.post("/api/saved-hotels", json=save_payload())

    assert response.status_code == 500
    assert response.json() == {
        "detail": "Local hotel storage is temporarily unavailable."
    }
    assert "private database path" not in response.text


def test_deletion_database_failure_is_safe_and_preserves_record(
    client: TestClient,
    database_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    assert client.post("/api/saved-hotels", json=save_payload()).status_code == 201

    def fail(*args: object, **kwargs: object) -> None:
        raise sqlite3.OperationalError("private database path must stay hidden")

    monkeypatch.setattr(main_module, "delete_local_hotel_record", fail)
    response = client.delete("/api/saved-hotels/provider-place-1")

    assert response.status_code == 500
    assert "private database path" not in response.text
    connection = connect_database(database_path)
    try:
        assert connection.execute("SELECT COUNT(*) FROM saved_hotels").fetchone()[
            0
        ] == 1
    finally:
        connection.close()


def test_repeat_initialization_preserves_saved_local_data(
    client: TestClient, database_path: Path
) -> None:
    assert client.post("/api/saved-hotels", json=save_payload()).status_code == 201

    initialize_database(database_path, DATA_DIRECTORY)

    response = client.get("/api/saved-hotels", params={"zip_code": "16802"})
    assert response.status_code == 200
    assert [hotel["place_id"] for hotel in response.json()["hotels"]] == [
        "provider-place-1"
    ]


def test_provider_id_is_preserved_through_encoded_delete_route(
    client: TestClient,
) -> None:
    provider_id = "provider/place 1"
    assert client.post(
        "/api/saved-hotels", json=save_payload(provider_id)
    ).status_code == 201

    response = client.delete(
        f"/api/saved-hotels/{quote(provider_id, safe='')}"
    )

    assert response.status_code == 204
    assert client.get("/api/saved-hotels/ids").json() == {"place_ids": []}


@pytest.mark.parametrize("invalid_zip", ["", "1234", "12a45", "１２３４５"])
def test_save_rejects_invalid_searched_zip(
    client: TestClient, invalid_zip: str
) -> None:
    response = client.post(
        "/api/saved-hotels", json=save_payload(zip_code=invalid_zip)
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "Enter a five-digit U.S. ZIP code."}
