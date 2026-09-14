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
    app.state.database_path = database_path
    app.state.today_provider = lambda: date(2026, 9, 14)
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.state.database_path = original_database_path
        app.state.today_provider = original_today_provider
