import asyncio
import json
from collections.abc import Callable
from typing import Any

import httpx
import pytest

from backend.app.openrouter import (
    GROUNDED_ANSWER_TOOL_NAME,
    GROUNDED_ANSWER_MAX_TOKENS,
    OPENROUTER_CHAT_COMPLETIONS_URL,
    OPENROUTER_TIMEOUT_SECONDS,
    QUERY_PROPOSAL_MAX_TOKENS,
    QUERY_TOOL_NAME,
    OpenRouterAuthenticationError,
    OpenRouterConfigurationError,
    OpenRouterModelUnavailableError,
    OpenRouterProviderError,
    OpenRouterRateLimitError,
    OpenRouterResponseError,
    OpenRouterTransportError,
    GroundedAnswer,
    QueryProposal,
    generate_grounded_answer,
    propose_hotel_query,
)


FAKE_API_KEY = "fake-openrouter-key-for-tests"
FAKE_MODEL = "test-provider/test-model"
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


def proposal_response(
    arguments: object = None,
    *,
    tool_name: str = QUERY_TOOL_NAME,
    tool_calls: object = None,
) -> dict[str, object]:
    if arguments is None:
        arguments = json.dumps({"sql": SQL, "parameters": PARAMETERS})
    if tool_calls is None:
        tool_calls = [
            {
                "id": "call-test",
                "type": "function",
                "function": {"name": tool_name, "arguments": arguments},
            }
        ]
    return {"choices": [{"message": {"tool_calls": tool_calls}}]}


def answer_response(
    status: object = "answered",
    answer: object = "A grounded answer.",
    *,
    tool_name: str = GROUNDED_ANSWER_TOOL_NAME,
    tool_calls: object = None,
) -> dict[str, object]:
    if tool_calls is None:
        tool_calls = [
            {
                "id": "call-answer-test",
                "type": "function",
                "function": {
                    "name": tool_name,
                    "arguments": json.dumps(
                        {"status": status, "answer": answer}
                    ),
                },
            }
        ]
    return {"choices": [{"message": {"tool_calls": tool_calls}}]}


def run_proposal(
    handler: Callable[[httpx.Request], httpx.Response],
    *,
    api_key: str | None = FAKE_API_KEY,
) -> QueryProposal:
    async def run() -> QueryProposal:
        transport = httpx.MockTransport(handler)
        async with httpx.AsyncClient(transport=transport) as client:
            return await propose_hotel_query(
                QUESTION,
                api_key_provider=lambda: api_key,
                model_provider=lambda: FAKE_MODEL,
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
            return await generate_grounded_answer(
                QUESTION,
                SQL,
                PARAMETERS,
                records,
                api_key_provider=lambda: api_key,
                model_provider=lambda: FAKE_MODEL,
                client=client,
            )

    return asyncio.run(run())


def test_query_proposal_sends_exact_safe_mocked_request() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        assert str(request.url) == OPENROUTER_CHAT_COMPLETIONS_URL
        assert request.headers["Authorization"] == f"Bearer {FAKE_API_KEY}"
        assert request.headers["Content-Type"] == "application/json"
        timeout = request.extensions["timeout"]
        assert timeout["connect"] == OPENROUTER_TIMEOUT_SECONDS
        assert timeout["read"] == OPENROUTER_TIMEOUT_SECONDS

        payload = json.loads(request.content)
        assert payload["model"] == FAKE_MODEL
        assert payload["temperature"] == 0
        assert payload["max_tokens"] == QUERY_PROPOSAL_MAX_TOKENS
        assert payload["stream"] is False
        assert payload["parallel_tool_calls"] is False
        assert payload["tool_choice"] == {
            "type": "function",
            "function": {"name": QUERY_TOOL_NAME},
        }
        tool = payload["tools"][0]["function"]
        assert tool["name"] == QUERY_TOOL_NAME
        assert tool["strict"] is True
        assert tool["parameters"]["required"] == ["sql", "parameters"]
        assert tool["parameters"]["additionalProperties"] is False

        system_prompt = payload["messages"][0]["content"]
        assert "saved_hotels(" in system_prompt
        assert "saved_hotel_searches(" in system_prompt
        assert "demo_hotel_nights(" in system_prompt
        assert "bookings(" not in system_prompt
        assert "users(" not in system_prompt
        assert "trips(" not in system_prompt
        assert "GEOAPIFY" not in system_prompt
        assert payload["messages"][1] == {"role": "user", "content": QUESTION}
        assert FAKE_API_KEY.encode() not in request.content

        return httpx.Response(200, json=proposal_response())

    assert run_proposal(handler) == QueryProposal(
        sql=SQL, parameters=PARAMETERS
    )


def test_missing_configuration_prevents_query_proposal_request() -> None:
    request_was_made = False

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal request_was_made
        request_was_made = True
        return httpx.Response(200, json=proposal_response())

    with pytest.raises(OpenRouterConfigurationError, match="not configured"):
        run_proposal(handler, api_key=None)

    assert request_was_made is False


def test_missing_configuration_prevents_grounded_answer_request() -> None:
    request_was_made = False

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal request_was_made
        request_was_made = True
        return httpx.Response(200, json=answer_response(answer="unused"))

    with pytest.raises(OpenRouterConfigurationError, match="not configured"):
        run_answer(handler, [], api_key=None)

    assert request_was_made is False


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"choices": []},
        {"choices": [{"message": {}}]},
        proposal_response(tool_calls=[]),
        proposal_response(
            tool_calls=[
                {
                    "type": "function",
                    "function": {
                        "name": QUERY_TOOL_NAME,
                        "arguments": json.dumps(
                            {"sql": SQL, "parameters": PARAMETERS}
                        ),
                    },
                },
                {
                    "type": "function",
                    "function": {
                        "name": QUERY_TOOL_NAME,
                        "arguments": json.dumps(
                            {"sql": SQL, "parameters": PARAMETERS}
                        ),
                    },
                },
            ]
        ),
        proposal_response(tool_name="wrong_tool"),
        proposal_response(
            tool_calls=[
                {
                    "type": "not-function",
                    "function": {
                        "name": QUERY_TOOL_NAME,
                        "arguments": "{}",
                    },
                }
            ]
        ),
    ],
)
def test_query_proposal_rejects_missing_duplicate_or_wrong_tool_calls(
    payload: dict[str, object],
) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=payload)

    with pytest.raises(OpenRouterResponseError):
        run_proposal(handler)


