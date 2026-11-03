from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
from pathlib import Path
import sqlite3
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.skills.routes import router


@pytest.fixture
def skills_client(client, tmp_path, monkeypatch):
    # Patch State storage directly so pytest undo restores dynamic attributes.
    monkeypatch.setitem(app.state._state, "skills_database_path", tmp_path / "skills.sqlite3")
    monkeypatch.setitem(
        app.state._state, "skills_now_provider",
        lambda: datetime(2026, 10, 21, 12, tzinfo=timezone.utc),
    )
    # A session request must not touch any configured travel-model provider.
    def unexpected_provider(*args, **kwargs):
        pytest.fail("A skills session operation reached a model provider.")
    monkeypatch.setitem(app.state._state, "advisor_query_proposer", unexpected_provider)
    monkeypatch.setitem(app.state._state, "advisor_answer_generator", unexpected_provider)
    return client


def create(client, session_id=None, **settings):
    response = client.post("/api/skills/sessions", json={
        "session_id": session_id or str(uuid4()), "display_settings": settings,
    })
    assert response.status_code in (200, 201), response.text
    return response.json()["session"]


def snapshot(**changes):
    return {
        "active_ms": 0, "pause_ms": 0, "support_ms": 0, "setup_ms": 1000,
        "cycles_completed": 0, "phase": "inhale", "phase_remaining_ms": 4000,
        **changes,
    }


def event(sequence, kind, **changes):
    return {
        "event_id": str(uuid4()), "sequence": sequence,
        "expected_revision": sequence - 1, "kind": kind,
        "snapshot": snapshot(**changes),
    }


def post_event(client, session_id, payload, code=200):
    response = client.post(f"/api/skills/sessions/{session_id}/events", json=payload)
    assert response.status_code == code, response.text
    return response.json()


def detail(client, session_id, **params):
    response = client.get(f"/api/skills/sessions/{session_id}", params=params)
    assert response.status_code == 200, response.text
    return response.json()


def test_create_defaults_and_idempotent_creation_do_not_reset_progress(skills_client):
    session = create(skills_client)
    sid = session["session_id"]
    assert session["status"] == "ready"
    assert session["revision"] == 0
    assert session["skill_id"] == "paced_breathing_4_6"
    assert session["skill_version"] == "1"
    assert session["display_settings"] == {"simpler_view": False, "motion_mode": "system"}
    post_event(skills_client, sid, event(1, "start"))
    response = skills_client.post("/api/skills/sessions", json={"session_id": sid})
    assert response.status_code == 200
    assert response.json()["replayed"]
    assert response.json()["session"]["status"] == "running"
    assert skills_client.post("/api/skills/sessions", json={
        "session_id": sid, "display_settings": {"simpler_view": True},
    }).status_code == 409


def test_full_lifecycle_keeps_pause_support_and_setup_separate(skills_client):
    sid = create(skills_client, motion_mode="static")["session_id"]
    post_event(skills_client, sid, event(1, "start"))
    progress = {"active_ms": 5000, "phase": "exhale", "phase_remaining_ms": 5000}
    post_event(skills_client, sid, event(2, "pause", **progress))
    post_event(skills_client, sid, event(3, "support_open", pause_ms=2000, **progress))
    post_event(skills_client, sid, event(4, "support_close", pause_ms=2000,
                                       support_ms=3000, **progress))
    state = detail(skills_client, sid)["session"]
    assert state["status"] == "paused" and not state["support_open"]
    post_event(skills_client, sid, event(5, "resume", pause_ms=2500, support_ms=3000, **progress))
    final = post_event(skills_client, sid, event(
        6, "complete", active_ms=60100, pause_ms=2500, support_ms=3000,
        cycles_completed=6, phase="exhale", phase_remaining_ms=0,
    ))["session"]
    assert final["status"] == "completed"
    assert final["active_ms"] == 60100 and final["setup_ms"] == 1000
    assert final["within_duration_limit"] is True
    assert final["timing_source"] == "client_reported"
    assert final["timing_verified"] is False
    assert final["started_at"] and final["ended_at"]
    saved = detail(skills_client, sid)
    assert [entry["sequence"] for entry in saved["events"]] == list(range(1, 7))


