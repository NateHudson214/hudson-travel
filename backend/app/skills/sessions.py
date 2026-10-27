"""Isolated SQLite records for fictional skills sessions, never travel data."""

import base64
from contextlib import contextmanager
from datetime import datetime
import json
from pathlib import Path
import sqlite3
from uuid import UUID


SCHEMA_VERSION = 5
SESSION_TABLES = {"skills_metadata", "skills_sessions", "skills_session_events"}
V2_TABLES = SESSION_TABLES | {"skills_conversations", "skills_messages", "skills_model_runs"}
V3_TABLES = V2_TABLES | {"skills_preferences"}
V4_TABLES = V3_TABLES | {"skills_history_state"}
from .live_schema import TABLES as LIVE_TABLES
TABLES = V4_TABLES | LIVE_TABLES
TERMINAL = {"completed", "stopped", "interrupted"}
SCHEMA = (
    "CREATE TABLE skills_metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL)",
    """CREATE TABLE skills_sessions (
        session_id TEXT PRIMARY KEY,
        skill_id TEXT NOT NULL CHECK (skill_id = 'paced_breathing_4_6'),
        skill_version TEXT NOT NULL CHECK (skill_version = '1'),
        status TEXT NOT NULL CHECK (status IN
            ('ready','running','paused','completed','stopped','interrupted')),
        revision INTEGER NOT NULL CHECK (revision >= 0),
        settings_json TEXT NOT NULL,
        created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
        started_at TEXT, ended_at TEXT,
        active_ms INTEGER NOT NULL CHECK (active_ms >= 0),
        pause_ms INTEGER NOT NULL CHECK (pause_ms >= 0),
        support_ms INTEGER NOT NULL CHECK (support_ms >= 0),
        setup_ms INTEGER NOT NULL CHECK (setup_ms >= 0),
        cycles_completed INTEGER NOT NULL CHECK (cycles_completed BETWEEN 0 AND 6),
        phase TEXT NOT NULL CHECK (phase IN ('inhale','exhale')),
        phase_remaining_ms INTEGER NOT NULL CHECK (phase_remaining_ms BETWEEN 0 AND 6000),
        support_open INTEGER NOT NULL CHECK (support_open IN (0,1))
    )""",
    """CREATE TABLE skills_session_events (
        event_id TEXT PRIMARY KEY,
        session_id TEXT NOT NULL REFERENCES skills_sessions(session_id) ON DELETE CASCADE,
        sequence INTEGER NOT NULL CHECK (sequence > 0),
        kind TEXT NOT NULL CHECK (kind IN ('start','checkpoint','pause','resume',
            'support_open','support_close','stop','complete','interrupt')),
        created_at TEXT NOT NULL,
        payload_json TEXT NOT NULL,
        UNIQUE (session_id, sequence)
    )""",
    "CREATE INDEX skills_session_order ON skills_sessions(created_at DESC, session_id DESC)",
)


class SkillsStorageError(Exception):
    pass


class SessionNotFound(Exception):
    pass


class SessionConflict(Exception):
    pass


class InvalidCursor(Exception):
    pass


