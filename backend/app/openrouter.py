import json
from collections.abc import Callable
from typing import Any

import httpx

from .config import get_openrouter_api_key, get_openrouter_model
from .advisor_contracts import (
    AdvisorProviderAuthenticationError,
    AdvisorProviderConfigurationError,
    AdvisorProviderHTTPError,
    AdvisorProviderModelUnavailableError,
    AdvisorProviderRateLimitError,
    AdvisorProviderResponseError,
    AdvisorProviderTransportError,
    GroundedAnswer,
    QueryParameter,
    QueryProposal,
)


OPENROUTER_CHAT_COMPLETIONS_URL = (
    "https://openrouter.ai/api/v1/chat/completions"
)
OPENROUTER_TIMEOUT_SECONDS = 10.0
QUERY_PROPOSAL_MAX_TOKENS = 600
GROUNDED_ANSWER_MAX_TOKENS = 500
QUERY_TOOL_NAME = "propose_hotel_query"
GROUNDED_ANSWER_TOOL_NAME = "return_grounded_answer"

class OpenRouterConfigurationError(AdvisorProviderConfigurationError):
    """Raised when the backend-only OpenRouter key is unavailable."""


class OpenRouterAuthenticationError(AdvisorProviderAuthenticationError):
    """Raised when OpenRouter rejects backend authentication."""


class OpenRouterRateLimitError(AdvisorProviderRateLimitError):
    """Raised when OpenRouter rejects a request because of quota or rate limits."""


class OpenRouterModelUnavailableError(AdvisorProviderModelUnavailableError):
    """Raised when the configured model is not available through OpenRouter."""


class OpenRouterTransportError(AdvisorProviderTransportError):
    """Raised when a timeout or network failure prevents an OpenRouter response."""


class OpenRouterProviderError(AdvisorProviderHTTPError):
    """Raised for other unsuccessful OpenRouter HTTP responses."""


class OpenRouterResponseError(AdvisorProviderResponseError):
    """Raised when OpenRouter returns a malformed or unusable response."""


QUERY_PROPOSAL_SYSTEM_PROMPT = """You propose one SQLite query for Hudson Travel.
Use only this schema:
saved_hotels(hotel_id, name, address, latitude, longitude)
saved_hotel_searches(hotel_id, zip_code, postcode, country_code, latitude, longitude, locality)
demo_hotel_nights(hotel_id, stay_date, nightly_rate_cents, rooms_available)

Rules:
- Return exactly one propose_hotel_query tool call.
- Propose one parameterized, read-only SELECT, optionally preceded by a non-recursive WITH.
- Use named placeholders for every question-derived value and return those values in parameters.
- Do not use comments, semicolons, multiple statements, PRAGMA, ATTACH, transactions, writes, schema changes, recursive CTEs, compound queries, or unknown tables.
- Limit results to at most 50 rows.
- A stay includes check-in and excludes checkout.
- Availability requires every requested night to exist with rooms_available greater than zero.
- Sum nightly_rate_cents only across the requested nights.
- Missing nights mean insufficient data; never invent a rate, room, date, or hotel.
"""

GROUNDED_ANSWER_SYSTEM_PROMPT = """Answer the hotel question using only the supplied retrieved records.
The nightly rates and availability are simulated demonstration data, and the answer must say so.
If the records are empty, do not match the question, or omit a required night or value, state that there is no match or insufficient data.
Do not invent hotels, dates, rates, rooms, availability, bookings, or facts outside the supplied records.
Return exactly one return_grounded_answer tool call. Use answered only when nonempty records support the answer, no_matches only for an empty record list, and insufficient_data when required data is missing. Give a concise, actionable answer.
"""


def _query_tool() -> dict[str, Any]:
    return {
        "type": "function",
        "function": {
            "name": QUERY_TOOL_NAME,
            "description": (
                "Propose one parameterized read-only query over the approved "
                "saved-hotel schema."
            ),
            "strict": True,
            "parameters": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "sql": {"type": "string"},
                    "parameters": {
                        "type": "object",
                        "additionalProperties": {
                            "type": ["string", "number", "null"]
                        },
                    },
                },
                "required": ["sql", "parameters"],
            },
        },
    }


def _grounded_answer_tool() -> dict[str, Any]:
    return {
        "type": "function",
        "function": {
            "name": GROUNDED_ANSWER_TOOL_NAME,
            "description": (
                "Return one grounded hotel-advisor status and answer based "
                "only on the supplied retrieved records."
            ),
            "strict": True,
            "parameters": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "status": {
                        "type": "string",
                        "enum": [
                            "answered",
                            "no_matches",
                            "insufficient_data",
                        ],
                    },
                    "answer": {"type": "string"},
                },
                "required": ["status", "answer"],
            },
        },
    }


