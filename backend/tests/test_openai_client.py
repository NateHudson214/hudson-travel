import asyncio
import json
from collections.abc import Callable
from typing import Any

import httpx
import pytest

from backend.app.advisor_contracts import (
    AdvisorProviderAuthenticationError,
    AdvisorProviderConfigurationError,
    AdvisorProviderHTTPError,
    AdvisorProviderModelUnavailableError,
    AdvisorProviderRateLimitError,
    AdvisorProviderResponseError,
    AdvisorProviderTransportError,
    GroundedAnswer,
    QueryProposal,
)
from backend.app.advisor_prompt import AdvisorPrompt
from backend.app.openai_client import (
    GROUNDED_ANSWER_MAX_OUTPUT_TOKENS,
    GROUNDED_ANSWER_TOOL_NAME,
    OPENAI_RESPONSES_URL,
    OPENAI_TIMEOUT_SECONDS,
    QUERY_PROPOSAL_MAX_OUTPUT_TOKENS,
    QUERY_TOOL_NAME,
    TOTAL_COST_PLACEHOLDER,
    generate_grounded_answer_openai,
    propose_hotel_query_openai,
)


FAKE_API_KEY = "fake-openai-key-for-tests"
FAKE_MODEL = "gpt-test-model"
FAKE_PROMPT = AdvisorPrompt(
    text=(
        "Use only saved_hotels, saved_hotel_searches, and demo_hotel_nights. "
        "Rates and availability are simulated demonstration data."
    ),
    version="sha256:test-prompt-version",
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
RECORDS = [
    {
        "hotel_id": "provider-hotel-1",
        "name": "Hotel State College",
        "total_cost_cents": 20000,
        "rooms_available": 7,
    }
]


def responses_tool_result(
    tool_name: str,
    arguments: object,
    *,
    status: str = "completed",
    output: object = None,
) -> dict[str, object]:
    if output is None:
        output = [
            {"type": "reasoning", "id": "reasoning-test", "summary": []},
            {
                "type": "function_call",
                "id": "function-test",
                "call_id": "call-test",
                "name": tool_name,
                "arguments": (
                    arguments
                    if isinstance(arguments, str)
                    else json.dumps(arguments)
                ),
            },
        ]
    return {"id": "response-test", "status": status, "output": output}


def proposal_payload() -> dict[str, object]:
    return responses_tool_result(
        QUERY_TOOL_NAME,
        {
            "sql": SQL,
            "parameters": [
                {"name": "check_in", "value": "2026-10-10"},
                {"name": "check_out", "value": "2026-10-12"},
            ],
        },
    )


def answer_payload(
    status: object = "answered",
    answer: object = "A grounded answer.",
    total_cost_cents: object = None,
) -> dict[str, object]:
    return responses_tool_result(
        GROUNDED_ANSWER_TOOL_NAME,
        {
            "status": status,
            "answer": answer,
            "total_cost_cents": total_cost_cents,
        },
    )


def run_proposal(
    handler: Callable[[httpx.Request], httpx.Response],
    *,
    api_key: str | None = FAKE_API_KEY,
) -> QueryProposal:
    async def run() -> QueryProposal:
        transport = httpx.MockTransport(handler)
        async with httpx.AsyncClient(transport=transport) as client:
            return await propose_hotel_query_openai(
                QUESTION,
                api_key_provider=lambda: api_key,
                model_provider=lambda: FAKE_MODEL,
                prompt_provider=lambda: FAKE_PROMPT,
                client=client,
            )

    return asyncio.run(run())


def run_answer(
    handler: Callable[[httpx.Request], httpx.Response],
    records: list[dict[str, Any]],
    *,
    api_key: str | None = FAKE_API_KEY,
) -> GroundedAnswer:
    async def run() -> GroundedAnswer:
        transport = httpx.MockTransport(handler)
        async with httpx.AsyncClient(transport=transport) as client:
            return await generate_grounded_answer_openai(
                QUESTION,
                SQL,
                PARAMETERS,
                records,
                api_key_provider=lambda: api_key,
                model_provider=lambda: FAKE_MODEL,
                prompt_provider=lambda: FAKE_PROMPT,
                client=client,
            )

    return asyncio.run(run())


def test_query_proposal_sends_exact_mocked_responses_request() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        assert str(request.url) == OPENAI_RESPONSES_URL
        assert request.headers["Authorization"] == f"Bearer {FAKE_API_KEY}"
        assert request.headers["Content-Type"] == "application/json"
        timeout = request.extensions["timeout"]
        assert timeout["connect"] == OPENAI_TIMEOUT_SECONDS
        assert timeout["read"] == OPENAI_TIMEOUT_SECONDS

        payload = json.loads(request.content)
        assert payload["model"] == FAKE_MODEL
        assert payload["store"] is False
        assert payload["reasoning"] == {"effort": "none"}
        assert payload["parallel_tool_calls"] is False
        assert payload["max_output_tokens"] == QUERY_PROPOSAL_MAX_OUTPUT_TOKENS
        assert payload["tool_choice"] == {
            "type": "function",
            "name": QUERY_TOOL_NAME,
        }
        assert payload["input"][1] == {"role": "user", "content": QUESTION}
        system_content = payload["input"][0]["content"]
        assert FAKE_PROMPT.text in system_content
        assert f"Prompt version: {FAKE_PROMPT.version}" in system_content
        tool = payload["tools"][0]
        assert tool["name"] == QUERY_TOOL_NAME
        assert tool["strict"] is True
        assert tool["parameters"]["additionalProperties"] is False
        item_schema = tool["parameters"]["properties"]["parameters"]["items"]
        assert item_schema["additionalProperties"] is False
        assert item_schema["required"] == ["name", "value"]
        assert FAKE_API_KEY.encode() not in request.content
        return httpx.Response(200, json=proposal_payload())

    assert run_proposal(handler) == QueryProposal(
        sql=SQL, parameters=PARAMETERS
    )


def test_missing_configuration_stops_before_http_request() -> None:
    def should_not_run(request: httpx.Request) -> httpx.Response:
        raise AssertionError("HTTP request must not run")

    with pytest.raises(AdvisorProviderConfigurationError):
        run_proposal(should_not_run, api_key=None)


@pytest.mark.parametrize(
    ("records", "status", "answer"),
    [
        (
            RECORDS,
            "answered",
            (
                "Hotel State College has simulated availability for "
                f"{TOTAL_COST_PLACEHOLDER}."
            ),
        ),
        ([], "no_matches", "No saved hotel matches the requested dates."),
        (
            RECORDS,
            "insufficient_data",
            "The saved simulated data does not include every requested night.",
        ),
    ],
)
def test_grounded_answer_request_and_all_supported_statuses(
    records: list[dict[str, Any]], status: str, answer: str
) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        payload = json.loads(request.content)
        assert payload["store"] is False
        assert payload["max_output_tokens"] == GROUNDED_ANSWER_MAX_OUTPUT_TOKENS
        assert payload["tool_choice"] == {
            "type": "function",
            "name": GROUNDED_ANSWER_TOOL_NAME,
        }
        tool = payload["tools"][0]
        assert tool["name"] == GROUNDED_ANSWER_TOOL_NAME
        assert tool["strict"] is True
        assert tool["parameters"]["required"] == [
            "status",
            "answer",
            "total_cost_cents",
        ]
        assert tool["parameters"]["properties"]["total_cost_cents"] == {
            "type": ["integer", "null"]
        }
        context = json.loads(payload["input"][1]["content"])
        assert context == {
            "question": QUESTION,
            "proposed_sql": SQL,
            "query_parameters": PARAMETERS,
            "retrieved_records": records,
        }
        assert "only the supplied retrieved records" in payload["input"][0][
            "content"
        ]
        assert FAKE_API_KEY.encode() not in request.content
        total_cost_cents = 20000 if status == "answered" else None
        return httpx.Response(
            200,
            json=answer_payload(status, answer, total_cost_cents),
        )

    assert run_answer(handler, records) == GroundedAnswer(
        status=status,
        answer=answer,
        total_cost_cents=(20000 if status == "answered" else None),
    )


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"status": "incomplete", "output": []},
        {"status": "completed", "output": "invalid"},
        responses_tool_result(QUERY_TOOL_NAME, {}, output=[]),
        responses_tool_result("wrong_tool", {}),
        responses_tool_result(QUERY_TOOL_NAME, "not-json"),
        responses_tool_result(QUERY_TOOL_NAME, {"sql": SQL}),
        responses_tool_result(
            QUERY_TOOL_NAME,
            {"sql": SQL, "parameters": [{"name": "x", "value": True}]},
        ),
        responses_tool_result(
            QUERY_TOOL_NAME,
            {
                "sql": SQL,
                "parameters": [
                    {"name": "x", "value": 1},
                    {"name": "x", "value": 2},
                ],
            },
        ),
    ],
)
def test_malformed_proposal_responses_are_rejected(
    payload: dict[str, object],
) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=payload)

    with pytest.raises(AdvisorProviderResponseError):
        run_proposal(handler)


