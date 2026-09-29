import os
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV_FILE = PROJECT_ROOT / ".env"
GEOAPIFY_API_KEY_NAME = "GEOAPIFY_API_KEY"


def get_geoapify_api_key(env_file: Path = ENV_FILE) -> str | None:
    """Load and return the backend-only Geoapify key when configured."""
    load_dotenv(dotenv_path=env_file, override=False)
    value = os.getenv(GEOAPIFY_API_KEY_NAME)
    if value is None:
        return None

    normalized_value = value.strip()
    return normalized_value or None


def geoapify_api_key_status(env_file: Path = ENV_FILE) -> str:
    if get_geoapify_api_key(env_file) is None:
        return "key is not configured"
    return "key is configured"