def _parse_json_response(response: httpx.Response) -> dict[str, Any]:
    try:
        payload = response.json()
    except ValueError:
        raise OpenRouterResponseError(
            "OpenRouter returned an invalid response."
        ) from None
    if not isinstance(payload, dict):
        raise OpenRouterResponseError("OpenRouter returned an invalid response.")
    return payload


def _raise_for_status(response: httpx.Response) -> None:
    if 200 <= response.status_code < 300:
        return
    if response.status_code in (401, 403):
        raise OpenRouterAuthenticationError(
            "OpenRouter authentication was rejected."
        )
    if response.status_code == 429:
        raise OpenRouterRateLimitError(
            "OpenRouter quota or rate limit was reached."
        )
    if response.status_code == 404:
        raise OpenRouterModelUnavailableError(
            "The configured OpenRouter model is unavailable."
        )
    raise OpenRouterProviderError(
        "OpenRouter could not complete the request."
    )


async def _send_chat_request(
    payload: dict[str, Any],
    *,
    api_key: str,
    client: httpx.AsyncClient | None,
) -> dict[str, Any]:
    owns_client = client is None
    http_client = client or httpx.AsyncClient(timeout=OPENROUTER_TIMEOUT_SECONDS)
    try:
        try:
            response = await http_client.post(
                OPENROUTER_CHAT_COMPLETIONS_URL,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=OPENROUTER_TIMEOUT_SECONDS,
            )
        except httpx.TimeoutException:
            raise OpenRouterTransportError(
                "OpenRouter request timed out."
            ) from None
        except httpx.RequestError:
            raise OpenRouterTransportError(
                "OpenRouter could not be reached."
            ) from None

        _raise_for_status(response)
        return _parse_json_response(response)
    finally:
        if owns_client:
            await http_client.aclose()


def _message_from_payload(payload: dict[str, Any]) -> dict[str, Any]:
    choices = payload.get("choices")
    if not isinstance(choices, list) or len(choices) != 1:
        raise OpenRouterResponseError("OpenRouter returned an invalid response.")
    choice = choices[0]
    if not isinstance(choice, dict) or not isinstance(choice.get("message"), dict):
        raise OpenRouterResponseError("OpenRouter returned an invalid response.")
    return choice["message"]


def _parse_query_proposal(payload: dict[str, Any]) -> QueryProposal:
    message = _message_from_payload(payload)
    tool_calls = message.get("tool_calls")
    if not isinstance(tool_calls, list) or len(tool_calls) != 1:
        raise OpenRouterResponseError(
            "OpenRouter did not return one valid query proposal."
        )

    tool_call = tool_calls[0]
    if not isinstance(tool_call, dict) or tool_call.get("type") != "function":
        raise OpenRouterResponseError(
            "OpenRouter did not return one valid query proposal."
        )
    function = tool_call.get("function")
    if not isinstance(function, dict) or function.get("name") != QUERY_TOOL_NAME:
        raise OpenRouterResponseError(
            "OpenRouter did not return one valid query proposal."
        )
    arguments = function.get("arguments")
    if not isinstance(arguments, str):
        raise OpenRouterResponseError(
            "OpenRouter returned invalid query arguments."
        )

    try:
        parsed_arguments = json.loads(arguments)
    except (TypeError, ValueError):
        raise OpenRouterResponseError(
            "OpenRouter returned invalid query arguments."
        ) from None
    if not isinstance(parsed_arguments, dict) or set(parsed_arguments) != {
        "sql",
        "parameters",
    }:
        raise OpenRouterResponseError(
            "OpenRouter returned invalid query arguments."
        )

    sql = parsed_arguments["sql"]
    parameters = parsed_arguments["parameters"]
    if not isinstance(sql, str) or not sql.strip() or not isinstance(parameters, dict):
        raise OpenRouterResponseError(
            "OpenRouter returned invalid query arguments."
        )

    normalized_parameters: dict[str, QueryParameter] = {}
    for name, value in parameters.items():
        if not isinstance(name, str) or not name.strip():
            raise OpenRouterResponseError(
                "OpenRouter returned invalid query arguments."
            )
        if isinstance(value, bool) or not isinstance(
            value, (str, int, float, type(None))
        ):
            raise OpenRouterResponseError(
                "OpenRouter returned invalid query arguments."
            )
        normalized_parameters[name] = value

    return QueryProposal(sql=sql.strip(), parameters=normalized_parameters)