@pytest.mark.parametrize(
    "payload",
    [
        answer_payload(status="unsupported"),
        answer_payload(answer=""),
        responses_tool_result(
            GROUNDED_ANSWER_TOOL_NAME,
            {
                "status": "answered",
                "answer": "Answer",
                "total_cost_cents": 20000,
                "extra": True,
            },
        ),
        answer_payload(total_cost_cents=True),
        answer_payload(total_cost_cents=-1),
    ],
)
def test_malformed_answer_responses_are_rejected(
    payload: dict[str, object],
) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=payload)

    with pytest.raises(AdvisorProviderResponseError):
        run_answer(handler, RECORDS)


@pytest.mark.parametrize(
    ("records", "status"),
    [([], "answered"), (RECORDS, "no_matches")],
)
def test_grounded_status_must_agree_with_record_presence(
    records: list[dict[str, Any]], status: str
) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=answer_payload(status, "Unsafe answer"))

    with pytest.raises(AdvisorProviderResponseError, match="inconsistent"):
        run_answer(handler, records)


@pytest.mark.parametrize(
    ("status_code", "body", "expected_error"),
    [
        (401, {}, AdvisorProviderAuthenticationError),
        (403, {}, AdvisorProviderAuthenticationError),
        (429, {}, AdvisorProviderRateLimitError),
        (404, {}, AdvisorProviderModelUnavailableError),
        (
            400,
            {"error": {"code": "model_not_found"}},
            AdvisorProviderModelUnavailableError,
        ),
        (400, {}, AdvisorProviderHTTPError),
        (500, {}, AdvisorProviderHTTPError),
    ],
)
def test_http_failures_are_distinct_and_sanitized(
    status_code: int,
    body: dict[str, object],
    expected_error: type[Exception],
) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            status_code,
            json={
                **body,
                "credential": FAKE_API_KEY,
                "url": OPENAI_RESPONSES_URL,
            },
        )

    with pytest.raises(expected_error) as captured_error:
        run_proposal(handler)

    error_text = str(captured_error.value)
    assert FAKE_API_KEY not in error_text
    assert "Bearer" not in error_text
    assert OPENAI_RESPONSES_URL not in error_text


