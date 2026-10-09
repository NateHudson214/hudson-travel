import json
import sqlite3
from collections.abc import Callable
from pathlib import Path

import httpx
import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.advisor_prompt import load_hotel_assistant_prompt
from backend.app.openai_client import (
    GROUNDED_ANSWER_TOOL_NAME,
    OPENAI_RESPONSES_URL,
    QUERY_TOOL_NAME,
    TOTAL_COST_PLACEHOLDER,
)


FAKE_API_KEY = "fake-openai-route-key"
FAKE_MODEL = "gpt-route-test"
QUESTION = (
    "Which saved hotel has rooms from October 10 through October 12, "
    "and what is the total cost?"
)
SQL = (
    "SELECT h.hotel_id, h.name, COUNT(n.stay_date) AS requested_nights, "
    "MIN(n.rooms_available) AS minimum_rooms, "
    "SUM(n.nightly_rate_cents) AS total_cost_cents "
    "FROM saved_hotels AS h "
    "JOIN saved_hotel_searches AS s ON s.hotel_id = h.hotel_id "
    "JOIN demo_hotel_nights AS n ON n.hotel_id = h.hotel_id "
    "WHERE n.stay_date >= :check_in AND n.stay_date < :check_out "
    "GROUP BY h.hotel_id, h.name "
    "HAVING COUNT(n.stay_date) = :night_count "
    "AND MIN(n.rooms_available) > 0 "
    "ORDER BY total_cost_cents LIMIT :limit"
)
PARAMETERS = {
    "check_in": "2026-10-10",
    "check_out": "2026-10-12",
    "night_count": 2,
    "limit": 50,
}
PARAMETER_ITEMS = [
    {"name": name, "value": value} for name, value in PARAMETERS.items()
]
ANSWER = (
    "Hotel State College has simulated availability for both requested nights "
    "at a simulated total cost of $200.00."
)
PROVIDER_ANSWER_TEMPLATE = (
    "Hotel State College has simulated availability for both requested nights "
    f"at a simulated total cost of {TOTAL_COST_PLACEHOLDER}."
)
RECORDS = [
    {
        "hotel_id": "provider-hotel-1",
        "name": "Hotel State College",
        "requested_nights": 2,
        "minimum_rooms": 20,
        "total_cost_cents": 20000,
    },
]
SAFE_PROVIDER_DETAIL = "The hotel advisor service is temporarily unavailable."


