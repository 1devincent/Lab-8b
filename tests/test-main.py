import pytest


def test_7_patch_invalid_strict_boolean(client):
    post_res = client.post("/tasks", json={"title": "Test"})
    task_id = post_res.json()["id"]
    # Send a string instead of boolean
    response = client.patch(f"/tasks/{task_id}", json={"completed": "true"})
    assert response.status_code == 422


@pytest.mark.parametrize("invalid_id", ["0", "-1", "abc", "1.5"])
def test_8_invalid_task_ids(client, invalid_id):
    response = client.get(f"/tasks/{invalid_id}")
    assert response.status_code == 422


def test_9_patch_missing_task_404(client):
    response = client.patch("/tasks/999", json={"completed": True})
    assert response.status_code == 404


def test_10_extra_fields_rejected(client):
    # POST with extra field
    res_post = client.post("/tasks", json={"title": "Test", "extra": "field"})
    assert res_post.status_code == 422

    # PATCH with extra field
    post_res = client.post("/tasks", json={"title": "Test"})
    task_id = post_res.json()["id"]
    res_patch = client.patch(f"/tasks/{task_id}", json={"completed": True, "extra": "field"})
    assert res_patch.status_code == 422