async def propose_hotel_query(
    question: str,
    *,
    api_key_provider: Callable[[], str | None] = get_openrouter_api_key,
    model_provider: Callable[[], str] = get_openrouter_model,
    client: httpx.AsyncClient | None = None,
) -> QueryProposal:
    """Ask OpenRouter for an untrusted query proposal without executing it."""
    api_key = api_key_provider()
    if api_key is None:
        raise OpenRouterConfigurationError("OpenRouter is not configured.")

    payload = {
        "model": model_provider(),
        "messages": [
            {"role": "system", "content": QUERY_PROPOSAL_SYSTEM_PROMPT},
            {"role": "user", "content": question},
        ],
        "tools": [_query_tool()],
        "tool_choice": {
            "type": "function",
            "function": {"name": QUERY_TOOL_NAME},
        },
        "parallel_tool_calls": False,
        "temperature": 0,
        "max_tokens": QUERY_PROPOSAL_MAX_TOKENS,
        "stream": False,
    }
    response_payload = await _send_chat_request(
        payload, api_key=api_key, client=client
    )
    return _parse_query_proposal(response_payload)


def _parse_grounded_answer(payload: dict[str, Any]) -> GroundedAnswer:
    message = _message_from_payload(payload)
    tool_calls = message.get("tool_calls")
    if not isinstance(tool_calls, list) or len(tool_calls) != 1:
        raise OpenRouterResponseError(
            "OpenRouter returned an invalid grounded answer."
        )

    tool_call = tool_calls[0]
    if not isinstance(tool_call, dict) or tool_call.get("type") != "function":
        raise OpenRouterResponseError(
            "OpenRouter returned an invalid grounded answer."
        )
    function = tool_call.get("function")
    if (
        not isinstance(function, dict)
        or function.get("name") != GROUNDED_ANSWER_TOOL_NAME
        or not isinstance(function.get("arguments"), str)
    ):
        raise OpenRouterResponseError(
            "OpenRouter returned an invalid grounded answer."
        )

    try:
        arguments = json.loads(function["arguments"])
    except (TypeError, ValueError):
        raise OpenRouterResponseError(
            "OpenRouter returned an invalid grounded answer."
        ) from None
    if not isinstance(arguments, dict) or set(arguments) != {
        "status",
        "answer",
    }:
        raise OpenRouterResponseError(
            "OpenRouter returned an invalid grounded answer."
        )

    answer_status = arguments["status"]
    answer = arguments["answer"]
    if answer_status not in {
        "answered",
        "no_matches",
        "insufficient_data",
    } or not isinstance(answer, str) or not answer.strip():
        raise OpenRouterResponseError(
            "OpenRouter returned an invalid grounded answer."
        )
    return GroundedAnswer(status=answer_status, answer=answer.strip())


async def generate_grounded_answer(
    question: str,
    proposed_sql: str,
    query_parameters: dict[str, QueryParameter],
    retrieved_records: list[dict[str, Any]],
    *,
    api_key_provider: Callable[[], str | None] = get_openrouter_api_key,
    model_provider: Callable[[], str] = get_openrouter_model,
    client: httpx.AsyncClient | None = None,
) -> GroundedAnswer:
    """Ask OpenRouter to answer only from already retrieved, bounded records."""
    api_key = api_key_provider()
    if api_key is None:
        raise OpenRouterConfigurationError("OpenRouter is not configured.")

    grounded_context = json.dumps(
        {
            "question": question,
            "proposed_sql": proposed_sql,
            "query_parameters": query_parameters,
            "retrieved_records": retrieved_records,
        },
        ensure_ascii=True,
        separators=(",", ":"),
    )
    payload = {
        "model": model_provider(),
        "messages": [
            {"role": "system", "content": GROUNDED_ANSWER_SYSTEM_PROMPT},
            {"role": "user", "content": grounded_context},
        ],
        "tools": [_grounded_answer_tool()],
        "tool_choice": {
            "type": "function",
            "function": {"name": GROUNDED_ANSWER_TOOL_NAME},
        },
        "parallel_tool_calls": False,
        "temperature": 0,
        "max_tokens": GROUNDED_ANSWER_MAX_TOKENS,
        "stream": False,
    }
    response_payload = await _send_chat_request(
        payload, api_key=api_key, client=client
    )
    grounded_answer = _parse_grounded_answer(response_payload)
    if (not retrieved_records and grounded_answer.status == "answered") or (
        retrieved_records and grounded_answer.status == "no_matches"
    ):
        raise OpenRouterResponseError(
            "OpenRouter returned an inconsistent grounded answer."
        )
    return grounded_answer
