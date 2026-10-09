import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .database import connect_database


MAX_HISTORY_MESSAGES = 12
MAX_CONVERSATIONS = 50
MAX_STORED_JSON_BYTES = 32_768


class AdvisorPersistenceError(Exception):
    """Raised when advisor history cannot be stored or read safely."""


class AdvisorConversationNotFoundError(Exception):
    """Raised when a requested advisor conversation does not exist."""


@dataclass(frozen=True)
class AdvisorRunStart:
    conversation_id: str
    user_message_id: str
    run_id: str
    history: list[dict[str, str]]


def _json_text(value: Any) -> str:
    try:
        encoded = json.dumps(
            value,
            ensure_ascii=True,
            separators=(",", ":"),
            allow_nan=False,
        )
    except (TypeError, ValueError):
        raise AdvisorPersistenceError("Advisor history is unavailable.") from None
    if len(encoded.encode("utf-8")) > MAX_STORED_JSON_BYTES:
        raise AdvisorPersistenceError("Advisor history exceeded safe limits.")
    return encoded


def _next_id(
    connection: sqlite3.Connection, *, metadata_key: str, prefix: str
) -> str:
    row = connection.execute(
        "SELECT value FROM app_metadata WHERE key = ?", (metadata_key,)
    ).fetchone()
    if row is None:
        raise AdvisorPersistenceError("Advisor history is unavailable.")
    try:
        number = int(row["value"])
    except (TypeError, ValueError):
        raise AdvisorPersistenceError("Advisor history is unavailable.") from None
    connection.execute(
        "UPDATE app_metadata SET value = ? WHERE key = ?",
        (str(number + 1), metadata_key),
    )
    return f"{prefix}{number:06d}"


def _history_rows(
    connection: sqlite3.Connection, conversation_id: str
) -> list[dict[str, str]]:
    rows = connection.execute(
        """
        SELECT role, content
        FROM advisor_messages
        WHERE conversation_id = ?
        ORDER BY sequence_number DESC
        LIMIT ?
        """,
        (conversation_id, MAX_HISTORY_MESSAGES),
    ).fetchall()
    return [dict(row) for row in reversed(rows)]


def start_advisor_run(
    database_path: Path,
    *,
    question: str,
    conversation_id: str | None,
    prompt_version: str,
    now: str,
) -> AdvisorRunStart:
    connection = connect_database(database_path)
    try:
        connection.execute("BEGIN IMMEDIATE")
        if conversation_id is None:
            conversation_id = _next_id(
                connection,
                metadata_key="next_advisor_conversation_number",
                prefix="C",
            )
            connection.execute(
                """
                INSERT INTO advisor_conversations (
                    conversation_id, created_at, updated_at
                ) VALUES (?, ?, ?)
                """,
                (conversation_id, now, now),
            )
        elif connection.execute(
            "SELECT 1 FROM advisor_conversations WHERE conversation_id = ?",
            (conversation_id,),
        ).fetchone() is None:
            raise AdvisorConversationNotFoundError(conversation_id)

        history = _history_rows(connection, conversation_id)
        sequence_number = connection.execute(
            """
            SELECT COALESCE(MAX(sequence_number), 0) + 1
            FROM advisor_messages
            WHERE conversation_id = ?
            """,
            (conversation_id,),
        ).fetchone()[0]
        user_message_id = _next_id(
            connection,
            metadata_key="next_advisor_message_number",
            prefix="M",
        )
        run_id = _next_id(
            connection,
            metadata_key="next_advisor_run_number",
            prefix="R",
        )
        connection.execute(
            """
            INSERT INTO advisor_messages (
                message_id, conversation_id, sequence_number,
                role, content, created_at
            ) VALUES (?, ?, ?, 'user', ?, ?)
            """,
            (user_message_id, conversation_id, sequence_number, question, now),
        )
        connection.execute(
            """
            INSERT INTO advisor_runs (
                run_id, conversation_id, user_message_id,
                prompt_version, normalized_question, status, created_at
            ) VALUES (?, ?, ?, ?, ?, 'pending', ?)
            """,
            (
                run_id,
                conversation_id,
                user_message_id,
                prompt_version,
                question,
                now,
            ),
        )
        connection.execute(
            """
            UPDATE advisor_conversations
            SET updated_at = ?
            WHERE conversation_id = ?
            """,
            (now, conversation_id),
        )
        connection.commit()
        return AdvisorRunStart(
            conversation_id=conversation_id,
            user_message_id=user_message_id,
            run_id=run_id,
            history=history,
        )
    except AdvisorConversationNotFoundError:
        connection.rollback()
        raise
    except AdvisorPersistenceError:
        connection.rollback()
        raise
    except (OSError, sqlite3.Error):
        connection.rollback()
        raise AdvisorPersistenceError("Advisor history is unavailable.") from None
    finally:
        connection.close()


