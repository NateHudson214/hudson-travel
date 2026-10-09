import json
import sqlite3
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from backend.app.advisor_history import (
    AdvisorConversationNotFoundError,
    complete_advisor_run,
    fail_advisor_run,
    get_advisor_conversation,
    list_advisor_conversations,
    record_advisor_proposal,
    record_advisor_retrieval,
    start_advisor_run,
)
from backend.app.database import initialize_database


DATA_DIRECTORY = Path(__file__).resolve().parents[1] / "data"
QUESTION = "Which saved hotel has rooms for both nights?"
SQL = (
    "SELECT hotel_id, stay_date FROM demo_hotel_nights "
    "WHERE stay_date >= :start_date LIMIT 50"
)
PARAMETERS = {"start_date": "2026-10-10"}
RECORDS = [{"hotel_id": "provider-hotel-1", "stay_date": "2026-10-10"}]


def initialize(path: Path) -> None:
    initialize_database(path, DATA_DIRECTORY)


def test_additive_schema_is_repeatable_and_preserves_existing_records(
    database_path: Path,
) -> None:
    initialize(database_path)
    connection = sqlite3.connect(database_path)
    try:
        baseline = {
            table: connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            for table in ("hotels", "trips", "users", "bookings")
        }
        tables = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            )
        }
    finally:
        connection.close()

    initialize(database_path)

    connection = sqlite3.connect(database_path)
    try:
        assert {
            "advisor_conversations",
            "advisor_messages",
            "advisor_runs",
        } <= tables
        assert {
            table: connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            for table in baseline
        } == baseline
        assert connection.execute(
            "SELECT COUNT(*) FROM advisor_conversations"
        ).fetchone() == (0,)
    finally:
        connection.close()


def test_completed_run_persists_full_audit_and_visible_history(
    client: TestClient, database_path: Path,
) -> None:
    initialize(database_path)
    started = start_advisor_run(
        database_path,
        question=QUESTION,
        conversation_id=None,
        prompt_version="sha256:prompt-version",
        now="2026-10-06T14:00:00+00:00",
    )
    record_advisor_proposal(
        database_path,
        started.run_id,
        proposed_sql=SQL,
        query_parameters=PARAMETERS,
    )
    record_advisor_retrieval(
        database_path,
        started.run_id,
        executed_sql=SQL,
        query_parameters=PARAMETERS,
        retrieved_records=RECORDS,
    )
    assistant_message_id = complete_advisor_run(
        database_path,
        started.run_id,
        answer="The simulated records contain one matching night.",
        result_status="answered",
        now="2026-10-06T14:00:02+00:00",
    )

    initialize(database_path)
    database_before_read = database_path.read_bytes()
    conversation = get_advisor_conversation(
        database_path, started.conversation_id
    )
    assert database_path.read_bytes() == database_before_read
    assert started == type(started)(
        conversation_id="C000001",
        user_message_id="M000001",
        run_id="R000001",
        history=[],
    )
    assert assistant_message_id == "M000002"
    assert [(message["role"], message["content"]) for message in conversation["messages"]] == [
        ("user", QUESTION),
        ("assistant", "The simulated records contain one matching night."),
    ]
    assert conversation["latest_completed_run"] == {
        "status": "answered",
        "proposed_sql": SQL,
        "query_parameters": PARAMETERS,
        "retrieved_records": RECORDS,
        "run_id": "R000001",
        "prompt_version": "sha256:prompt-version",
    }
    assert set(conversation["latest_completed_run"]) == {
        "status",
        "proposed_sql",
        "query_parameters",
        "retrieved_records",
        "run_id",
        "prompt_version",
    }
    detail = client.get(
        f"/api/advisor/conversations/{started.conversation_id}"
    )
    assert detail.status_code == 200
    assert detail.json()["latest_completed_run"] == conversation[
        "latest_completed_run"
    ]
    serialized_evidence = json.dumps(detail.json()["latest_completed_run"])
    for hidden in (
        "executed_sql",
        "provider_url",
        "authorization_header",
        "error_category",
        "error_message",
        str(database_path),
    ):
        assert hidden not in serialized_evidence.lower()
    assert list_advisor_conversations(database_path)[0]["message_count"] == 2

    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
    try:
        run = dict(
            connection.execute(
                "SELECT * FROM advisor_runs WHERE run_id = 'R000001'"
            ).fetchone()
        )
    finally:
        connection.close()
    assert run["conversation_id"] == "C000001"
    assert run["user_message_id"] == "M000001"
    assert run["assistant_message_id"] == "M000002"
    assert run["prompt_version"] == "sha256:prompt-version"
    assert run["normalized_question"] == QUESTION
    assert run["proposed_sql"] == SQL
    assert run["executed_sql"] == SQL
    assert json.loads(run["query_parameters_json"]) == PARAMETERS
    assert json.loads(run["retrieved_records_json"]) == RECORDS
    assert run["status"] == "completed"
    assert run["result_status"] == "answered"
    assert run["error_category"] is None


