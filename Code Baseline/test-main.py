# tests/test_main.py
import pytest
from fastapi.testclient import TestClient
from app.main import create_app

@pytest.fixture
def client(tmp_path):
    # Each test gets its own SQLite file
    db_path = tmp_path / "test.db"
    app = create_app(db_path)
    with TestClient(app) as client:
        yield client

def test_create_task(client):
    response = client.post("/tasks", json={"title": "  Test Task  "})
    assert response.status_code == 201
    assert response.json() == {"id": 1, "title": "Test Task", "completed": False}

def test_create_task_invalid_extra_fields(client):
    response = client.post("/tasks", json={"title": "Test", "extra": "field"})
    assert response.status_code == 422

def test_get_task_not_found(client):
    response = client.get("/tasks/99")
    assert response.status_code == 404