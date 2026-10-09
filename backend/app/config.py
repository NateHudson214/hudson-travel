import os
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV_FILE = PROJECT_ROOT / ".env"
GEOAPIFY_API_KEY_NAME = "GEOAPIFY_API_KEY"
OPENROUTER_API_KEY_NAME = "OPENROUTER_API_KEY"
OPENROUTER_MODEL_NAME = "OPENROUTER_MODEL"
DEFAULT_OPENROUTER_MODEL = "nvidia/nemotron-3.5-lightning:free"
OPENAI_API_KEY_NAME = "OPEN_AI"
OPENAI_MODEL_NAME = "OPENAI_MODEL"
DEFAULT_OPENAI_MODEL = "gpt-6-luna"


def _get_optional_setting(name: str, env_file: Path) -> str | None:
    load_dotenv(dotenv_path=env_file, override=False)
    value = os.getenv(name)
    if value is None:
        return None

    normalized_value = value.strip()
    return normalized_value or None


def get_geoapify_api_key(env_file: Path = ENV_FILE) -> str | None:
    """Load and return the backend-only Geoapify key when configured."""
    return _get_optional_setting(GEOAPIFY_API_KEY_NAME, env_file)


def geoapify_api_key_status(env_file: Path = ENV_FILE) -> str:
    if get_geoapify_api_key(env_file) is None:
        return "key is not configured"
    return "key is configured"


def get_openrouter_api_key(env_file: Path = ENV_FILE) -> str | None:
    """Load and return the backend-only OpenRouter key when configured."""
    return _get_optional_setting(OPENROUTER_API_KEY_NAME, env_file)


def openrouter_api_key_status(env_file: Path = ENV_FILE) -> str:
    if get_openrouter_api_key(env_file) is None:
        return "key is not configured"
    return "key is configured"


def get_openrouter_model(env_file: Path = ENV_FILE) -> str:
    """Return the configured OpenRouter model or the reviewed free default."""
    return (
        _get_optional_setting(OPENROUTER_MODEL_NAME, env_file)
        or DEFAULT_OPENROUTER_MODEL
    )


def get_openai_api_key(env_file: Path = ENV_FILE) -> str | None:
    """Load and return the backend-only OpenAI key when configured."""
    return _get_optional_setting(OPENAI_API_KEY_NAME, env_file)


def openai_api_key_status(env_file: Path = ENV_FILE) -> str:
    if get_openai_api_key(env_file) is None:
        return "key is not configured"
    return "key is configured"


def get_openai_model(env_file: Path = ENV_FILE) -> str:
    """Return the configured OpenAI model or the reviewed default."""
    return _get_optional_setting(OPENAI_MODEL_NAME, env_file) or DEFAULT_OPENAI_MODEL