def canonical_json(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


@contextmanager
def open_sessions(path: Path, travel_path: Path):
    connection = None
    try:
        if path.resolve() == travel_path.resolve() or (
            path.exists() and travel_path.exists() and path.samefile(travel_path)
        ):
            raise SkillsStorageError("Skills storage must be separate.")
        path.parent.mkdir(parents=True, exist_ok=True)
        # FastAPI may enter/use/exit one sync dependency on different workers.
        # Each request still owns its connection; transactions serialize writes.
        connection = sqlite3.connect(path, timeout=2, check_same_thread=False)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        with connection:
            connection.execute("BEGIN IMMEDIATE")
            tables = {row[0] for row in connection.execute(
                "SELECT name FROM sqlite_schema WHERE type='table' AND name NOT LIKE 'sqlite_%'"
            )}
            version = connection.execute("PRAGMA user_version").fetchone()[0]
            # Explicit additive migrations; never recreate older records.
            from .conversations import SCHEMA as CONVERSATION_SCHEMA
            from .preferences import SCHEMA as PREFERENCE_SCHEMA
            from .history import SCHEMA as HISTORY_SCHEMA
            if not tables and version == 0:
                for statement in (*SCHEMA, *CONVERSATION_SCHEMA, *PREFERENCE_SCHEMA, *HISTORY_SCHEMA):
                    connection.execute(statement)
                connection.execute("INSERT INTO skills_metadata VALUES ('schema_version', '4')")
                connection.execute("PRAGMA user_version = 4")
            elif ((tables == SESSION_TABLES and version == 1)
                  or (tables == V2_TABLES and version == 2)
                  or (tables == V3_TABLES and version == 3)
                  or (tables == V4_TABLES and version == 4)
                  or (tables == TABLES and version == SCHEMA_VERSION)):
                row = connection.execute(
                    "SELECT value FROM skills_metadata WHERE key='schema_version'"
                ).fetchone()
                if row is None or row[0] != str(version):
                    raise SkillsStorageError("Unsupported skills schema.")
                if version < 4:
                    connection.execute("""SELECT session_id,skill_id,skill_version,status,
                        revision,settings_json,created_at,updated_at,started_at,ended_at,
                        active_ms,pause_ms,support_ms,setup_ms,cycles_completed,phase,
                        phase_remaining_ms,support_open FROM skills_sessions LIMIT 0""")
                    connection.execute("SELECT event_id,session_id,sequence,kind,created_at,payload_json FROM skills_session_events LIMIT 0")
                    if version == 1:
                        for statement in CONVERSATION_SCHEMA:
                            connection.execute(statement)
                if version < 4:
                    # Validate legacy columns before modifying the database.
                    connection.execute("SELECT conversation_id,session_id,placement,created_at,updated_at,revision FROM skills_conversations LIMIT 0")
                    connection.execute("SELECT message_id,conversation_id,sequence,role,content,source,created_at,reply_id,fact_ids_json FROM skills_messages LIMIT 0")
                    connection.execute("SELECT request_id,conversation_id,user_message_id,payload_json,response_json,status,mode,model_id,context_version,context_hash,error_category,created_at FROM skills_model_runs LIMIT 0")
                    if version < 3:
                        for statement in PREFERENCE_SCHEMA:
                            connection.execute(statement)
                if version < 4:
                    connection.execute("SELECT singleton_id,revision,has_saved,simpler_view,motion_mode,updated_at,last_request_id,last_payload_json FROM skills_preferences LIMIT 0")
                    for statement in HISTORY_SCHEMA:
                        connection.execute(statement)
                    connection.execute("UPDATE skills_metadata SET value='4' WHERE key='schema_version'")
                    connection.execute("PRAGMA user_version = 4")
            else:
                raise SkillsStorageError("Unsupported skills schema.")
            if version < 5:
                from .live_schema import migrate
                migrate(connection)
        yield SessionStore(connection)
    except (sqlite3.Error, OSError) as error:
        raise SkillsStorageError("Skills storage is unavailable.") from error
    finally:
        if connection is not None:
            connection.close()


def session_view(row):
    result = dict(row)
    result["display_settings"] = json.loads(result.pop("settings_json"))
    result["support_open"] = bool(result["support_open"])
    result["within_duration_limit"] = (
        result["status"] == "completed" and result["active_ms"] <= 90000
    )
    result["timing_source"] = "client_reported"
    result["timing_verified"] = False
    return result


def event_view(row):
    payload = json.loads(row["payload_json"])
    return {
        "event_id": row["event_id"], "sequence": row["sequence"],
        "kind": row["kind"], "created_at": row["created_at"],
        "snapshot": payload["snapshot"], "reason": payload["reason"],
    }


def position(snapshot):
    duration = 4000 if snapshot["phase"] == "inhale" else 6000
    return (snapshot["cycles_completed"] * 10000
            + (4000 if snapshot["phase"] == "exhale" else 0)
            + duration - snapshot["phase_remaining_ms"])


def validate_transition(old, event):
    kind, data = event["kind"], event["snapshot"]
    previous = old["status"]
    if previous in TERMINAL:
        raise SessionConflict("A finished session cannot change.")
    if event["reason"] is not None and kind != "pause":
        raise SessionConflict("A pause reason requires a pause event.")
    duration = 4000 if data["phase"] == "inhale" else 6000
    if data["phase_remaining_ms"] > duration:
        raise SessionConflict("Invalid phase duration.")
    if data["cycles_completed"] == 6:
        if (data["phase"] != "exhale" or data["phase_remaining_ms"] != 0
                or kind not in {"complete", "stop", "interrupt"}):
            raise SessionConflict("Invalid final phase.")
        progress = 60000
    else:
        if data["phase_remaining_ms"] == 0:
            raise SessionConflict("A nonfinal phase must have remaining time.")
        progress = position(data)
    old_progress = 60000 if old["cycles_completed"] == 6 else position(old)
    if progress < old_progress or data["active_ms"] < progress:
        raise SessionConflict("Progress or active time is inconsistent.")
    for field in ("active_ms", "pause_ms", "support_ms", "setup_ms"):
        if data[field] < old[field]:
            raise SessionConflict("Durations cannot decrease.")
    if previous != "ready" and data["setup_ms"] != old["setup_ms"]:
        raise SessionConflict("Setup time is fixed after start.")
    if previous == "ready" and (progress or any(
        data[field] for field in ("active_ms", "pause_ms", "support_ms")
    )):
        raise SessionConflict("An unstarted session cannot record exercise time.")
    if previous == "running" and any(
        data[field] != old[field] for field in ("pause_ms", "support_ms")
    ):
        raise SessionConflict("Running time cannot increase excluded time.")
    if previous == "paused":
        fixed = "pause_ms" if old["support_open"] else "support_ms"
        if (progress != old_progress or data["active_ms"] != old["active_ms"]
                or data[fixed] != old[fixed]):
            raise SessionConflict("Paused progress or excluded time is inconsistent.")

    new_status, support_open = previous, old["support_open"]
    if kind == "start" and previous == "ready" and not support_open:
        new_status = "running"
    elif kind == "checkpoint" and previous in {"running", "paused"}:
        pass
    elif kind == "pause" and previous == "running":
        new_status = "paused"
    elif kind == "resume" and previous == "paused" and not support_open:
        new_status = "running"
    elif kind == "support_open" and not support_open:
        support_open = 1
        if previous == "running":
            new_status = "paused"
    elif kind == "support_close" and support_open:
        support_open = 0
    elif kind == "stop":
        new_status = "stopped"
    elif kind == "interrupt":
        new_status = "interrupted"
    elif kind == "complete" and previous == "running" and data["cycles_completed"] == 6:
        new_status = "completed"
    else:
        raise SessionConflict("This event is not valid for the current state.")
    return new_status, support_open


class SessionStore:
    def __init__(self, connection):
        self.connection = connection

    def get(self, session_id):
        row = self.connection.execute(
            "SELECT * FROM skills_sessions WHERE session_id = ?", (session_id,)
        ).fetchone()
        if row is None:
            raise SessionNotFound("Session not found.")
        return row

    def create(self, session_id, settings, now, history_epoch=0):
        encoded = canonical_json(settings)
        with self.connection:
            self.connection.execute("BEGIN IMMEDIATE")
            from .history import require_epoch
            require_epoch(self.connection, history_epoch)
            existing = self.connection.execute(
                "SELECT * FROM skills_sessions WHERE session_id = ?", (session_id,)
            ).fetchone()
            if existing is not None:
                if existing["settings_json"] != encoded:
                    raise SessionConflict("Session ID was already used with different settings.")
                return session_view(existing), True
            self.connection.execute(
                """INSERT INTO skills_sessions VALUES (
                    ?, 'paced_breathing_4_6', '1', 'ready', 0, ?, ?, ?, NULL, NULL,
                    0, 0, 0, 0, 0, 'inhale', 4000, 0
                )""", (session_id, encoded, now, now),
            )
        return session_view(self.get(session_id)), False

    def append(self, session_id, event, now):
        encoded = canonical_json(event)
        with self.connection:
            self.connection.execute("BEGIN IMMEDIATE")
            from .history import require_epoch
            require_epoch(self.connection, event.get('history_epoch', 0))
            old = self.get(session_id)
            existing = self.connection.execute(
                "SELECT * FROM skills_session_events WHERE event_id = ?", (event["event_id"],)
            ).fetchone()
            if existing is not None:
                if existing["session_id"] != session_id or canonical_json({"history_epoch": 0, **json.loads(existing["payload_json"])}) != canonical_json({"history_epoch": 0, **event}):
                    raise SessionConflict("Event ID was already used with different data.")
                return {"session": session_view(old), "event": event_view(existing), "replayed": True}
            if (event["expected_revision"] != old["revision"]
                    or event["sequence"] != old["revision"] + 1):
                raise SessionConflict("The event is stale or out of order.")
            new_status, support_open = validate_transition(old, event)
            data = event["snapshot"]
            started_at = now if event["kind"] == "start" else old["started_at"]
            ended_at = now if new_status in TERMINAL else None
            self.connection.execute(
                """UPDATE skills_sessions SET status=?, revision=?, updated_at=?,
                    started_at=?, ended_at=?, active_ms=?, pause_ms=?, support_ms=?,
                    setup_ms=?, cycles_completed=?, phase=?, phase_remaining_ms=?, support_open=?
                    WHERE session_id=?""",
                (new_status, event["sequence"], now, started_at, ended_at,
                 data["active_ms"], data["pause_ms"], data["support_ms"], data["setup_ms"],
                 data["cycles_completed"], data["phase"], data["phase_remaining_ms"],
                 support_open, session_id),
            )
            self.connection.execute(
                "INSERT INTO skills_session_events VALUES (?, ?, ?, ?, ?, ?)",
                (event["event_id"], session_id, event["sequence"], event["kind"], now, encoded),
            )
            saved = self.connection.execute(
                "SELECT * FROM skills_session_events WHERE event_id=?", (event["event_id"],)
            ).fetchone()
            return {"session": session_view(self.get(session_id)), "event": event_view(saved), "replayed": False}

    def detail(self, session_id, after_sequence=0, limit=50):
        with self.connection:
            self.connection.execute("BEGIN")
            from .history import state
            epoch = state(self.connection)['epoch']
            session = session_view(self.get(session_id))
            rows = self.connection.execute(
                """SELECT * FROM skills_session_events WHERE session_id=? AND sequence>?
                    ORDER BY sequence LIMIT ?""", (session_id, after_sequence, limit + 1),
            ).fetchall()
        return {
            "history_epoch": epoch, "session": session, "events": [event_view(row) for row in rows[:limit]],
            "next_after_sequence": rows[limit-1]["sequence"] if len(rows) > limit else None,
        }

    def history(self, limit=50, cursor=None):
        params = []
        where = ""
        if cursor is not None:
            try:
                decoded = json.loads(base64.b64decode(
                    cursor, altchars=b"-_", validate=True,
                ))
                if type(decoded) is not list or len(decoded) != 2:
                    raise ValueError
                date, session_id = decoded
                if not isinstance(date, str) or not isinstance(session_id, str):
                    raise ValueError
                datetime.fromisoformat(date)
                UUID(session_id)
            except (ValueError, TypeError, UnicodeError) as error:
                raise InvalidCursor("Invalid history cursor.") from error
            where = "WHERE (created_at, session_id) < (?, ?)"
            params.extend([date, session_id])
        rows = self.connection.execute(
            "SELECT * FROM skills_sessions " + where
            + " ORDER BY created_at DESC, session_id DESC LIMIT ?", [*params, limit + 1],
        ).fetchall()
        next_cursor = None
        if len(rows) > limit:
            last = rows[limit-1]
            next_cursor = base64.urlsafe_b64encode(canonical_json(
                [last["created_at"], last["session_id"]]
            ).encode()).decode()
        return {"sessions": [session_view(row) for row in rows[:limit]], "next_cursor": next_cursor}