def test_opening_support_does_not_autostart_or_autoresume(skills_client):
    sid = create(skills_client)["session_id"]
    post_event(skills_client, sid, event(1, "support_open"))
    post_event(skills_client, sid, event(2, "start"), 409)
    assert detail(skills_client, sid)["session"]["revision"] == 1
    post_event(skills_client, sid, event(2, "support_close"))
    post_event(skills_client, sid, event(3, "start"))
    paused = post_event(skills_client, sid, event(4, "support_open"))["session"]
    assert paused["status"] == "paused"
    post_event(skills_client, sid, event(5, "resume"), 409)
    closed = post_event(skills_client, sid, event(5, "support_close"))["session"]
    assert closed["status"] == "paused"


def test_repeated_event_is_idempotent_even_after_later_events(skills_client):
    sid = create(skills_client)["session_id"]
    first = event(1, "start")
    post_event(skills_client, sid, first)
    post_event(skills_client, sid, event(2, "pause"))
    replay = post_event(skills_client, sid, first)
    assert replay["replayed"] and replay["session"]["revision"] == 2
    assert len(detail(skills_client, sid)["events"]) == 2
    post_event(skills_client, sid, {**first, "kind": "stop"}, 409)
    other = create(skills_client)["session_id"]
    post_event(skills_client, other, first, 409)


@pytest.mark.parametrize("kind", ["stop", "interrupt"])
@pytest.mark.parametrize("initial", ["ready", "running", "paused"])
def test_leave_or_interruption_is_terminal_from_any_nonterminal_state(skills_client, kind, initial):
    sid = create(skills_client)["session_id"]
    seq = 1
    if initial != "ready":
        post_event(skills_client, sid, event(seq, "start"))
        seq += 1
    if initial == "paused":
        post_event(skills_client, sid, event(seq, "pause"))
        seq += 1
    result = post_event(skills_client, sid, event(seq, kind))
    assert result["session"]["status"] == ("stopped" if kind == "stop" else "interrupted")
    assert result["session"]["within_duration_limit"] is False
    post_event(skills_client, sid, event(seq+1, "start"), 409)


@pytest.mark.parametrize("payload", [
    {"session_id": "not-a-uuid"},
    {"session_id": str(uuid4()), "skill_id": "model_invented_skill"},
    {"session_id": str(uuid4()), "display_settings": {"motion_mode": "flashing"}},
    {"session_id": str(uuid4()), "display_settings": {"simpler_view": "true"}},
])
def test_invalid_session_inputs_are_rejected(skills_client, payload):
    assert skills_client.post("/api/skills/sessions", json=payload).status_code == 422
    assert skills_client.get("/api/skills/sessions").json()["sessions"] == []


@pytest.mark.parametrize("field,value", [
    ("active_ms", -1), ("active_ms", True), ("active_ms", 1.5),
    ("pause_ms", "1000"), ("active_ms", 2**53),
    ("cycles_completed", 7), ("phase_remaining_ms", 6001),
    ("phase", "hold"), ("instructions", "invented content"),
])
def test_invalid_snapshot_never_creates_an_event(skills_client, field, value):
    sid = create(skills_client)["session_id"]
    payload = event(1, "start")
    payload["snapshot"][field] = value
    post_event(skills_client, sid, payload, 422)
    assert detail(skills_client, sid)["events"] == []


@pytest.mark.parametrize("change", [
    {"sequence": 2}, {"expected_revision": 1}, {"kind": "resume"},
    {"kind": "complete"}, {"reason": "user"},
])
def test_stale_out_of_order_and_invalid_transitions_rollback(skills_client, change):
    sid = create(skills_client)["session_id"]
    post_event(skills_client, sid, {**event(1, "start"), **change}, 409)
    assert detail(skills_client, sid)["session"]["revision"] == 0
    assert detail(skills_client, sid)["events"] == []


def test_timing_and_progress_cannot_move_backward_or_advance_while_paused(skills_client):
    sid = create(skills_client)["session_id"]
    post_event(skills_client, sid, event(1, "start"))
    post_event(skills_client, sid, event(2, "pause", active_ms=1000, phase_remaining_ms=3000))
    post_event(skills_client, sid, event(3, "resume", active_ms=999, phase_remaining_ms=3000), 409)
    post_event(skills_client, sid, event(3, "resume", active_ms=2000, phase_remaining_ms=2000), 409)
    post_event(skills_client, sid, event(3, "resume", active_ms=1000, phase_remaining_ms=3000,
                                       support_ms=1000), 409)
    post_event(skills_client, sid, event(3, "resume", active_ms=1000, phase_remaining_ms=3000,
                                       setup_ms=2000), 409)
    assert detail(skills_client, sid)["session"]["revision"] == 2