def record_advisor_proposal(
    database_path: Path,
    run_id: str,
    *,
    proposed_sql: str,
    query_parameters: dict[str, Any],
) -> None:
    _update_run(
        database_path,
        run_id,
        """
        UPDATE advisor_runs
        SET proposed_sql = ?, query_parameters_json = ?
        WHERE run_id = ? AND status = 'pending'
        """,
        (proposed_sql, _json_text(query_parameters), run_id),
    )


def record_advisor_retrieval(
    database_path: Path,
    run_id: str,
    *,
    executed_sql: str,
    query_parameters: dict[str, Any],
    retrieved_records: list[dict[str, Any]],
) -> None:
    _update_run(
        database_path,
        run_id,
        """
        UPDATE advisor_runs
        SET executed_sql = ?, query_parameters_json = ?,
            retrieved_records_json = ?
        WHERE run_id = ? AND status = 'pending'
        """,
        (
            executed_sql,
            _json_text(query_parameters),
            _json_text(retrieved_records),
            run_id,
        ),
    )


def _update_run(
    database_path: Path,
    run_id: str,
    sql: str,
    parameters: tuple[Any, ...],
) -> None:
    connection = connect_database(database_path)
    try:
        connection.execute("BEGIN IMMEDIATE")
        result = connection.execute(sql, parameters)
        if result.rowcount != 1:
            raise AdvisorPersistenceError("Advisor history is unavailable.")
        connection.commit()
    except AdvisorPersistenceError:
        connection.rollback()
        raise
    except (OSError, sqlite3.Error):
        connection.rollback()
        raise AdvisorPersistenceError("Advisor history is unavailable.") from None
    finally:
        connection.close()


def complete_advisor_run(
    database_path: Path,
    run_id: str,
    *,
    answer: str,
    result_status: str,
    now: str,
) -> str:
    connection = connect_database(database_path)
    try:
        connection.execute("BEGIN IMMEDIATE")
        run = connection.execute(
            """
            SELECT conversation_id
            FROM advisor_runs
            WHERE run_id = ? AND status = 'pending'
            """,
            (run_id,),
        ).fetchone()
        if run is None:
            raise AdvisorPersistenceError("Advisor history is unavailable.")
        message_id = _next_id(
            connection,
            metadata_key="next_advisor_message_number",
            prefix="M",
        )
        sequence_number = connection.execute(
            """
            SELECT COALESCE(MAX(sequence_number), 0) + 1
            FROM advisor_messages
            WHERE conversation_id = ?
            """,
            (run["conversation_id"],),
        ).fetchone()[0]
        connection.execute(
            """
            INSERT INTO advisor_messages (
                message_id, conversation_id, sequence_number,
                role, content, created_at
            ) VALUES (?, ?, ?, 'assistant', ?, ?)
            """,
            (message_id, run["conversation_id"], sequence_number, answer, now),
        )
        connection.execute(
            """
            UPDATE advisor_runs
            SET assistant_message_id = ?, status = 'completed',
                result_status = ?, completed_at = ?
            WHERE run_id = ? AND status = 'pending'
            """,
            (message_id, result_status, now, run_id),
        )
        connection.execute(
            """
            UPDATE advisor_conversations SET updated_at = ?
            WHERE conversation_id = ?
            """,
            (now, run["conversation_id"]),
        )
        connection.commit()
        return message_id
    except AdvisorPersistenceError:
        connection.rollback()
        raise
    except (OSError, sqlite3.Error):
        connection.rollback()
        raise AdvisorPersistenceError("Advisor history is unavailable.") from None
    finally:
        connection.close()


