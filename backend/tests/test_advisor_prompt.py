from hashlib import sha256
from pathlib import Path

import pytest

from backend.app.advisor_prompt import (
    HOTEL_ASSISTANT_PROMPT_FILE,
    AdvisorPromptError,
    load_hotel_assistant_prompt,
)


def test_repository_prompt_uses_explicit_project_path_and_required_rules() -> None:
    prompt = load_hotel_assistant_prompt()
    normalized_prompt = " ".join(prompt.text.split())

    assert HOTEL_ASSISTANT_PROMPT_FILE.is_absolute()
    assert HOTEL_ASSISTANT_PROMPT_FILE.name == "hotel-assistant.md"
    assert "saved_hotels(" in prompt.text
    assert "saved_hotel_searches(" in prompt.text
    assert "demo_hotel_nights(" in prompt.text
    assert "parameterized" in prompt.text
    assert "read-only" in prompt.text
    assert "LIMIT" in prompt.text
    assert "nightly_rate_cents" in prompt.text
    assert "rooms_available" in prompt.text
    assert "simulated demonstration data" in prompt.text
    assert "October 10 through October 14, 2026" in prompt.text
    assert "without a year" in prompt.text
    assert "use 2026 in every bound date value" in prompt.text
    assert "never invent or substitute a different year" in prompt.text
    assert '"October 10 through October 12"' in prompt.text
    assert "bind check-in to `2026-10-10`" in prompt.text
    assert "checkout to `2026-10-12`" in prompt.text
    assert "do not advance checkout to October 13" in prompt.text
    assert "exactly one flat" in prompt.text
    assert "Never use a" in prompt.text
    assert "`WITH` clause" in prompt.text
    assert "`UNION`" in prompt.text
    assert "`INTERSECT`" in prompt.text
    assert "`EXCEPT`" in prompt.text
    assert "no more than two `JOIN` clauses" in prompt.text
    assert "with exactly two joins" in normalized_prompt
    assert "n.stay_date >= :check_in" in prompt.text
    assert "n.stay_date <" in prompt.text
    assert ":check_out" in prompt.text
    assert "`night_count` to `2`" in prompt.text
    assert "COUNT(n.stay_date) AS requested_nights" in prompt.text
    assert "MIN(n.rooms_available) AS" in prompt.text
    assert "minimum_rooms" in prompt.text
    assert "HAVING COUNT(n.stay_date) = :night_count" in prompt.text
    assert "MIN(n.rooms_available) > 0" in prompt.text
    assert "check-in date and excludes the checkout date" in prompt.text
    assert "SUM(nightly_rate_cents) AS" in prompt.text
    assert "total_cost_cents" in prompt.text
    assert "dividing cents by exactly 100" in prompt.text
    assert "{{total_cost}}" in prompt.text
    assert "Preserve an explicit" in prompt.text
    assert "no-match" in prompt.text
    assert "insufficient-data" in prompt.text
    assert "bookings(" not in prompt.text
    assert "users(" not in prompt.text
    assert "OPEN_AI" not in prompt.text
    assert "API_KEY" not in prompt.text


def test_prompt_version_is_sha256_of_exact_file_bytes(tmp_path: Path) -> None:
    prompt_file = tmp_path / "hotel-assistant.md"
    prompt_bytes = b"Test prompt with deterministic bytes.\n"
    prompt_file.write_bytes(prompt_bytes)

    prompt = load_hotel_assistant_prompt(prompt_file)

    assert prompt.text == "Test prompt with deterministic bytes."
    assert prompt.version == f"sha256:{sha256(prompt_bytes).hexdigest()}"


@pytest.mark.parametrize("contents", [b"", b"   \n", b"\xff"])
def test_missing_empty_or_invalid_prompt_is_sanitized(
    tmp_path: Path, contents: bytes
) -> None:
    prompt_file = tmp_path / "hotel-assistant.md"
    prompt_file.write_bytes(contents)

    with pytest.raises(AdvisorPromptError) as captured_error:
        load_hotel_assistant_prompt(prompt_file)

    assert str(prompt_file) not in str(captured_error.value)
