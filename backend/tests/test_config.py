from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from backend.app.config import (
    DEFAULT_OPENAI_MODEL,
    DEFAULT_OPENROUTER_MODEL,
    GEOAPIFY_API_KEY_NAME,
    OPENAI_API_KEY_NAME,
    OPENAI_MODEL_NAME,
    OPENROUTER_API_KEY_NAME,
    OPENROUTER_MODEL_NAME,
    geoapify_api_key_status,
    get_geoapify_api_key,
    get_openai_api_key,
    get_openai_model,
    get_openrouter_api_key,
    get_openrouter_model,
    openai_api_key_status,
    openrouter_api_key_status,
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
    ("env_contents", "expected_key", "expected_status"),
    [
        (
            "OPENROUTER_API_KEY=fake-openrouter-test-key\n",
            "fake-openrouter-test-key",
            "key is configured",
        ),
        ("OPENROUTER_API_KEY=\n", None, "key is not configured"),
        ('OPENROUTER_API_KEY="   "\n', None, "key is not configured"),
    ],
)
def test_openrouter_configuration_from_explicit_temporary_file(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    env_contents: str,
    expected_key: str | None,
    expected_status: str,
) -> None:
    monkeypatch.delenv(OPENROUTER_API_KEY_NAME, raising=False)
    env_file = tmp_path / ".env"
    env_file.write_text(env_contents, encoding="utf-8")

    assert get_openrouter_api_key(env_file) == expected_key
    assert openrouter_api_key_status(env_file) == expected_status


