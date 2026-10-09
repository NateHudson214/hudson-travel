import json
from collections.abc import Callable
from typing import Any

import httpx

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
from .advisor_prompt import (
    AdvisorPrompt,
    AdvisorPromptError,
    load_hotel_assistant_prompt,
)
from .config import get_openai_api_key, get_openai_model


OPENAI_RESPONSES_URL = "https://api.openai.com/v1/responses"
OPENAI_TIMEOUT_SECONDS = 10.0
QUERY_PROPOSAL_MAX_OUTPUT_TOKENS = 600
GROUNDED_ANSWER_MAX_OUTPUT_TOKENS = 500
QUERY_TOOL_NAME = "propose_hotel_query"
GROUNDED_ANSWER_TOOL_NAME = "return_grounded_answer"
TOTAL_COST_PLACEHOLDER = "{{total_cost}}"


def _parameter_schema() -> dict[str, Any]:
    return {
        "type": "array",
        "description": "Named SQLite parameters as name/value pairs.",
        "items": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "name": {"type": "string"},
                "value": {"type": ["string", "number", "null"]},
            },
            "required": ["name", "value"],
        },
    }


def _query_tool() -> dict[str, Any]:
    return {
        "type": "function",
        "name": QUERY_TOOL_NAME,
        "description": (
            "Propose one bounded parameterized read-only SQLite query over "
            "the approved saved-hotel schema."
        ),
        "strict": True,
        "parameters": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "sql": {"type": "string"},
                "parameters": _parameter_schema(),
            },
            "required": ["sql", "parameters"],
        },
    }


def _grounded_answer_tool() -> dict[str, Any]:
    return {
        "type": "function",
        "name": GROUNDED_ANSWER_TOOL_NAME,
        "description": (
            "Return one status and a concise hotel answer grounded only in "
            "the supplied retrieved records."
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
                "total_cost_cents": {"type": ["integer", "null"]},
            },
            "required": ["status", "answer", "total_cost_cents"],
        },
    }


def _load_prompt(
    prompt_provider: Callable[[], AdvisorPrompt],
) -> AdvisorPrompt:
    try:
        return prompt_provider()
    except AdvisorPromptError:
        raise AdvisorProviderResponseError(
            "The hotel assistant prompt is unavailable."
        ) from None


def _safe_error_code(response: httpx.Response) -> str | None:
    try:
        payload = response.json()
    except ValueError:
        return None
    if not isinstance(payload, dict) or not isinstance(payload.get("error"), dict):
        return None
    code = payload["error"].get("code")
    return code if isinstance(code, str) else None


def _raise_for_status(response: httpx.Response) -> None:
    if 200 <= response.status_code < 300:
        return
    if response.status_code in (401, 403):
        raise AdvisorProviderAuthenticationError(
            "Provider authentication was rejected."
        )
    if response.status_code == 429:
        raise AdvisorProviderRateLimitError(
            "Provider quota or rate limit was reached."
        )
    if response.status_code == 404 or _safe_error_code(response) in {
        "model_not_found",
        "invalid_model",
        "model_not_available",
    }:
        raise AdvisorProviderModelUnavailableError(
            "The configured provider model is unavailable."
        )
    raise AdvisorProviderHTTPError("The provider could not complete the request.")


def _parse_json_response(response: httpx.Response) -> dict[str, Any]:
    try:
        payload = response.json()
    except ValueError:
        raise AdvisorProviderResponseError(
            "The provider returned an invalid response."
        ) from None
    if not isinstance(payload, dict):
        raise AdvisorProviderResponseError(
            "The provider returned an invalid response."
        )
    return payload


