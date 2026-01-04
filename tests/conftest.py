import pytest  # type: ignore
from fastapi.testclient import TestClient  # type: ignore

from app_gestao.app import app


@pytest.fixture
def client():
    return TestClient(app)
