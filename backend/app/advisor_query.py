import json
import math
import re
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import TypeAlias

from .advisor_contracts import QueryParameter, QueryProposal


MAX_SQL_CHARACTERS = 4_000
MAX_PARAMETERS = 20
MAX_PARAMETER_NAME_CHARACTERS = 64
MAX_PARAMETER_TEXT_CHARACTERS = 500
MAX_RESULT_ROWS = 50
MAX_TEXT_CELL_CHARACTERS = 2_000
MAX_RESULT_BYTES = 100_000
PROGRESS_OPERATION_LIMIT = 100_000
PROGRESS_HANDLER_INTERVAL = 100

ResultScalar: TypeAlias = str | int | float | None

ALLOWED_COLUMNS = {
    "saved_hotels": {
        "hotel_id",
        "name",
        "address",
        "latitude",
        "longitude",
    },
    "saved_hotel_searches": {
        "hotel_id",
        "zip_code",
        "postcode",
        "country_code",
        "latitude",
        "longitude",
        "locality",
    },
    "demo_hotel_nights": {
        "hotel_id",
        "stay_date",
        "nightly_rate_cents",
        "rooms_available",
    },
}
ALLOWED_TABLES = frozenset(ALLOWED_COLUMNS)
ALLOWED_FUNCTIONS = frozenset(
    {"count", "sum", "min", "max", "round", "coalesce", "lower", "upper"}
)

PROHIBITED_KEYWORDS = frozenset(
    {
        "insert",
        "update",
        "delete",
        "replace",
        "upsert",
        "create",
        "alter",
        "drop",
        "vacuum",
        "reindex",
        "analyze",
        "pragma",
        "attach",
        "detach",
        "begin",
        "commit",
        "rollback",
        "savepoint",
        "release",
        "recursive",
        "union",
        "intersect",
        "except",
        "temporary",
        "temp",
        "load_extension",
    }
)

_PARAMETER_NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
_NAMED_PLACEHOLDER = re.compile(r"(?<!:):([A-Za-z_][A-Za-z0-9_]*)")
_POSITIONAL_PLACEHOLDER = re.compile(r"\?|[$@][A-Za-z_][A-Za-z0-9_]*")
_TABLE_REFERENCE = re.compile(
    r"\b(?:FROM|JOIN)\s+([A-Za-z_][A-Za-z0-9_]*)", re.IGNORECASE
)
_CTE_NAME = re.compile(
    r"(?:\bWITH|,)\s*([A-Za-z_][A-Za-z0-9_]*)\s+AS\s*\(",
    re.IGNORECASE,
)
_FINAL_LIMIT = re.compile(
    r"\bLIMIT\s+(:[A-Za-z_][A-Za-z0-9_]*|[0-9]+)"
    r"(?:\s+OFFSET\s+(:[A-Za-z_][A-Za-z0-9_]*|[0-9]+))?\s*$",
    re.IGNORECASE,
)


class AdvisorQueryRejectedError(Exception):
    """Raised before or during preparation when a proposal is not permitted."""


class AdvisorQueryExecutionError(Exception):
    """Raised when a permitted local query cannot be completed."""


class AdvisorQueryLimitError(Exception):
    """Raised when execution or results exceed a configured safety limit."""


class AdvisorQueryResultError(Exception):
    """Raised when SQLite returns data outside the safe response contract."""


@dataclass(frozen=True)
class ValidatedQuery:
    sql: str
    parameters: dict[str, QueryParameter]


def _reject() -> None:
    raise AdvisorQueryRejectedError("The proposed hotel query is not allowed.")


def _validate_parameters(
    parameters: dict[str, QueryParameter], placeholders: set[str]
) -> dict[str, QueryParameter]:
    if len(parameters) > MAX_PARAMETERS or set(parameters) != placeholders:
        _reject()

    validated: dict[str, QueryParameter] = {}
    for name, value in parameters.items():
        if (
            not isinstance(name, str)
            or len(name) > MAX_PARAMETER_NAME_CHARACTERS
            or _PARAMETER_NAME.fullmatch(name) is None
        ):
            _reject()
        if isinstance(value, bool):
            _reject()
        if value is None or isinstance(value, int):
            validated[name] = value
            continue
        if isinstance(value, float):
            if not math.isfinite(value):
                _reject()
            validated[name] = value
            continue
        if isinstance(value, str):
            if len(value) > MAX_PARAMETER_TEXT_CHARACTERS:
                _reject()
            validated[name] = value
            continue
        _reject()
    return validated