@pytest.mark.parametrize("failure", ["timeout", "network"])
def test_transport_failures_are_sanitized(failure: str) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if failure == "timeout":
            raise httpx.ReadTimeout(
                f"Bearer {FAKE_API_KEY} at {OPENAI_RESPONSES_URL}",
                request=request,
            )
        raise httpx.ConnectError(
            f"Bearer {FAKE_API_KEY} at /private/database.sqlite3",
            request=request,
        )

    with pytest.raises(AdvisorProviderTransportError) as captured_error:
        run_proposal(handler)

    error_text = str(captured_error.value)
    assert FAKE_API_KEY not in error_text
    assert "Bearer" not in error_text
    assert OPENAI_RESPONSES_URL not in error_text
    assert "/private/database.sqlite3" not in error_text


@pytest.mark.parametrize(
    "response",
    [
        httpx.Response(200, content=b"not-json"),
        httpx.Response(200, content=b"null"),
        httpx.Response(200, json=[]),
    ],
)
def test_invalid_json_shapes_are_sanitized(response: httpx.Response) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return response

    with pytest.raises(AdvisorProviderResponseError) as captured_error:
        run_proposal(handler)

    assert FAKE_API_KEY not in str(captured_error.value)
    assert OPENAI_RESPONSES_URL not in str(captured_error.value)
