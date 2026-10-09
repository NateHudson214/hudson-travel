from collections.abc import Callable
from pathlib import Path
import sqlite3
from typing import Any

import pytest
from fastapi.testclient import TestClient

from backend.app.advisor_prompt import load_hotel_assistant_prompt
from backend.app.advisor_query import (
    AdvisorQueryExecutionError,
    AdvisorQueryLimitError,
    AdvisorQueryRejectedError,
    AdvisorQueryResultError,
)
from backend.app.advisor_contracts import GroundedAnswer, QueryProposal
from backend.app.main import app
from backend.app.openai_client import TOTAL_COST_PLACEHOLDER
from backend.app.openrouter import (
    OpenRouterAuthenticationError,
    OpenRouterConfigurationError,
    OpenRouterModelUnavailableError,
    OpenRouterProviderError,
    OpenRouterRateLimitError,
    OpenRouterResponseError,
    OpenRouterTransportError,
)


QUESTION = (
    "Which saved hotel has rooms from October 10 through October 12, "
    "and what is the total cost?"
)
SQL = (
    "SELECT h.hotel_id, h.name FROM saved_hotels AS h "
    "JOIN demo_hotel_nights AS n ON n.hotel_id = h.hotel_id "
    "WHERE n.stay_date >= :check_in AND n.stay_date < :check_out LIMIT 50"
)
PARAMETERS = {"check_in": "2026-10-10", "check_out": "2026-10-12"}
PROPOSAL = QueryProposal(sql=SQL, parameters=PARAMETERS)
RECORDS = [
    {
        "hotel_id": "provider-hotel-1",
        "name": "Hotel State College",
        "total_cost_cents": 22550,
        "rooms_available": 7,
    }
]
ANSWER = (
    "Hotel State College has simulated availability for the requested nights "
    "at a simulated total of $225.50."
)
PROVIDER_ANSWER_TEMPLATE = (
    "Hotel State College has simulated availability for the requested nights "
    f"at a simulated total of {TOTAL_COST_PLACEHOLDER}."
)
SAFE_PROVIDER_DETAIL = "The hotel advisor service is temporarily unavailable."
SECRET_TEXT = (
    "Bearer secret-key https://openrouter.ai/api/v1/chat/completions "
    "/private/database.sqlite3 SELECT secret"
)


def install_workflow(
    *,
    proposal: QueryProposal = PROPOSAL,
    records: list[dict[str, Any]] | None = None,
    grounded_answer: GroundedAnswer | None = None,
    events: list[str] | None = None,
) -> None:
    result_records = RECORDS if records is None else records
    result_answer = grounded_answer or GroundedAnswer(
        status="answered",
        answer=PROVIDER_ANSWER_TEMPLATE,
        total_cost_cents=22550,
    )

    async def proposer(question: str) -> QueryProposal:
        if events is not None:
            events.append("proposal")
        assert question == QUESTION
        return proposal

    def executor(
        database_path: Path, received_proposal: QueryProposal
    ) -> list[dict[str, Any]]:
        if events is not None:
            events.append("retrieval")
        assert database_path == Path(app.state.database_path)
        assert received_proposal is proposal
        return result_records

    async def answerer(
        question: str,
        proposed_sql: str,
        query_parameters: dict[str, Any],
        retrieved_records: list[dict[str, Any]],
    ) -> GroundedAnswer:
        if events is not None:
            events.append("answer")
        assert question == QUESTION
        assert proposed_sql == proposal.sql
        assert query_parameters is proposal.parameters
        assert retrieved_records is result_records
        return result_answer

    app.state.advisor_query_proposer = proposer
    app.state.advisor_query_executor = executor
    app.state.advisor_answer_generator = answerer


@pytest.mark.parametrize(
    "request_kwargs",
    [
        {},
        {"json": {}},
        {"json": {"question": None}},
        {"json": {"question": 123}},
        {"json": {"question": []}},
        {"json": {"question": ""}},
        {"json": {"question": "   \t\n"}},
        {"json": {"question": "x" * 501}},
        {"json": ["not", "an", "object"]},
    ],
)
def test_invalid_questions_return_400_without_invoking_workflow(
    client: TestClient, request_kwargs: dict[str, Any]
) -> None:
    calls: list[str] = []

    async def should_not_propose(question: str) -> QueryProposal:
        calls.append(question)
        raise AssertionError("workflow must not run")

    app.state.advisor_query_proposer = should_not_propose
    response = client.post("/api/hotel-advisor", **request_kwargs)

    assert response.status_code == 400
    assert response.json() == {
        "detail": "Enter a hotel question of 500 characters or fewer."
    }
    assert calls == []


def test_successful_answered_workflow_runs_once_in_order(
    client: TestClient, database_path: Path
) -> None:
    events: list[str] = []
    install_workflow(events=events)

    response = client.post(
        "/api/hotel-advisor", json={"question": f"  {QUESTION}  "}
    )

    assert response.status_code == 200
    assert events == ["proposal", "retrieval", "answer"]
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
    assert Path(app.state.database_path) == database_path