def _validate_limit(sql: str, parameters: dict[str, QueryParameter]) -> None:
    match = _FINAL_LIMIT.search(sql)
    if match is None:
        _reject()

    limit_expression = match.group(1)
    if limit_expression.startswith(":"):
        limit_value = parameters.get(limit_expression[1:])
    else:
        limit_value = int(limit_expression)
    if (
        isinstance(limit_value, bool)
        or not isinstance(limit_value, int)
        or not 1 <= limit_value <= MAX_RESULT_ROWS
    ):
        _reject()

    offset_expression = match.group(2)
    if offset_expression is None:
        return
    if offset_expression.startswith(":"):
        offset_value = parameters.get(offset_expression[1:])
    else:
        offset_value = int(offset_expression)
    if (
        isinstance(offset_value, bool)
        or not isinstance(offset_value, int)
        or offset_value < 0
    ):
        _reject()


def validate_query_proposal(proposal: QueryProposal) -> ValidatedQuery:
    """Validate shape and bounds before any SQLite connection is opened."""
    raw_sql = proposal.sql if isinstance(proposal.sql, str) else ""
    if len(raw_sql) > MAX_SQL_CHARACTERS:
        _reject()
    sql = raw_sql.strip()
    if not sql:
        _reject()
    if not re.match(r"^(?:SELECT|WITH)\b", sql, re.IGNORECASE):
        _reject()
    if any(token in sql for token in ("--", "/*", "*/", ";", "`", '"', "[", "]")):
        _reject()

    words = {word.lower() for word in re.findall(r"\b[A-Za-z_][A-Za-z0-9_]*\b", sql)}
    if words & PROHIBITED_KEYWORDS:
        _reject()
    if len(re.findall(r"\bJOIN\b", sql, re.IGNORECASE)) > 2:
        _reject()

    used_allowed_tables = {
        table
        for table in ALLOWED_TABLES
        if re.search(rf"\b{re.escape(table)}\b", sql, re.IGNORECASE)
    }
    if not used_allowed_tables:
        _reject()
    for table in used_allowed_tables:
        if len(re.findall(rf"\b{re.escape(table)}\b", sql, re.IGNORECASE)) > 1:
            _reject()

    cte_names = {name.lower() for name in _CTE_NAME.findall(sql)}
    table_references = {name.lower() for name in _TABLE_REFERENCE.findall(sql)}
    if not table_references or not table_references <= ALLOWED_TABLES | cte_names:
        _reject()
    if any(name.startswith("sqlite_") for name in table_references | cte_names):
        _reject()

    if _POSITIONAL_PLACEHOLDER.search(sql):
        _reject()
    placeholders = set(_NAMED_PLACEHOLDER.findall(sql))
    if not placeholders:
        _reject()
    validated_parameters = _validate_parameters(proposal.parameters, placeholders)
    _validate_limit(sql, validated_parameters)
    return ValidatedQuery(sql=sql, parameters=validated_parameters)


def _authorizer(
    action: int,
    argument_one: str | None,
    argument_two: str | None,
    database_name: str | None,
    trigger_name: str | None,
) -> int:
    del database_name, trigger_name
    if action == sqlite3.SQLITE_SELECT:
        return sqlite3.SQLITE_OK
    if action == sqlite3.SQLITE_READ:
        table = (argument_one or "").lower()
        column = (argument_two or "").lower()
        if table in ALLOWED_COLUMNS and (
            column in ALLOWED_COLUMNS[table] or column == ""
        ):
            return sqlite3.SQLITE_OK
        return sqlite3.SQLITE_DENY
    if action == sqlite3.SQLITE_FUNCTION:
        function_name = (argument_two or argument_one or "").lower()
        if function_name in ALLOWED_FUNCTIONS:
            return sqlite3.SQLITE_OK
    return sqlite3.SQLITE_DENY