def fail_advisor_run(
    database_path: Path,
    run_id: str,
    *,
    error_category: str,
    error_message: str,
    now: str,
) -> None:
    connection = connect_database(database_path)
    try:
        connection.execute("BEGIN IMMEDIATE")
        result = connection.execute(
            """
            UPDATE advisor_runs
            SET status = 'failed', error_category = ?, error_message = ?,
                completed_at = ?
            WHERE run_id = ? AND status = 'pending'
            """,
            (error_category, error_message, now, run_id),
        )
        if result.rowcount != 1:
            raise AdvisorPersistenceError("Advisor history is unavailable.")
        run = connection.execute(
            "SELECT conversation_id FROM advisor_runs WHERE run_id = ?",
            (run_id,),
        ).fetchone()
        connection.execute(
            """
            UPDATE advisor_conversations SET updated_at = ?
            WHERE conversation_id = ?
            """,
            (now, run["conversation_id"]),
        )
        connection.commit()
    except AdvisorPersistenceError:
        connection.rollback()
        raise
    except (OSError, sqlite3.Error):
        connection.rollback()
        raise AdvisorPersistenceError("Advisor history is unavailable.") from None
    finally:
        connection.close()


def list_advisor_conversations(database_path: Path) -> list[dict[str, Any]]:
    connection = connect_database(database_path)
    try:
        rows = connection.execute(
            """
            SELECT
                c.conversation_id,
                c.created_at,
                c.updated_at,
                COUNT(m.message_id) AS message_count,
                (
                    SELECT content FROM advisor_messages AS latest
                    WHERE latest.conversation_id = c.conversation_id
                    ORDER BY latest.sequence_number DESC LIMIT 1
                ) AS latest_message
            FROM advisor_conversations AS c
            LEFT JOIN advisor_messages AS m
                ON m.conversation_id = c.conversation_id
            GROUP BY c.conversation_id, c.created_at, c.updated_at
            ORDER BY c.updated_at DESC, c.conversation_id DESC
            LIMIT ?
            """,
            (MAX_CONVERSATIONS,),
        ).fetchall()
        return [dict(row) for row in rows]
    except (OSError, sqlite3.Error):
        raise AdvisorPersistenceError("Advisor history is unavailable.") from None
    finally:
        connection.close()


def get_advisor_conversation(
    database_path: Path, conversation_id: str
) -> dict[str, Any]:
    connection = connect_database(database_path)
    try:
        conversation = connection.execute(
            """
            SELECT conversation_id, created_at, updated_at
            FROM advisor_conversations WHERE conversation_id = ?
            """,
            (conversation_id,),
        ).fetchone()
        if conversation is None:
            raise AdvisorConversationNotFoundError(conversation_id)
        messages = connection.execute(
            """
            SELECT message_id, role, content, created_at
            FROM advisor_messages
            WHERE conversation_id = ?
            ORDER BY sequence_number DESC
            LIMIT ?
            """,
            (conversation_id, MAX_HISTORY_MESSAGES),
        ).fetchall()
        completed_run = connection.execute(
            """
            SELECT
                result_status AS status,
                proposed_sql,
                query_parameters_json,
                retrieved_records_json,
                run_id,
                prompt_version
            FROM advisor_runs
            WHERE conversation_id = ?
              AND status = 'completed'
              AND result_status IN ('answered', 'no_matches', 'insufficient_data')
              AND proposed_sql IS NOT NULL
              AND query_parameters_json IS NOT NULL
              AND retrieved_records_json IS NOT NULL
            ORDER BY completed_at DESC, run_id DESC
            LIMIT 1
            """,
            (conversation_id,),
        ).fetchone()
        latest_completed_run = None
        if completed_run is not None:
            try:
                query_parameters = json.loads(
                    completed_run["query_parameters_json"]
                )
                retrieved_records = json.loads(
                    completed_run["retrieved_records_json"]
                )
            except (TypeError, json.JSONDecodeError):
                raise AdvisorPersistenceError(
                    "Advisor history is unavailable."
                ) from None
            if not isinstance(query_parameters, dict) or not isinstance(
                retrieved_records, list
            ):
                raise AdvisorPersistenceError(
                    "Advisor history is unavailable."
                )
            latest_completed_run = {
                "status": completed_run["status"],
                "proposed_sql": completed_run["proposed_sql"],
                "query_parameters": query_parameters,
                "retrieved_records": retrieved_records,
                "run_id": completed_run["run_id"],
                "prompt_version": completed_run["prompt_version"],
            }
        return {
            **dict(conversation),
            "messages": [dict(row) for row in reversed(messages)],
            "latest_completed_run": latest_completed_run,
        }
    except AdvisorConversationNotFoundError:
        raise
    except (OSError, sqlite3.Error):
        raise AdvisorPersistenceError("Advisor history is unavailable.") from None
    finally:
        connection.close()