@pytest.mark.parametrize(
    ("records", "grounded_answer", "expected_status"),
    [
        (
            [],
            GroundedAnswer(
                status="no_matches",
                answer="No saved hotel matches the requested simulated stay.",
            ),
            "no_matches",
        ),
        (
            RECORDS,
            GroundedAnswer(
                status="insufficient_data",
                answer="The saved simulated data does not include every night.",
            ),
            "insufficient_data",
        ),
    ],
)
def test_no_match_and_insufficient_data_still_complete_second_call(
    client: TestClient,
    records: list[dict[str, Any]],
    grounded_answer: GroundedAnswer,
    expected_status: str,
) -> None:
    events: list[str] = []
    install_workflow(
        records=records, grounded_answer=grounded_answer, events=events
    )

    response = client.post(
        "/api/hotel-advisor", json={"question": QUESTION}
    )

    assert response.status_code == 200
    assert response.json()["status"] == expected_status
    assert response.json()["retrieved_records"] == records
    assert events == ["proposal", "retrieval", "answer"]


@pytest.mark.parametrize(
    ("records", "grounded_answer"),
    [
        ([], GroundedAnswer(status="answered", answer="Unsafe answer.")),
        (
            RECORDS,
            GroundedAnswer(status="no_matches", answer="Unsafe no match."),
        ),
    ],
)
def test_inconsistent_status_and_records_become_safe_provider_failure(
    client: TestClient,
    records: list[dict[str, Any]],
    grounded_answer: GroundedAnswer,
) -> None:
    install_workflow(records=records, grounded_answer=grounded_answer)

    response = client.post(
        "/api/hotel-advisor", json={"question": QUESTION}
    )

    assert response.status_code == 502
    assert response.json() == {"detail": SAFE_PROVIDER_DETAIL}


@pytest.mark.parametrize(
    ("provider_total_cents", "provider_answer"),
    [
        (2000, f"The simulated total is {TOTAL_COST_PLACEHOLDER}."),
        (200, f"The simulated total is {TOTAL_COST_PLACEHOLDER}."),
        (None, "The simulated total is $20.00."),
    ],
)
def test_misplaced_decimal_total_is_rejected_before_persistence(
    client: TestClient,
    database_path: Path,
    provider_total_cents: int | None,
    provider_answer: str,
) -> None:
    records = [
        {
            "hotel_id": "provider-hotel-1",
            "name": "Hotel State College",
            "requested_nights": 2,
            "minimum_rooms": 20,
            "total_cost_cents": 20000,
        }
    ]
    install_workflow(
        records=records,
        grounded_answer=GroundedAnswer(
            status="answered",
            answer=provider_answer,
            total_cost_cents=provider_total_cents,
        ),
    )

    response = client.post("/api/hotel-advisor", json={"question": QUESTION})

    assert response.status_code == 502
    assert response.json() == {"detail": SAFE_PROVIDER_DETAIL}
    connection = sqlite3.connect(database_path)
    try:
        assert connection.execute(
            "SELECT status, error_category FROM advisor_runs"
        ).fetchone() == ("failed", "provider_failure")
        assert connection.execute(
            "SELECT COUNT(*) FROM advisor_messages"
        ).fetchone() == (1,)
    finally:
        connection.close()


@pytest.mark.parametrize(
    "query_error",
    [
        AdvisorQueryRejectedError(SECRET_TEXT),
        AdvisorQueryLimitError(SECRET_TEXT),
    ],
)
def test_rejected_or_excessive_query_prevents_second_provider_call(
    client: TestClient, database_path: Path, query_error: Exception
) -> None:
    events: list[str] = []

    async def proposer(question: str) -> QueryProposal:
        events.append("proposal")
        return PROPOSAL

    def executor(database_path: Path, proposal: QueryProposal) -> list[dict]:
        events.append("retrieval")
        raise query_error

    async def should_not_answer(*args: object) -> GroundedAnswer:
        events.append("answer")
        raise AssertionError("second provider call must not run")

    app.state.advisor_query_proposer = proposer
    app.state.advisor_query_executor = executor
    app.state.advisor_answer_generator = should_not_answer

    response = client.post(
        "/api/hotel-advisor", json={"question": QUESTION}
    )

    assert response.status_code == 422
    assert response.json() == {
        "detail": "The proposed hotel query was rejected for safety."
    }
    assert events == ["proposal", "retrieval"]
    connection = sqlite3.connect(database_path)
    try:
        assert connection.execute(
            "SELECT status, error_category FROM advisor_runs"
        ).fetchone() == ("failed", "unsafe_query")
    finally:
        connection.close()