@pytest.mark.parametrize(
    "arguments",
    [
        "not-json",
        "[]",
        json.dumps({"sql": SQL}),
        json.dumps({"sql": SQL, "parameters": PARAMETERS, "extra": True}),
        json.dumps({"sql": "   ", "parameters": PARAMETERS}),
        json.dumps({"sql": SQL, "parameters": []}),
        json.dumps({"sql": SQL, "parameters": {"active": True}}),
        json.dumps({"sql": SQL, "parameters": {"nested": {"value": 1}}}),
    ],
)
def test_query_proposal_rejects_invalid_tool_arguments(arguments: str) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=proposal_response(arguments))

    with pytest.raises(
        OpenRouterResponseError, match="invalid query arguments"
    ):
        run_proposal(handler)


def test_grounded_answer_sends_only_expected_context_and_instructions() -> None:
    records = [
        {
            "hotel_id": "provider-hotel-1",
            "name": "Hotel State College",
            "total_cents": 22550,
            "rooms_available": 7,
        }
    ]
    expected_answer = (
        "Hotel State College has simulated availability for the requested "
        "nights at a simulated total of $225.50."
    )

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        assert str(request.url) == OPENROUTER_CHAT_COMPLETIONS_URL
        assert request.headers["Authorization"] == f"Bearer {FAKE_API_KEY}"
        payload = json.loads(request.content)
        assert payload["model"] == FAKE_MODEL
        assert payload["temperature"] == 0
        assert payload["max_tokens"] == GROUNDED_ANSWER_MAX_TOKENS
        assert payload["stream"] is False
        assert payload["parallel_tool_calls"] is False
        assert payload["tool_choice"] == {
            "type": "function",
            "function": {"name": GROUNDED_ANSWER_TOOL_NAME},
        }
        tool = payload["tools"][0]["function"]
        assert tool["name"] == GROUNDED_ANSWER_TOOL_NAME
        assert tool["strict"] is True
        assert tool["parameters"]["required"] == ["status", "answer"]
        assert tool["parameters"]["additionalProperties"] is False
        assert "simulated demonstration data" in payload["messages"][0]["content"]
        assert "only the supplied retrieved records" in payload["messages"][0][
            "content"
        ]
        assert "no match or insufficient data" in payload["messages"][0][
            "content"
        ]
        context = json.loads(payload["messages"][1]["content"])
        assert context == {
            "question": QUESTION,
            "proposed_sql": SQL,
            "query_parameters": PARAMETERS,
            "retrieved_records": records,
        }
        assert FAKE_API_KEY.encode() not in request.content
        return httpx.Response(
            200, json=answer_response("answered", expected_answer)
        )

    assert run_answer(handler, records) == GroundedAnswer(
        status="answered", answer=expected_answer
    )


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"choices": []},
        {"choices": [{"message": {}}]},
        answer_response(tool_calls=[]),
        answer_response(tool_name="wrong_tool"),
        answer_response(status="wrong_status"),
        answer_response(answer=""),
        answer_response(answer="   "),
        answer_response(answer=[]),
        answer_response(
            tool_calls=[
                {
                    "type": "function",
                    "function": {
                        "name": GROUNDED_ANSWER_TOOL_NAME,
                        "arguments": "not-json",
                    },
                }
            ]
        ),
        answer_response(
            tool_calls=[
                {
                    "type": "function",
                    "function": {
                        "name": GROUNDED_ANSWER_TOOL_NAME,
                        "arguments": json.dumps(
                            {
                                "status": "answered",
                                "answer": "answer",
                                "extra": True,
                            }
                        ),
                    },
                }
            ]
        ),
    ],
)
def test_grounded_answer_rejects_missing_or_malformed_tool_results(
    payload: dict[str, object],
) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=payload)

    with pytest.raises(OpenRouterResponseError):
        run_answer(handler, [])


