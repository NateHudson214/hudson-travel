from fastapi.testclient import TestClient


def test_harbor_lantern_search_returns_every_joined_stay(
    client: TestClient,
) -> None:
    response = client.get(
        "/api/trips", params={"hotel_name": "Harbor Lantern Hotel"}
    )

    assert response.status_code == 200
    results = response.json()
    assert [result["trip_id"] for result in results] == ["T001", "T009"]
    assert results[0] == {
        "trip_id": "T001",
        "trip_name": "Boston Harbor Weekend",
        "hotel_id": "H001",
        "hotel_name": "Harbor Lantern Hotel",
        "city": "Boston",
        "state": "MA",
        "nightly_rate_usd": 150.0,
        "check_in": "2026-09-18",
        "check_out": "2026-09-20",
    }


def test_search_trims_hotel_name_and_matches_case_insensitively(
    client: TestClient,
) -> None:
    response = client.get(
        "/api/trips", params={"hotel_name": "  harbor lantern hotel  "}
    )

    assert response.status_code == 200
    assert [result["trip_id"] for result in response.json()] == ["T001", "T009"]


def test_partial_hotel_name_search_returns_associated_stays(
    client: TestClient,
) -> None:
    response = client.get("/api/trips", params={"hotel_name": "Lantern"})

    assert response.status_code == 200
    assert [result["trip_id"] for result in response.json()] == ["T001", "T009"]


def test_unmatched_hotel_name_returns_empty_list(client: TestClient) -> None:
    response = client.get("/api/trips", params={"hotel_name": "Not a Real Hotel"})

    assert response.status_code == 200
    assert response.json() == []


def test_search_treats_sql_wildcard_characters_as_hotel_name_text(
    client: TestClient,
) -> None:
    response = client.get("/api/trips", params={"hotel_name": "%"})

    assert response.status_code == 200
    assert response.json() == []


def test_missing_hotel_name_returns_clear_client_error(client: TestClient) -> None:
    response = client.get("/api/trips")

    assert response.status_code == 400
    assert response.json() == {"detail": "Enter a hotel name to search."}


def test_blank_hotel_name_returns_clear_client_error(client: TestClient) -> None:
    response = client.get("/api/trips", params={"hotel_name": "   "})

    assert response.status_code == 400
    assert response.json() == {"detail": "Enter a hotel name to search."}