def _safe_records(
    cursor: sqlite3.Cursor,
    rows: list[sqlite3.Row],
    *,
    max_text_characters: int,
    max_result_bytes: int,
) -> list[dict[str, ResultScalar]]:
    description = cursor.description
    if description is None:
        raise AdvisorQueryResultError(
            "The local hotel query returned invalid data."
        )
    columns = [column[0] for column in description]
    if any(not isinstance(column, str) or not column for column in columns):
        raise AdvisorQueryResultError(
            "The local hotel query returned invalid data."
        )
    if len(columns) != len(set(columns)):
        raise AdvisorQueryResultError(
            "The local hotel query returned invalid data."
        )

    records: list[dict[str, ResultScalar]] = []
    for row in rows:
        record: dict[str, ResultScalar] = {}
        for column, value in zip(columns, row, strict=True):
            if isinstance(value, bool):
                raise AdvisorQueryResultError(
                    "The local hotel query returned invalid data."
                )
            if value is None or isinstance(value, int):
                record[column] = value
            elif isinstance(value, float) and math.isfinite(value):
                record[column] = value
            elif isinstance(value, str) and len(value) <= max_text_characters:
                record[column] = value
            else:
                raise AdvisorQueryResultError(
                    "The local hotel query returned invalid data."
                )
        records.append(record)

    encoded = json.dumps(
        records, ensure_ascii=False, separators=(",", ":")
    ).encode("utf-8")
    if len(encoded) > max_result_bytes:
        raise AdvisorQueryLimitError(
            "The local hotel query exceeded safe limits."
        )
    return records


def execute_read_only_query(
    database_path: Path,
    proposal: QueryProposal,
    *,
    max_result_rows: int = MAX_RESULT_ROWS,
    max_text_characters: int = MAX_TEXT_CELL_CHARACTERS,
    max_result_bytes: int = MAX_RESULT_BYTES,
    progress_operation_limit: int = PROGRESS_OPERATION_LIMIT,
    progress_handler_interval: int = PROGRESS_HANDLER_INTERVAL,
) -> list[dict[str, ResultScalar]]:
    """Validate and execute one bounded query against an explicit database."""
    validated = validate_query_proposal(proposal)

    try:
        database_uri = f"{Path(database_path).resolve().as_uri()}?mode=ro"
        connection = sqlite3.connect(database_uri, uri=True)
    except (OSError, sqlite3.Error):
        raise AdvisorQueryExecutionError(
            "The local hotel query could not be completed."
        ) from None

    authorization_denied = False
    progress_interrupted = False
    progress_calls = 0

    def authorize(
        action: int,
        argument_one: str | None,
        argument_two: str | None,
        database_name: str | None,
        trigger_name: str | None,
    ) -> int:
        nonlocal authorization_denied
        decision = _authorizer(
            action,
            argument_one,
            argument_two,
            database_name,
            trigger_name,
        )
        if decision != sqlite3.SQLITE_OK:
            authorization_denied = True
        return decision

    def check_progress() -> int:
        nonlocal progress_calls, progress_interrupted
        progress_calls += 1
        if progress_calls * progress_handler_interval > progress_operation_limit:
            progress_interrupted = True
            return 1
        return 0

    try:
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA query_only = ON")
        connection.execute("PRAGMA trusted_schema = OFF")
        connection.set_authorizer(authorize)
        connection.set_progress_handler(
            check_progress, progress_handler_interval
        )
        try:
            cursor = connection.execute(validated.sql, validated.parameters)
            rows = cursor.fetchmany(max_result_rows + 1)
        except sqlite3.OperationalError:
            if authorization_denied:
                _reject()
            if progress_interrupted:
                raise AdvisorQueryLimitError(
                    "The local hotel query exceeded safe limits."
                ) from None
            _reject()
        except sqlite3.Error:
            raise AdvisorQueryExecutionError(
                "The local hotel query could not be completed."
            ) from None

        if len(rows) > max_result_rows:
            raise AdvisorQueryLimitError(
                "The local hotel query exceeded safe limits."
            )
        return _safe_records(
            cursor,
            rows,
            max_text_characters=max_text_characters,
            max_result_bytes=max_result_bytes,
        )
    finally:
        connection.close()