@pytest.mark.parametrize(
    "query_error",
    [
        AdvisorQueryExecutionError(SECRET_TEXT),
        AdvisorQueryResultError(SECRET_TEXT),
    ],
)
def test_retrieval_failure_prevents_second_provider_call(
    client: TestClient, database_path: Path, query_error: Exception
) -> None:
    events: list[str] = []

    async def proposer(question: str) -> QueryProposal:
        events.append("proposal")
        return PROPOSAL

    def executor(database_path: Path, proposal: QueryProposal) -> list[dict]:
        events.append("retrieval")
        raise query_error

    async def should_not_answer(*args: object) -> GroundedAnswer:
        events.append("answer")
        raise AssertionError("second provider call must not run")

    app.state.advisor_query_proposer = proposer
    app.state.advisor_query_executor = executor
    app.state.advisor_answer_generator = should_not_answer

    response = client.post(
        "/api/hotel-advisor", json={"question": QUESTION}
    )

    assert response.status_code == 500
    assert response.json() == {
        "detail": "The local hotel advisor data could not be retrieved."
    }
    assert events == ["proposal", "retrieval"]
    connection = sqlite3.connect(database_path)
    try:
        assert connection.execute(
            "SELECT status, error_category FROM advisor_runs"
        ).fetchone() == ("failed", "retrieval_failure")
    finally:
        connection.close()


PROVIDER_FAILURES: list[tuple[Exception, int, str]] = [
    (
        OpenRouterConfigurationError(SECRET_TEXT),
        503,
        "The hotel advisor is not configured.",
    ),
    (
        OpenRouterRateLimitError(SECRET_TEXT),
        429,
        "The hotel advisor rate limit was reached. Try again later.",
    ),
    (OpenRouterAuthenticationError(SECRET_TEXT), 502, SAFE_PROVIDER_DETAIL),
    (OpenRouterModelUnavailableError(SECRET_TEXT), 502, SAFE_PROVIDER_DETAIL),
    (OpenRouterTransportError(SECRET_TEXT), 502, SAFE_PROVIDER_DETAIL),
    (OpenRouterProviderError(SECRET_TEXT), 502, SAFE_PROVIDER_DETAIL),
    (OpenRouterResponseError(SECRET_TEXT), 502, SAFE_PROVIDER_DETAIL),
]


@pytest.mark.parametrize(
    ("provider_error", "expected_status", "expected_detail"),
    PROVIDER_FAILURES,
)
def test_proposal_failures_map_to_safe_responses_and_stop_workflow(
    client: TestClient,
    provider_error: Exception,
    expected_status: int,
    expected_detail: str,
) -> None:
    events: list[str] = []

    async def proposer(question: str) -> QueryProposal:
        events.append("proposal")
        raise provider_error

    def should_not_retrieve(*args: object) -> list[dict]:
        events.append("retrieval")
        raise AssertionError("retrieval must not run")

    async def should_not_answer(*args: object) -> GroundedAnswer:
        events.append("answer")
        raise AssertionError("second provider call must not run")

    app.state.advisor_query_proposer = proposer
    app.state.advisor_query_executor = should_not_retrieve
    app.state.advisor_answer_generator = should_not_answer

    response = client.post(
        "/api/hotel-advisor", json={"question": QUESTION}
    )

    assert response.status_code == expected_status
    assert response.json() == {"detail": expected_detail}
    assert events == ["proposal"]
    assert_no_sensitive_error_content(response.text)


@pytest.mark.parametrize(
    ("provider_error", "expected_status", "expected_detail"),
    PROVIDER_FAILURES,
)
def test_grounded_answer_failures_map_to_safe_responses(
    client: TestClient,
    provider_error: Exception,
    expected_status: int,
    expected_detail: str,
) -> None:
    events: list[str] = []

    async def proposer(question: str) -> QueryProposal:
        events.append("proposal")
        return PROPOSAL

    def executor(database_path: Path, proposal: QueryProposal) -> list[dict]:
        events.append("retrieval")
        return RECORDS

    async def answerer(*args: object) -> GroundedAnswer:
        events.append("answer")
        raise provider_error

    app.state.advisor_query_proposer = proposer
    app.state.advisor_query_executor = executor
    app.state.advisor_answer_generator = answerer

    response = client.post(
        "/api/hotel-advisor", json={"question": QUESTION}
    )

    assert response.status_code == expected_status
    assert response.json() == {"detail": expected_detail}
    assert events == ["proposal", "retrieval", "answer"]
    assert_no_sensitive_error_content(response.text)


def assert_no_sensitive_error_content(response_text: str) -> None:
    for forbidden in (
        "secret-key",
        "Bearer",
        "Authorization",
        "openrouter.ai",
        "database.sqlite3",
        "SELECT secret",
    ):
        assert forbidden not in response_text


def test_all_query_errors_are_sanitized(client: TestClient) -> None:
    async def proposer(question: str) -> QueryProposal:
        return PROPOSAL

    def executor(database_path: Path, proposal: QueryProposal) -> list[dict]:
        raise AdvisorQueryExecutionError(SECRET_TEXT)

    app.state.advisor_query_proposer = proposer
    app.state.advisor_query_executor = executor

    response = client.post(
        "/api/hotel-advisor", json={"question": QUESTION}
    )

    assert response.status_code == 500
    assert_no_sensitive_error_content(response.text)