async def _send_response_request(
    payload: dict[str, Any],
    *,
    api_key: str,
    client: httpx.AsyncClient | None,
    transport: httpx.AsyncBaseTransport | None,
) -> dict[str, Any]:
    if client is not None and transport is not None:
        raise AdvisorProviderResponseError(
            "The provider client configuration is invalid."
        )
    owns_client = client is None
    http_client = client or httpx.AsyncClient(
        timeout=OPENAI_TIMEOUT_SECONDS,
        transport=transport,
    )
    try:
        try:
            response = await http_client.post(
                OPENAI_RESPONSES_URL,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=OPENAI_TIMEOUT_SECONDS,
            )
        except httpx.TimeoutException:
            raise AdvisorProviderTransportError(
                "The provider request timed out."
            ) from None
        except httpx.RequestError:
            raise AdvisorProviderTransportError(
                "The provider could not be reached."
            ) from None

        _raise_for_status(response)
        return _parse_json_response(response)
    finally:
        if owns_client:
            await http_client.aclose()


def _function_arguments(
    payload: dict[str, Any], expected_tool_name: str
) -> dict[str, Any]:
    if payload.get("status") != "completed":
        raise AdvisorProviderResponseError(
            "The provider returned an incomplete response."
        )
    output = payload.get("output")
    if not isinstance(output, list):
        raise AdvisorProviderResponseError(
            "The provider returned an invalid response."
        )
    calls = [
        item
        for item in output
        if isinstance(item, dict) and item.get("type") == "function_call"
    ]
    if len(calls) != 1 or calls[0].get("name") != expected_tool_name:
        raise AdvisorProviderResponseError(
            "The provider returned an invalid tool result."
        )
    raw_arguments = calls[0].get("arguments")
    if not isinstance(raw_arguments, str):
        raise AdvisorProviderResponseError(
            "The provider returned invalid tool arguments."
        )
    try:
        arguments = json.loads(raw_arguments)
    except (TypeError, ValueError):
        raise AdvisorProviderResponseError(
            "The provider returned invalid tool arguments."
        ) from None
    if not isinstance(arguments, dict):
        raise AdvisorProviderResponseError(
            "The provider returned invalid tool arguments."
        )
    return arguments


def _parse_query_proposal(payload: dict[str, Any]) -> QueryProposal:
    arguments = _function_arguments(payload, QUERY_TOOL_NAME)
    if set(arguments) != {"sql", "parameters"}:
        raise AdvisorProviderResponseError(
            "The provider returned invalid query arguments."
        )
    sql = arguments["sql"]
    parameter_items = arguments["parameters"]
    if not isinstance(sql, str) or not sql.strip() or not isinstance(
        parameter_items, list
    ):
        raise AdvisorProviderResponseError(
            "The provider returned invalid query arguments."
        )

    parameters: dict[str, QueryParameter] = {}
    for item in parameter_items:
        if not isinstance(item, dict) or set(item) != {"name", "value"}:
            raise AdvisorProviderResponseError(
                "The provider returned invalid query arguments."
            )
        name = item["name"]
        value = item["value"]
        if (
            not isinstance(name, str)
            or not name.strip()
            or name in parameters
            or isinstance(value, bool)
            or not isinstance(value, (str, int, float, type(None)))
        ):
            raise AdvisorProviderResponseError(
                "The provider returned invalid query arguments."
            )
        parameters[name] = value
    return QueryProposal(sql=sql.strip(), parameters=parameters)


def _parse_grounded_answer(payload: dict[str, Any]) -> GroundedAnswer:
    arguments = _function_arguments(payload, GROUNDED_ANSWER_TOOL_NAME)
    if set(arguments) != {"status", "answer", "total_cost_cents"}:
        raise AdvisorProviderResponseError(
            "The provider returned an invalid grounded answer."
        )
    answer_status = arguments["status"]
    answer = arguments["answer"]
    total_cost_cents = arguments["total_cost_cents"]
    if answer_status not in {
        "answered",
        "no_matches",
        "insufficient_data",
    } or not isinstance(answer, str) or not answer.strip() or (
        total_cost_cents is not None
        and (
            isinstance(total_cost_cents, bool)
            or not isinstance(total_cost_cents, int)
            or total_cost_cents < 0
        )
    ):
        raise AdvisorProviderResponseError(
            "The provider returned an invalid grounded answer."
        )
    return GroundedAnswer(
        status=answer_status,
        answer=answer.strip(),
        total_cost_cents=total_cost_cents,
    )