def test_completion_requires_six_cycles_and_preserves_over_limit_duration(skills_client):
    sid = create(skills_client)["session_id"]
    post_event(skills_client, sid, event(1, "start"))
    post_event(skills_client, sid, event(2, "complete", active_ms=59999,
                                       cycles_completed=6, phase="exhale", phase_remaining_ms=0), 409)
    result = post_event(skills_client, sid, event(2, "complete", active_ms=95000,
                                                cycles_completed=6, phase="exhale", phase_remaining_ms=0))
    assert result["session"]["status"] == "completed"
    assert result["session"]["within_duration_limit"] is False
    assert result["session"]["active_ms"] == 95000


def test_history_cursor_and_event_pagination_have_no_gaps_or_duplicates(skills_client):
    ids = {create(skills_client)["session_id"] for _ in range(5)}
    seen = []
    cursor = None
    while True:
        page = skills_client.get("/api/skills/sessions", params={
            "limit": 2, **({"cursor": cursor} if cursor else {}),
        }).json()
        seen.extend(row["session_id"] for row in page["sessions"])
        cursor = page["next_cursor"]
        if cursor is None:
            break
    assert len(seen) == len(set(seen)) == 5
    assert set(seen) == ids
    sid = seen[0]
    post_event(skills_client, sid, event(1, "start"))
    post_event(skills_client, sid, event(2, "pause"))
    post_event(skills_client, sid, event(3, "resume"))
    page = detail(skills_client, sid, limit=2)
    assert [row["sequence"] for row in page["events"]] == [1, 2]
    assert page["next_after_sequence"] == 2
    assert [row["sequence"] for row in detail(skills_client, sid, after_sequence=2)["events"]] == [3]


@pytest.mark.parametrize("cursor", ["not base64!", "e30=", "W251bGwsbnVsbF0=", "W10="])
def test_invalid_cursor_is_sanitized(skills_client, cursor):
    response = skills_client.get("/api/skills/sessions", params={"cursor": cursor})
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid skills history cursor."}


def test_query_bounds_and_missing_session(skills_client):
    for params in ({"limit": 0}, {"limit": 51}, {"cursor": "x" * 1001}):
        assert skills_client.get("/api/skills/sessions", params=params).status_code == 422
    assert skills_client.get("/api/skills/sessions/not-a-uuid").status_code == 422
    sid = str(uuid4())
    assert skills_client.get(f"/api/skills/sessions/{sid}").status_code == 404
    post_event(skills_client, sid, event(1, "start"), 404)


def test_reopening_storage_and_get_requests_preserve_unfinished_state(skills_client):
    sid = create(skills_client)["session_id"]
    post_event(skills_client, sid, event(1, "start"))
    # Every API request closes/reopens its connection and rechecks schema version.
    for _ in range(3):
        saved = detail(skills_client, sid)
        assert saved["session"]["status"] == "running"
        assert len(saved["events"]) == 1
    post_event(skills_client, sid, event(2, "interrupt"))
    assert detail(skills_client, sid)["session"]["status"] == "interrupted"


def test_concurrent_same_revision_has_exactly_one_winner(skills_client):
    sid = create(skills_client)["session_id"]
    with ThreadPoolExecutor(max_workers=2) as executor:
        responses = list(executor.map(
            lambda payload: skills_client.post(f"/api/skills/sessions/{sid}/events", json=payload),
            [event(1, "start"), event(1, "start")],
        ))
    assert sorted(response.status_code for response in responses) == [200, 409]
    assert len(detail(skills_client, sid)["events"]) == 1


def test_concurrent_retries_of_same_event_do_not_double_count(skills_client):
    sid = create(skills_client)["session_id"]
    payload = event(1, "start")
    with ThreadPoolExecutor(max_workers=2) as executor:
        responses = list(executor.map(
            lambda _: skills_client.post(f"/api/skills/sessions/{sid}/events", json=payload),
            range(2),
        ))
    assert [response.status_code for response in responses] == [200, 200]
    assert sorted(response.json()["replayed"] for response in responses) == [False, True]
    assert len(detail(skills_client, sid)["events"]) == 1


