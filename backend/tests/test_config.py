from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from backend.app.config import (
    GEOAPIFY_API_KEY_NAME,
    geoapify_api_key_status,
    get_geoapify_api_key,
)
from backend.app.main import app


@pytest.mark.parametrize(
    ("env_contents", "expected_key", "expected_status"),
    [
        ("GEOAPIFY_API_KEY=fake-test-key\n", "fake-test-key", "key is configured"),
        ("GEOAPIFY_API_KEY=\n", None, "key is not configured"),
        ('GEOAPIFY_API_KEY="   "\n', None, "key is not configured"),
    ],
)
def test_geoapify_configuration_from_explicit_temporary_file(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    env_contents: str,
    expected_key: str | None,
    expected_status: str,
) -> None:
    monkeypatch.delenv(GEOAPIFY_API_KEY_NAME, raising=False)
    env_file = tmp_path / ".env"
    env_file.write_text(env_contents, encoding="utf-8")

    assert get_geoapify_api_key(env_file) == expected_key
    assert geoapify_api_key_status(env_file) == expected_status


def test_missing_geoapify_configuration_is_not_configured(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv(GEOAPIFY_API_KEY_NAME, raising=False)

    assert get_geoapify_api_key(tmp_path / "missing.env") is None
    assert (
        geoapify_api_key_status(tmp_path / "missing.env")
        == "key is not configured"
    )


@pytest.mark.parametrize(
    ("provider_result", "expected_status"),
    [("fake-test-key", "key is configured"), (None, "key is not configured")],
)
def test_health_reports_only_safe_configuration_status(
    client: TestClient, provider_result: str | None, expected_status: str
) -> None:
    app.state.geoapify_key_provider = lambda: provider_result

    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "geoapify": expected_status}
