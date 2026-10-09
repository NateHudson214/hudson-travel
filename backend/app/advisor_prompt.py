from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
HOTEL_ASSISTANT_PROMPT_FILE = PROJECT_ROOT / "prompts" / "hotel-assistant.md"


class AdvisorPromptError(Exception):
    """Raised when the repository-owned hotel-assistant prompt is unavailable."""


@dataclass(frozen=True)
class AdvisorPrompt:
    text: str
    version: str


def load_hotel_assistant_prompt(
    prompt_file: Path = HOTEL_ASSISTANT_PROMPT_FILE,
) -> AdvisorPrompt:
    """Load the explicit repository prompt and return its deterministic version."""
    try:
        prompt_bytes = prompt_file.read_bytes()
        prompt_text = prompt_bytes.decode("utf-8").strip()
    except (OSError, UnicodeError):
        raise AdvisorPromptError(
            "The hotel assistant prompt could not be loaded."
        ) from None
    if not prompt_text:
        raise AdvisorPromptError(
            "The hotel assistant prompt could not be loaded."
        )
    return AdvisorPrompt(
        text=prompt_text,
        version=f"sha256:{sha256(prompt_bytes).hexdigest()}",
    )