@pytest.mark.parametrize(
    ("records", "answer_status"),
    [([], "answered"), ([{"hotel_id": "hotel-1"}], "no_matches")],
)
def test_grounded_answer_rejects_status_inconsistent_with_records(
    records: list[dict[str, Any]], answer_status: str
) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json=answer_response(answer_status, "Inconsistent answer."),
        )

    with pytest.raises(OpenRouterResponseError, match="inconsistent"):
        run_answer(handler, records)


@pytest.mark.parametrize(
    ("records", "answer_status"),
    [
        ([], "no_matches"),
        ([], "insufficient_data"),
        ([{"hotel_id": "hotel-1"}], "answered"),
        ([{"hotel_id": "hotel-1"}], "insufficient_data"),
    ],
)
def test_grounded_answer_accepts_locally_consistent_statuses(
    records: list[dict[str, Any]], answer_status: str
) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200, json=answer_response(answer_status, "Safe grounded answer.")
        )

    assert run_answer(handler, records) == GroundedAnswer(
        status=answer_status, answer="Safe grounded answer."
    )


@pytest.mark.parametrize(
    ("status_code", "expected_error"),
    [
        (401, OpenRouterAuthenticationError),
        (403, OpenRouterAuthenticationError),
        (429, OpenRouterRateLimitError),
        (404, OpenRouterModelUnavailableError),
        (400, OpenRouterProviderError),
        (500, OpenRouterProviderError),
        (503, OpenRouterProviderError),
    ],
)
def test_openrouter_http_failures_are_distinct_and_sanitized(
    status_code: int, expected_error: type[Exception]
) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            status_code,
            json={
                "error": FAKE_API_KEY,
                "provider_url": OPENROUTER_CHAT_COMPLETIONS_URL,
                "header": f"Bearer {FAKE_API_KEY}",
            },
        )

    with pytest.raises(expected_error) as captured_error:
        run_proposal(handler)

    error_text = str(captured_error.value)
    assert FAKE_API_KEY not in error_text
    assert "Bearer" not in error_text
    assert OPENROUTER_CHAT_COMPLETIONS_URL not in error_text


@pytest.mark.parametrize("failure", ["timeout", "network"])
def test_openrouter_transport_failures_are_sanitized(failure: str) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if failure == "timeout":
            raise httpx.ReadTimeout(
                f"timeout with Bearer {FAKE_API_KEY} at "
                f"{OPENROUTER_CHAT_COMPLETIONS_URL}",
                request=request,
            )
        raise httpx.ConnectError(
            f"network failure with Bearer {FAKE_API_KEY}", request=request
        )

    with pytest.raises(OpenRouterTransportError) as captured_error:
        run_proposal(handler)

    error_text = str(captured_error.value)
    assert FAKE_API_KEY not in error_text
    assert "Bearer" not in error_text
    assert OPENROUTER_CHAT_COMPLETIONS_URL not in error_text


@pytest.mark.parametrize(
    "response_factory",
    [
        lambda: httpx.Response(200, content=b"not-json"),
        lambda: httpx.Response(200, content=b"null"),
        lambda: httpx.Response(200, json=[]),
        lambda: httpx.Response(200, json={"choices": "invalid"}),
    ],
)
def test_malformed_provider_responses_are_sanitized(
    response_factory: Callable[[], httpx.Response],
) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return response_factory()

    with pytest.raises(OpenRouterResponseError) as captured_error:
        run_proposal(handler)

    error_text = str(captured_error.value)
    assert FAKE_API_KEY not in error_text
    assert "Authorization" not in error_text
    assert OPENROUTER_CHAT_COMPLETIONS_URL not in error_text