def test_failed_run_is_retained_and_ids_are_not_reused(
    database_path: Path,
) -> None:
    initialize(database_path)
    first = start_advisor_run(
        database_path,
        question=QUESTION,
        conversation_id=None,
        prompt_version="sha256:one",
        now="2026-10-06T14:00:00+00:00",
    )
    fail_advisor_run(
        database_path,
        first.run_id,
        error_category="unsafe_query",
        error_message="The proposed hotel query was rejected for safety.",
        now="2026-10-06T14:00:01+00:00",
    )
    assert get_advisor_conversation(
        database_path, first.conversation_id
    )["latest_completed_run"] is None

    connection = sqlite3.connect(database_path)
    try:
        connection.execute(
            "DELETE FROM advisor_conversations WHERE conversation_id = ?",
            (first.conversation_id,),
        )
        connection.commit()
    finally:
        connection.close()

    second = start_advisor_run(
        database_path,
        question="Try a different comparison.",
        conversation_id=None,
        prompt_version="sha256:two",
        now="2026-10-06T14:01:00+00:00",
    )
    assert second.conversation_id == "C000002"
    assert second.user_message_id == "M000002"
    assert second.run_id == "R000002"


def test_existing_conversation_returns_bounded_ordered_history(
    database_path: Path,
) -> None:
    initialize(database_path)
    first = start_advisor_run(
        database_path,
        question=QUESTION,
        conversation_id=None,
        prompt_version="sha256:one",
        now="2026-10-06T14:00:00+00:00",
    )
    complete_advisor_run(
        database_path,
        first.run_id,
        answer="First grounded answer.",
        result_status="answered",
        now="2026-10-06T14:00:01+00:00",
    )
    second = start_advisor_run(
        database_path,
        question="What about the next night?",
        conversation_id=first.conversation_id,
        prompt_version="sha256:one",
        now="2026-10-06T14:01:00+00:00",
    )
    assert second.history == [
        {"role": "user", "content": QUESTION},
        {"role": "assistant", "content": "First grounded answer."},
    ]
    assert second.user_message_id == "M000003"
    assert second.run_id == "R000002"


def test_unknown_conversation_is_rejected(database_path: Path) -> None:
    initialize(database_path)
    with pytest.raises(AdvisorConversationNotFoundError):
        start_advisor_run(
            database_path,
            question=QUESTION,
            conversation_id="C999999",
            prompt_version="sha256:prompt",
            now="2026-10-06T14:00:00+00:00",
        )


def test_provider_and_public_history_are_bounded_to_latest_messages(
    database_path: Path,
) -> None:
    initialize(database_path)
    conversation_id = None
    for number in range(1, 8):
        started = start_advisor_run(
            database_path,
            question=f"Question {number}",
            conversation_id=conversation_id,
            prompt_version="sha256:prompt",
            now=f"2026-10-06T14:{number:02d}:00+00:00",
        )
        conversation_id = started.conversation_id
        complete_advisor_run(
            database_path,
            started.run_id,
            answer=f"Answer {number}",
            result_status="answered",
            now=f"2026-10-06T14:{number:02d}:01+00:00",
        )

    follow_up = start_advisor_run(
        database_path,
        question="Question 8",
        conversation_id=conversation_id,
        prompt_version="sha256:prompt",
        now="2026-10-06T14:08:00+00:00",
    )
    public = get_advisor_conversation(database_path, conversation_id)

    assert len(follow_up.history) == 12
    assert follow_up.history[0]["content"] == "Question 2"
    assert follow_up.history[-1]["content"] == "Answer 7"
    assert len(public["messages"]) == 12
    assert public["messages"][0]["content"] == "Answer 2"
    assert public["messages"][-1]["content"] == "Question 8"


def test_history_endpoints_return_only_user_visible_fields(
    client: TestClient, database_path: Path
) -> None:
    started = start_advisor_run(
        database_path,
        question=QUESTION,
        conversation_id=None,
        prompt_version="sha256:not-public",
        now="2026-10-06T14:00:00+00:00",
    )
    fail_advisor_run(
        database_path,
        started.run_id,
        error_category="provider_failure",
        error_message="safe stored failure",
        now="2026-10-06T14:00:01+00:00",
    )

    summaries = client.get("/api/advisor/conversations")
    detail = client.get(f"/api/advisor/conversations/{started.conversation_id}")
    missing = client.get("/api/advisor/conversations/C999999")

    assert summaries.status_code == 200
    assert summaries.json() == [
        {
            "conversation_id": "C000001",
            "created_at": "2026-10-06T14:00:00+00:00",
            "updated_at": "2026-10-06T14:00:01+00:00",
            "message_count": 1,
            "latest_message": QUESTION,
        }
    ]
    assert detail.status_code == 200
    assert detail.json()["messages"] == [
        {
            "message_id": "M000001",
            "role": "user",
            "content": QUESTION,
            "created_at": "2026-10-06T14:00:00+00:00",
        }
    ]
    assert detail.json()["latest_completed_run"] is None
    combined = summaries.text + detail.text
    for hidden in (
        "sha256:not-public",
        "provider_failure",
        "safe stored failure",
        "proposed_sql",
        "executed_sql",
        str(database_path),
    ):
        assert hidden not in combined
    assert missing.status_code == 404
    assert missing.json() == {"detail": "The advisor conversation was not found."}
