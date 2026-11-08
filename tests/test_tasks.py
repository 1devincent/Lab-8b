import pytest
from fastapi.testclient import TestClient
from app.main import create_app


@pytest.fixture
def client(tmp_path):
    """Fixture that provides a TestClient with a fresh SQLite database for each test."""
    db_path = tmp_path / "test_tasks.db"
    app = create_app(db_path)
    # Use context manager to ensure startup/shutdown events run
    with TestClient(app) as test_client:
        yield test_client


def test_1_create_valid_task(client):
    """Test 1: POST a valid title and completed=false."""
    payload = {"title": "Write integration tests", "completed": False}
    response = client.post("/tasks", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert isinstance(data["id"], int)
    assert data["title"] == "Write integration tests"
    assert data["completed"] is False


def test_2_create_then_get(client):
    """Test 2: POST a task, then GET its returned ID."""
    payload = {"title": "Review PR", "completed": False}
    post_res = client.post("/tasks", json=payload)
    task_id = post_res.json()["id"]

    get_res = client.get(f"/tasks/{task_id}")
    assert get_res.status_code == 200
    assert get_res.json() == post_res.json()


def test_3_post_whitespace_title(client):
    """Test 3: POST with a title containing spaces only."""
    payload = {"title": "     "}
    response = client.post("/tasks", json=payload)

    assert response.status_code == 422
    assert "String should have at least 1 character" in response.text


def test_4_post_missing_title(client):
    """Test 4: POST with completed=false and no title."""
    payload = {"completed": False}
    response = client.post("/tasks", json=payload)

    assert response.status_code == 422
    assert "Field required" in response.text


def test_5_get_nonexistent_task(client):
    """Test 5: GET a positive ID that does not exist in the fresh database."""
    response = client.get("/tasks/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"


def test_6_patch_task_completed(client):
    """Test 6: POST a task, PATCH its ID with completed=true, then GET it."""
    payload = {"title": "Deploy to production", "completed": False}
    post_res = client.post("/tasks", json=payload)
    task_id = post_res.json()["id"]

    # PATCH
    patch_res = client.patch(f"/tasks/{task_id}", json={"completed": True})
    assert patch_res.status_code == 200
    patch_data = patch_res.json()
    assert patch_data["completed"] is True
    assert patch_data["id"] == task_id
    assert patch_data["title"] == "Deploy to production"

    # GET to verify stored result
    get_res = client.get(f"/tasks/{task_id}")
    assert get_res.status_code == 200
    assert get_res.json() == patch_data