def _base_payload(
    *,
    model: str,
    prompt: AdvisorPrompt,
    stage_instructions: str,
    user_content: str,
    tool: dict[str, Any],
    tool_name: str,
    max_output_tokens: int,
    conversation_history: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    history = [
        {"role": item["role"], "content": item["content"]}
        for item in (conversation_history or [])
        if item.get("role") in {"user", "assistant"}
        and isinstance(item.get("content"), str)
    ]
    return {
        "model": model,
        "store": False,
        "reasoning": {"effort": "none"},
        "input": [
            {
                "role": "system",
                "content": (
                    f"{prompt.text}\n\nPrompt version: {prompt.version}\n\n"
                    f"Current stage: {stage_instructions}"
                ),
            },
            *history,
            {"role": "user", "content": user_content},
        ],
        "tools": [tool],
        "tool_choice": {"type": "function", "name": tool_name},
        "parallel_tool_calls": False,
        "max_output_tokens": max_output_tokens,
    }


async def propose_hotel_query_openai(
    question: str,
    *,
    api_key_provider: Callable[[], str | None] = get_openai_api_key,
    model_provider: Callable[[], str] = get_openai_model,
    prompt_provider: Callable[[], AdvisorPrompt] = load_hotel_assistant_prompt,
    client: httpx.AsyncClient | None = None,
    transport: httpx.AsyncBaseTransport | None = None,
    conversation_history: list[dict[str, str]] | None = None,
) -> QueryProposal:
    """Request an untrusted proposal without validating or executing it."""
    api_key = api_key_provider()
    if api_key is None:
        raise AdvisorProviderConfigurationError(
            "The hotel advisor provider is not configured."
        )
    prompt = _load_prompt(prompt_provider)
    payload = _base_payload(
        model=model_provider(),
        prompt=prompt,
        stage_instructions=(
            "Return exactly one propose_hotel_query function call for the "
            "user's question."
        ),
        user_content=question,
        tool=_query_tool(),
        tool_name=QUERY_TOOL_NAME,
        max_output_tokens=QUERY_PROPOSAL_MAX_OUTPUT_TOKENS,
        conversation_history=conversation_history,
    )
    response_payload = await _send_response_request(
        payload,
        api_key=api_key,
        client=client,
        transport=transport,
    )
    return _parse_query_proposal(response_payload)


async def generate_grounded_answer_openai(
    question: str,
    proposed_sql: str,
    query_parameters: dict[str, QueryParameter],
    retrieved_records: list[dict[str, Any]],
    *,
    api_key_provider: Callable[[], str | None] = get_openai_api_key,
    model_provider: Callable[[], str] = get_openai_model,
    prompt_provider: Callable[[], AdvisorPrompt] = load_hotel_assistant_prompt,
    client: httpx.AsyncClient | None = None,
    transport: httpx.AsyncBaseTransport | None = None,
    conversation_history: list[dict[str, str]] | None = None,
) -> GroundedAnswer:
    """Request an answer grounded only in already retrieved bounded records."""
    api_key = api_key_provider()
    if api_key is None:
        raise AdvisorProviderConfigurationError(
            "The hotel advisor provider is not configured."
        )
    prompt = _load_prompt(prompt_provider)
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
    payload = _base_payload(
        model=model_provider(),
        prompt=prompt,
        stage_instructions=(
            "Return exactly one return_grounded_answer function call. Use "
            "only the supplied retrieved records as factual evidence."
        ),
        user_content=grounded_context,
        tool=_grounded_answer_tool(),
        tool_name=GROUNDED_ANSWER_TOOL_NAME,
        max_output_tokens=GROUNDED_ANSWER_MAX_OUTPUT_TOKENS,
        conversation_history=conversation_history,
    )
    response_payload = await _send_response_request(
        payload,
        api_key=api_key,
        client=client,
        transport=transport,
    )
    grounded_answer = _parse_grounded_answer(response_payload)
    if (not retrieved_records and grounded_answer.status == "answered") or (
        retrieved_records and grounded_answer.status == "no_matches"
    ):
        raise AdvisorProviderResponseError(
            "The provider returned an inconsistent grounded answer."
        )
    return grounded_answer
