"""Render approved reply selections. Never render model-supplied prose."""

from dataclasses import dataclass
from types import MappingProxyType
from typing import Callable


CONTEXT_VERSION = "skills-replies-v1"
FALLBACK_TEXT = (
    "Conversation is unavailable. You can continue without it. "
    "Crisis support remains available."
)

_REPLIES = MappingProxyType({
    "neutral_acknowledgment": "You can choose what to do next.",
    "explain_available_skill": "This prototype offers one paced breathing exercise.",
    "clarify_supported_scope": "This coursework prototype is for fictional testing only.",
    "support_signpost": "The Crisis support control opens U.S. support information.",
})
_FACTS = MappingProxyType({
    "breathing_sequence": "Each of six cycles has a four-second inhale and six-second exhale.",
    "no_typing_required": "No typing is required during the exercise.",
    "pause_or_stop": "You can pause, stop, or leave at any time.",
    "static_display_option": "You can choose a static display instead of motion.",
    "fictional_testing_only": "Use only fictional scenarios with this prototype.",
})
_ALLOWED_FACTS = MappingProxyType({
    "neutral_acknowledgment": frozenset({"pause_or_stop", "static_display_option"}),
    "explain_available_skill": frozenset(_FACTS),
    "clarify_supported_scope": frozenset({"fictional_testing_only", "pause_or_stop"}),
    "support_signpost": frozenset({"pause_or_stop", "fictional_testing_only"}),
})


class InvalidReply(ValueError):
    """Untrusted selection does not satisfy the reviewed response boundary."""


def approved_context() -> dict:
    """Return a fresh catalog; callers cannot mutate the renderer's definitions."""
    return {
        "version": CONTEXT_VERSION,
        "replies": dict(_REPLIES),
        "facts": dict(_FACTS),
        "compatible_facts": {
            key: sorted(values) for key, values in _ALLOWED_FACTS.items()
        },
    }


def render_reply(selection: object) -> str:
    if type(selection) is not dict or set(selection) != {"reply_id", "fact_ids"}:
        raise InvalidReply("The reply selection is invalid.")
    reply_id = selection["reply_id"]
    fact_ids = selection["fact_ids"]
    if (
        type(reply_id) is not str
        or reply_id not in _REPLIES
        or type(fact_ids) is not list
        or len(fact_ids) > 2
        or any(type(value) is not str for value in fact_ids)
    ):
        raise InvalidReply("The reply selection is invalid.")
    if len(set(fact_ids)) != len(fact_ids) or any(
        fact not in _ALLOWED_FACTS[reply_id] for fact in fact_ids
    ):
        raise InvalidReply("The reply selection is invalid.")
    text = " ".join([_REPLIES[reply_id], *(_FACTS[fact] for fact in fact_ids)])
    if len(text) > 600:
        raise InvalidReply("The reply selection exceeds its limit.")
    return text


@dataclass(frozen=True)
class MockReplyResult:
    status: str
    content: str
    mode: str = "mock"
    context_version: str = CONTEXT_VERSION


def mock_conversation_reply(
    fictional_message: str,
    *,
    response_provider: Callable[[str, dict], object],
) -> MockReplyResult:
    """Explicitly injected local mock, with no provider/client/config imports."""
    if (
        type(fictional_message) is not str
        or not fictional_message.strip()
        or len(fictional_message.strip()) > 500
    ):
        raise ValueError("Enter a fictional message of 1 to 500 characters.")
    try:
        selection = response_provider(fictional_message.strip(), approved_context())
        return MockReplyResult("completed", render_reply(selection))
    except Exception:
        # No raw rejected output or provider exception reaches visible conversation.
        return MockReplyResult("failed", FALLBACK_TEXT)