def test_missing_openrouter_configuration_is_not_configured(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv(OPENROUTER_API_KEY_NAME, raising=False)

    assert get_openrouter_api_key(tmp_path / "missing.env") is None
    assert (
        openrouter_api_key_status(tmp_path / "missing.env")
        == "key is not configured"
    )


@pytest.mark.parametrize(
    ("env_contents", "expected_model"),
    [
        (
            "OPENROUTER_MODEL=test-provider/test-model\n",
            "test-provider/test-model",
        ),
        ("OPENROUTER_MODEL=\n", DEFAULT_OPENROUTER_MODEL),
        ('OPENROUTER_MODEL="   "\n', DEFAULT_OPENROUTER_MODEL),
        ("", DEFAULT_OPENROUTER_MODEL),
    ],
)
def test_openrouter_model_from_explicit_temporary_file(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    env_contents: str,
    expected_model: str,
) -> None:
    monkeypatch.delenv(OPENROUTER_MODEL_NAME, raising=False)
    env_file = tmp_path / ".env"
    env_file.write_text(env_contents, encoding="utf-8")

    assert get_openrouter_model(env_file) == expected_model


@pytest.mark.parametrize(
    ("env_contents", "expected_key", "expected_status"),
    [
        (
            "OPEN_AI=fake-openai-test-key\n",
            "fake-openai-test-key",
            "key is configured",
        ),
        ("OPEN_AI=\n", None, "key is not configured"),
        ('OPEN_AI="   "\n', None, "key is not configured"),
    ],
)
def test_openai_configuration_from_explicit_temporary_file(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    env_contents: str,
    expected_key: str | None,
    expected_status: str,
) -> None:
    monkeypatch.delenv(OPENAI_API_KEY_NAME, raising=False)
    env_file = tmp_path / ".env"
    env_file.write_text(env_contents, encoding="utf-8")

    assert get_openai_api_key(env_file) == expected_key
    assert openai_api_key_status(env_file) == expected_status


def test_missing_openai_configuration_is_not_configured(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv(OPENAI_API_KEY_NAME, raising=False)

    assert get_openai_api_key(tmp_path / "missing.env") is None
    assert (
        openai_api_key_status(tmp_path / "missing.env")
        == "key is not configured"
    )


@pytest.mark.parametrize(
    ("env_contents", "expected_model"),
    [
        ("OPENAI_MODEL=test-openai-model\n", "test-openai-model"),
        ("OPENAI_MODEL=\n", DEFAULT_OPENAI_MODEL),
        ('OPENAI_MODEL="   "\n', DEFAULT_OPENAI_MODEL),
        ("", DEFAULT_OPENAI_MODEL),
    ],
)
def test_openai_model_from_explicit_temporary_file(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    env_contents: str,
    expected_model: str,
) -> None:
    monkeypatch.delenv(OPENAI_MODEL_NAME, raising=False)
    env_file = tmp_path / ".env"
    env_file.write_text(env_contents, encoding="utf-8")

    assert get_openai_model(env_file) == expected_model


@pytest.mark.parametrize(
    ("provider_result", "expected_status"),
    [("fake-test-key", "key is configured"), (None, "key is not configured")],
)
def test_health_reports_only_safe_configuration_status(
    client: TestClient, provider_result: str | None, expected_status: str
) -> None:
    app.state.geoapify_key_provider = lambda: provider_result
    app.state.openrouter_key_provider = lambda: provider_result
    app.state.openrouter_model_provider = lambda: DEFAULT_OPENROUTER_MODEL
    app.state.openai_key_provider = lambda: provider_result
    app.state.openai_model_provider = lambda: DEFAULT_OPENAI_MODEL

    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "geoapify": expected_status,
        "openrouter": expected_status,
        "openrouter_model": DEFAULT_OPENROUTER_MODEL,
        "openai": expected_status,
        "openai_model": DEFAULT_OPENAI_MODEL,
    }
    assert "fake-test-key" not in response.text


def test_health_never_exposes_openrouter_key_or_fragment(
    client: TestClient,
) -> None:
    secret_value = "openrouter-secret-value-for-test"
    app.state.geoapify_key_provider = lambda: None
    app.state.openrouter_key_provider = lambda: secret_value
    app.state.openrouter_model_provider = lambda: DEFAULT_OPENROUTER_MODEL
    app.state.openai_key_provider = lambda: None
    app.state.openai_model_provider = lambda: DEFAULT_OPENAI_MODEL

    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json()["openrouter"] == "key is configured"
    assert secret_value not in response.text
    assert "secret-value" not in response.text


def test_health_preserves_independent_geoapify_status(
    client: TestClient,
) -> None:
    app.state.geoapify_key_provider = lambda: "fake-geoapify-test-key"
    app.state.openrouter_key_provider = lambda: None
    app.state.openrouter_model_provider = lambda: DEFAULT_OPENROUTER_MODEL
    app.state.openai_key_provider = lambda: None
    app.state.openai_model_provider = lambda: DEFAULT_OPENAI_MODEL

    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "geoapify": "key is configured",
        "openrouter": "key is not configured",
        "openrouter_model": DEFAULT_OPENROUTER_MODEL,
        "openai": "key is not configured",
        "openai_model": DEFAULT_OPENAI_MODEL,
    }
    assert "fake-geoapify-test-key" not in response.text


def test_health_never_exposes_openai_key_or_fragment(client: TestClient) -> None:
    secret_value = "openai-secret-value-for-test"
    app.state.geoapify_key_provider = lambda: None
    app.state.openrouter_key_provider = lambda: None
    app.state.openrouter_model_provider = lambda: DEFAULT_OPENROUTER_MODEL
    app.state.openai_key_provider = lambda: secret_value
    app.state.openai_model_provider = lambda: DEFAULT_OPENAI_MODEL

    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json()["openai"] == "key is configured"
    assert secret_value not in response.text
    assert "secret-value" not in response.text


def test_health_preserves_independent_provider_statuses(client: TestClient) -> None:
    app.state.geoapify_key_provider = lambda: "fake-geoapify-key"
    app.state.openrouter_key_provider = lambda: None
    app.state.openrouter_model_provider = lambda: DEFAULT_OPENROUTER_MODEL
    app.state.openai_key_provider = lambda: "fake-openai-key"
    app.state.openai_model_provider = lambda: "test-openai-model"

    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "geoapify": "key is configured",
        "openrouter": "key is not configured",
        "openrouter_model": DEFAULT_OPENROUTER_MODEL,
        "openai": "key is configured",
        "openai_model": "test-openai-model",
    }
    assert "fake-geoapify-key" not in response.text
    assert "fake-openai-key" not in response.text