def test_records_survive_fresh_application_instances(tmp_path):
    def fresh_app():
        application = FastAPI()
        application.state.skills_database_path = tmp_path / "skills.sqlite3"
        application.state.database_path = tmp_path / "separate-travel.sqlite3"
        application.state.skills_now_provider = lambda: datetime(2026, 10, 21, tzinfo=timezone.utc)
        application.include_router(router)
        return application

    with TestClient(fresh_app()) as first:
        sid = create(first)["session_id"]
        post_event(first, sid, event(1, "start"))
        post_event(first, sid, event(2, "stop", active_ms=1000, phase_remaining_ms=3000))
    with TestClient(fresh_app()) as second:
        restored = detail(second, sid)
        assert restored["session"]["status"] == "stopped"
        assert restored["session"]["active_ms"] == 1000
        assert [entry["kind"] for entry in restored["events"]] == ["start", "stop"]


def test_locked_database_returns_safe_error_without_changes(skills_client):
    sid = create(skills_client)["session_id"]
    with sqlite3.connect(app.state.skills_database_path) as lock:
        lock.execute("BEGIN IMMEDIATE")
        response = skills_client.post(f"/api/skills/sessions/{sid}/events", json=event(1, "start"))
        assert response.status_code == 503
        assert response.json() == {"detail": "Skills session storage is unavailable."}
    assert detail(skills_client, sid)["session"]["revision"] == 0


def test_travel_database_is_untouched_and_only_skills_tables_exist(skills_client, database_path):
    before = hashlib.sha256(database_path.read_bytes()).hexdigest()
    sid = create(skills_client)["session_id"]
    post_event(skills_client, sid, event(1, "start"))
    post_event(skills_client, sid, event(2, "stop", active_ms=1000, phase_remaining_ms=3000))
    assert hashlib.sha256(database_path.read_bytes()).hexdigest() == before
    with sqlite3.connect(app.state.skills_database_path) as connection:
        tables = {row[0] for row in connection.execute("SELECT name FROM sqlite_schema WHERE type='table'")}
        assert tables == {"skills_metadata", "skills_sessions", "skills_session_events", "skills_conversations", "skills_messages", "skills_model_runs", "skills_preferences", "skills_history_state", "skills_call_budget", "skills_run_control"}
        assert connection.execute("PRAGMA user_version").fetchone()[0] == 5
        assert connection.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
        assert connection.execute("PRAGMA foreign_key_check").fetchall() == []
    assert skills_client.get("/api/trips", params={"hotel_name": "Harbor Lantern Hotel"}).status_code == 200


@pytest.mark.parametrize("mode", ["same_path", "hard_link", "travel_copy", "directory", "newer_schema", "partial_schema", "corrupt"])
def test_storage_failures_are_safe_and_travel_remains_available(skills_client, database_path, tmp_path,
                                                               monkeypatch, mode):
    path = Path(app.state.skills_database_path)
    if mode == "same_path":
        monkeypatch.setitem(app.state._state, "skills_database_path", database_path)
    elif mode == "hard_link":
        path.hardlink_to(database_path)
    elif mode == "travel_copy":
        path.write_bytes(database_path.read_bytes())
    elif mode == "directory":
        path.mkdir()
    elif mode == "corrupt":
        path.write_bytes(b"not a sqlite file")
    else:
        with sqlite3.connect(path) as connection:
            if mode == "newer_schema":
                connection.execute("PRAGMA user_version = 99")
            else:
                connection.execute("CREATE TABLE skills_sessions (bad TEXT)")
    before = hashlib.sha256(database_path.read_bytes()).hexdigest()
    response = skills_client.get("/api/skills/sessions")
    assert response.status_code == 503
    assert response.json() == {"detail": "Skills session storage is unavailable."}
    assert str(tmp_path) not in response.text
    assert hashlib.sha256(database_path.read_bytes()).hexdigest() == before
    assert skills_client.get("/api/trips", params={"hotel_name": "Harbor Lantern Hotel"}).status_code == 200


def test_transaction_failure_does_not_leave_session_ahead_of_its_event(skills_client):
    sid = create(skills_client)["session_id"]
    with sqlite3.connect(app.state.skills_database_path) as connection:
        connection.execute("""CREATE TRIGGER fail_event BEFORE INSERT ON skills_session_events
            BEGIN SELECT RAISE(ABORT, 'PRIVATE_TEST_DIAGNOSTIC'); END""")
    response = skills_client.post(f"/api/skills/sessions/{sid}/events", json=event(1, "start"))
    assert response.status_code == 503
    assert "PRIVATE_TEST_DIAGNOSTIC" not in response.text
    saved = detail(skills_client, sid)
    assert saved["session"]["revision"] == 0
    assert saved["session"]["status"] == "ready"
    assert saved["events"] == []
