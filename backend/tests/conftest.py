from collections.abc import Iterator
from datetime import date
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app


@pytest.fixture
def database_path(tmp_path: Path) -> Path:
    return tmp_path / "hudson_travel.sqlite3"


@pytest.fixture
def client(database_path: Path) -> Iterator[TestClient]:
    original_database_path = app.state.database_path
    original_today_provider = app.state.today_provider
    original_geoapify_key_provider = app.state.geoapify_key_provider
    original_openrouter_key_provider = app.state.openrouter_key_provider
    original_openrouter_model_provider = app.state.openrouter_model_provider
    original_openai_key_provider = app.state.openai_key_provider
    original_openai_model_provider = app.state.openai_model_provider
    original_zip_location_lookup = app.state.zip_location_lookup
    original_nearby_hotels_lookup = app.state.nearby_hotels_lookup
    original_advisor_query_proposer = app.state.advisor_query_proposer
    original_advisor_query_executor = app.state.advisor_query_executor
    original_advisor_answer_generator = app.state.advisor_answer_generator
    original_advisor_prompt_provider = app.state.advisor_prompt_provider
    original_advisor_http_transport_provider = (
        app.state.advisor_http_transport_provider
    )
    original_advisor_now_provider = app.state.advisor_now_provider
    app.state.database_path = database_path
    app.state.today_provider = lambda: date(2026, 9, 14)
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.state.database_path = original_database_path
        app.state.today_provider = original_today_provider
        app.state.geoapify_key_provider = original_geoapify_key_provider
        app.state.openrouter_key_provider = original_openrouter_key_provider
        app.state.openrouter_model_provider = original_openrouter_model_provider
        app.state.openai_key_provider = original_openai_key_provider
        app.state.openai_model_provider = original_openai_model_provider
        app.state.zip_location_lookup = original_zip_location_lookup
        app.state.nearby_hotels_lookup = original_nearby_hotels_lookup
        app.state.advisor_query_proposer = original_advisor_query_proposer
        app.state.advisor_query_executor = original_advisor_query_executor
        app.state.advisor_answer_generator = original_advisor_answer_generator
        app.state.advisor_prompt_provider = original_advisor_prompt_provider
        app.state.advisor_http_transport_provider = (
            original_advisor_http_transport_provider
        )
        app.state.advisor_now_provider = original_advisor_now_provider