def seed_advisor_records(database_path: Path) -> None:
    connection = sqlite3.connect(database_path)
    try:
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute(
            """
            INSERT INTO saved_hotels (
                hotel_id, name, address, latitude, longitude
            ) VALUES (?, ?, ?, ?, ?)
            """,
            (
                "provider-hotel-1",
                "Hotel State College",
                "100 College Avenue",
                40.7934,
                -77.86,
            ),
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
            ],
        )
        connection.execute(
            """
            INSERT INTO saved_hotel_searches (
                hotel_id, zip_code, postcode, country_code,
                latitude, longitude, locality
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "provider-hotel-1",
                "16802",
                "16802",
                "us",
                40.803,
                -77.861,
                "State College",
            ),
        )
        connection.commit()
    finally:
        connection.close()


def tool_response(tool_name: str, arguments: object) -> dict[str, object]:
    return {
        "id": "response-test",
        "status": "completed",
        "output": [
            {"type": "reasoning", "id": "reasoning-test", "summary": []},
            {
                "type": "function_call",
                "id": "function-test",
                "call_id": "call-test",
                "name": tool_name,
                "arguments": json.dumps(arguments),
            },
        ],
    }


def configure_mock_openai(
    handler: Callable[[httpx.Request], httpx.Response],
) -> None:
    app.state.openai_key_provider = lambda: FAKE_API_KEY
    app.state.openai_model_provider = lambda: FAKE_MODEL
    app.state.advisor_http_transport_provider = lambda: httpx.MockTransport(
        handler
    )


def assert_safe_response(response_text: str, database_path: Path) -> None:
    for forbidden in (
        FAKE_API_KEY,
        "Bearer",
        "Authorization",
        OPENAI_RESPONSES_URL,
        str(database_path),
        "# Hudson Travel Hotel Assistant",
    ):
        assert forbidden not in response_text


def test_default_openai_route_runs_mocked_two_call_retrieval_workflow(
    client: TestClient, database_path: Path
) -> None:
    seed_advisor_records(database_path)
    requests: list[dict[str, object]] = []

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        assert str(request.url) == OPENAI_RESPONSES_URL
        assert request.headers["Authorization"] == f"Bearer {FAKE_API_KEY}"
        payload = json.loads(request.content)
        requests.append(payload)
        assert payload["model"] == FAKE_MODEL
        assert payload["store"] is False
        assert payload["reasoning"] == {"effort": "none"}
        assert payload["input"][0]["content"].startswith(
            "# Hudson Travel Hotel Assistant"
        )
        assert "Prompt version: sha256:" in payload["input"][0]["content"]

        tool_name = payload["tools"][0]["name"]
        if tool_name == QUERY_TOOL_NAME:
            assert "October 10 through October 14, 2026" in payload["input"][0]["content"]
            assert "use 2026 in every bound date value" in payload["input"][0]["content"]
            assert "checkout to `2026-10-12`" in payload["input"][0]["content"]
            assert "exactly one flat" in payload["input"][0]["content"]
            assert "no more than two `JOIN` clauses" in payload["input"][0]["content"]
            assert payload["input"][1] == {
                "role": "user",
                "content": QUESTION,
            }
            return httpx.Response(
                200,
                json=tool_response(
                    QUERY_TOOL_NAME,
                    {"sql": SQL, "parameters": PARAMETER_ITEMS},
                ),
            )

        assert tool_name == GROUNDED_ANSWER_TOOL_NAME
        context = json.loads(payload["input"][1]["content"])
        assert context["question"] == QUESTION
        assert context["proposed_sql"] == SQL
        assert context["query_parameters"] == PARAMETERS
        assert context["retrieved_records"] == RECORDS
        return httpx.Response(
            200,
            json=tool_response(
                GROUNDED_ANSWER_TOOL_NAME,
                {
                    "status": "answered",
                    "answer": PROVIDER_ANSWER_TEMPLATE,
                    "total_cost_cents": 20000,
                },
            ),
        )

    configure_mock_openai(handler)

    response = client.post(
        "/api/hotel-advisor", json={"question": f"  {QUESTION}  "}
    )

    assert response.status_code == 200
    assert len(requests) == 2
    assert response.json() == {
        "status": "answered",
        "question": QUESTION,
        "proposed_sql": SQL,
        "query_parameters": PARAMETERS,
        "retrieved_records": RECORDS,
        "answer": ANSWER,
        "conversation_id": "C000001",
        "user_message_id": "M000001",
        "assistant_message_id": "M000002",
        "run_id": "R000001",
        "prompt_version": load_hotel_assistant_prompt().version,
    }
    assert_safe_response(response.text, database_path)

    connection = sqlite3.connect(database_path)
    try:
        assert connection.execute(
            "SELECT COUNT(*) FROM saved_hotels"
        ).fetchone()[0] == 1
        assert connection.execute(
            "SELECT COUNT(*) FROM demo_hotel_nights"
        ).fetchone() == (2,)
    finally:
        connection.close()


@pytest.mark.parametrize(
    ("query_parameters", "records_exist", "answer_status"),
    [
        (
            {**PARAMETERS, "check_in": "2027-01-01", "check_out": "2027-01-03"},
            False,
            "no_matches",
        ),
        (PARAMETERS, True, "insufficient_data"),
    ],
)
def test_default_openai_route_supports_no_match_and_insufficient_data(
    client: TestClient,
    database_path: Path,
    query_parameters: dict[str, object],
    records_exist: bool,
    answer_status: str,
) -> None:
    seed_advisor_records(database_path)
    calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        payload = json.loads(request.content)
        tool_name = payload["tools"][0]["name"]
        if tool_name == QUERY_TOOL_NAME:
            parameter_items = [
                {"name": name, "value": value}
                for name, value in query_parameters.items()
            ]
            return httpx.Response(
                200,
                json=tool_response(
                    QUERY_TOOL_NAME,
                    {"sql": SQL, "parameters": parameter_items},
                ),
            )
        context = json.loads(payload["input"][1]["content"])
        assert bool(context["retrieved_records"]) is records_exist
        return httpx.Response(
            200,
            json=tool_response(
                GROUNDED_ANSWER_TOOL_NAME,
                {
                    "status": answer_status,
                    "answer": "Safe answer based only on simulated records.",
                    "total_cost_cents": None,
                },
            ),
        )

    configure_mock_openai(handler)
    response = client.post("/api/hotel-advisor", json={"question": QUESTION})

    assert response.status_code == 200
    assert response.json()["status"] == answer_status
    assert bool(response.json()["retrieved_records"]) is records_exist
    assert calls == 2
    assert_safe_response(response.text, database_path)
    connection = sqlite3.connect(database_path)
    try:
        assert connection.execute(
            "SELECT status, result_status FROM advisor_runs"
        ).fetchone() == ("completed", answer_status)
    finally:
        connection.close()


def test_unsafe_mocked_proposal_stops_before_second_openai_call(
    client: TestClient, database_path: Path
) -> None:
    seed_advisor_records(database_path)
    calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        return httpx.Response(
            200,
            json=tool_response(
                QUERY_TOOL_NAME,
                {
                    "sql": "DELETE FROM saved_hotels WHERE hotel_id = :id",
                    "parameters": [
                        {"name": "id", "value": "provider-hotel-1"}
                    ],
                },
            ),
        )

    configure_mock_openai(handler)
    response = client.post("/api/hotel-advisor", json={"question": QUESTION})

    assert response.status_code == 422
    assert response.json() == {
        "detail": "The proposed hotel query was rejected for safety."
    }
    assert calls == 1
    assert_safe_response(response.text, database_path)

    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
    try:
        assert connection.execute(
            "SELECT COUNT(*) FROM saved_hotels"
        ).fetchone()[0] == 1
        run = dict(connection.execute("SELECT * FROM advisor_runs").fetchone())
        assert run["status"] == "failed"
        assert run["error_category"] == "unsafe_query"
        assert run["proposed_sql"].startswith("DELETE FROM saved_hotels")
        assert run["executed_sql"] is None
    finally:
        connection.close()


@pytest.mark.parametrize(
    "unsafe_sql",
    [
        (
            "SELECT hotel_id FROM saved_hotels WHERE hotel_id = :id "
            "UNION SELECT hotel_id FROM saved_hotels LIMIT :limit"
        ),
        (
            "SELECT h.hotel_id FROM saved_hotels AS h "
            "JOIN saved_hotel_searches AS s ON s.hotel_id = h.hotel_id "
            "JOIN demo_hotel_nights AS n ON n.hotel_id = h.hotel_id "
            "JOIN saved_hotels AS h2 ON h2.hotel_id = h.hotel_id "
            "WHERE h.hotel_id = :id LIMIT :limit"
        ),
    ],
)
def test_compound_or_excessive_join_proposal_stops_before_retrieval_and_answer(
    client: TestClient, database_path: Path, unsafe_sql: str
) -> None:
    seed_advisor_records(database_path)
    calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        return httpx.Response(
            200,
            json=tool_response(
                QUERY_TOOL_NAME,
                {
                    "sql": unsafe_sql,
                    "parameters": [
                        {"name": "id", "value": "provider-hotel-1"},
                        {"name": "limit", "value": 50},
                    ],
                },
            ),
        )

    configure_mock_openai(handler)

    response = client.post("/api/hotel-advisor", json={"question": QUESTION})

    assert response.status_code == 422
    assert calls == 1
    connection = sqlite3.connect(database_path)
    try:
        assert connection.execute(
            "SELECT executed_sql, error_category FROM advisor_runs"
        ).fetchone() == (None, "unsafe_query")
    finally:
        connection.close()


def test_missing_openai_configuration_returns_503_without_http(
    client: TestClient, database_path: Path
) -> None:
    app.state.openai_key_provider = lambda: None
    app.state.advisor_http_transport_provider = lambda: (_ for _ in ()).throw(
        AssertionError("transport must not be requested")
    )

    response = client.post("/api/hotel-advisor", json={"question": QUESTION})

    assert response.status_code == 503
    assert response.json() == {"detail": "The hotel advisor is not configured."}
    assert_safe_response(response.text, database_path)
    connection = sqlite3.connect(database_path)
    try:
        assert connection.execute(
            "SELECT status, error_category FROM advisor_runs"
        ).fetchone() == ("failed", "provider_configuration")
    finally:
        connection.close()


@pytest.mark.parametrize(
    ("outcome", "expected_status", "expected_detail"),
    [
        ("authentication", 502, SAFE_PROVIDER_DETAIL),
        (
            "rate_limit",
            429,
            "The hotel advisor rate limit was reached. Try again later.",
        ),
        ("model", 502, SAFE_PROVIDER_DETAIL),
        ("http", 502, SAFE_PROVIDER_DETAIL),
        ("timeout", 502, SAFE_PROVIDER_DETAIL),
        ("network", 502, SAFE_PROVIDER_DETAIL),
        ("malformed", 502, SAFE_PROVIDER_DETAIL),
    ],
)
def test_mocked_openai_failures_map_to_safe_route_responses(
    client: TestClient,
    database_path: Path,
    outcome: str,
    expected_status: int,
    expected_detail: str,
) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if outcome == "authentication":
            return httpx.Response(401, json={"error": FAKE_API_KEY})
        if outcome == "rate_limit":
            return httpx.Response(429, json={"error": FAKE_API_KEY})
        if outcome == "model":
            return httpx.Response(
                400,
                json={
                    "error": {
                        "code": "model_not_found",
                        "message": FAKE_API_KEY,
                    }
                },
            )
        if outcome == "http":
            return httpx.Response(500, json={"error": FAKE_API_KEY})
        if outcome == "timeout":
            raise httpx.ReadTimeout(
                f"Bearer {FAKE_API_KEY} at {OPENAI_RESPONSES_URL}",
                request=request,
            )
        if outcome == "network":
            raise httpx.ConnectError(
                f"Bearer {FAKE_API_KEY} at {database_path}", request=request
            )
        return httpx.Response(200, content=b"not-json")

    configure_mock_openai(handler)
    response = client.post("/api/hotel-advisor", json={"question": QUESTION})

    assert response.status_code == expected_status
    assert response.json() == {"detail": expected_detail}
    assert_safe_response(response.text, database_path)
    connection = sqlite3.connect(database_path)
    try:
        status, category, message = connection.execute(
            "SELECT status, error_category, error_message FROM advisor_runs"
        ).fetchone()
    finally:
        connection.close()
    assert status == "failed"
    assert category in {"provider_rate_limit", "provider_failure"}
    for forbidden in (
        FAKE_API_KEY,
        "Bearer",
        "Authorization",
        OPENAI_RESPONSES_URL,
        str(database_path),
    ):
        assert forbidden not in message


def test_follow_up_sends_bounded_ordered_history_to_both_openai_stages(
    client: TestClient, database_path: Path
) -> None:
    seed_advisor_records(database_path)
    follow_up = "Does that hotel still have at least seven rooms each night?"
    payloads: list[dict[str, object]] = []

    def handler(request: httpx.Request) -> httpx.Response:
        payload = json.loads(request.content)
        payloads.append(payload)
        tool_name = payload["tools"][0]["name"]
        if tool_name == QUERY_TOOL_NAME:
            return httpx.Response(
                200,
                json=tool_response(
                    QUERY_TOOL_NAME,
                    {"sql": SQL, "parameters": PARAMETER_ITEMS},
                ),
            )
        return httpx.Response(
            200,
            json=tool_response(
                GROUNDED_ANSWER_TOOL_NAME,
                {
                    "status": "answered",
                    "answer": PROVIDER_ANSWER_TEMPLATE,
                    "total_cost_cents": 20000,
                },
            ),
        )

    configure_mock_openai(handler)
    first = client.post("/api/hotel-advisor", json={"question": QUESTION})
    assert first.status_code == 200

    second = client.post(
        "/api/hotel-advisor",
        json={
            "question": follow_up,
            "conversation_id": first.json()["conversation_id"],
        },
    )

    assert second.status_code == 200
    assert second.json()["conversation_id"] == first.json()["conversation_id"]
    assert second.json()["user_message_id"] == "M000003"
    assert second.json()["assistant_message_id"] == "M000004"
    assert second.json()["run_id"] == "R000002"
    expected_history = [
        {"role": "user", "content": QUESTION},
        {"role": "assistant", "content": ANSWER},
    ]
    for payload in payloads[2:]:
        assert payload["input"][1:3] == expected_history
    assert payloads[2]["input"][3] == {
        "role": "user",
        "content": follow_up,
    }
    grounded_context = json.loads(payloads[3]["input"][3]["content"])
    assert grounded_context["question"] == follow_up
    assert grounded_context["proposed_sql"] == SQL
    assert grounded_context["query_parameters"] == PARAMETERS
    assert grounded_context["retrieved_records"] == RECORDS

    history = client.get(
        f"/api/advisor/conversations/{first.json()['conversation_id']}"
    )
    assert history.status_code == 200
    assert [message["role"] for message in history.json()["messages"]] == [
        "user",
        "assistant",
        "user",
        "assistant",
    ]
    assert [message["content"] for message in history.json()["messages"]] == [
        QUESTION,
        ANSWER,
        follow_up,
        ANSWER,
    ]
    assert_safe_response(second.text + history.text, database_path)

    connection = sqlite3.connect(database_path)
    try:
        stored = " ".join(
            str(value)
            for table in (
                "advisor_conversations",
                "advisor_messages",
                "advisor_runs",
            )
            for row in connection.execute(f"SELECT * FROM {table}")
            for value in row
            if value is not None
        )
    finally:
        connection.close()
    for forbidden in (
        FAKE_API_KEY,
        "Authorization",
        OPENAI_RESPONSES_URL,
        "# Hudson Travel Hotel Assistant",
        str(database_path),
    ):
        assert forbidden not in stored


def test_unknown_conversation_id_returns_safe_404_before_provider_call(
    client: TestClient, database_path: Path
) -> None:
    app.state.openai_key_provider = lambda: (_ for _ in ()).throw(
        AssertionError("provider configuration must not be requested")
    )

    response = client.post(
        "/api/hotel-advisor",
        json={"question": QUESTION, "conversation_id": "C999999"},
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "The advisor conversation was not found."
    }
    assert_safe_response(response.text, database_path)
