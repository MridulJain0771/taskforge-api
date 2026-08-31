import uuid

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.mark.integration
def test_task_crud_and_idempotency():
    email = f"task-{uuid.uuid4().hex}@example.com"
    password = "integration-password"
    with TestClient(app) as client:
        assert client.post("/api/v1/auth/register", json={"email": email, "password": password}).status_code == 201
        login = client.post("/api/v1/auth/login", json={"email": email, "password": password})
        token = login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}", "Idempotency-Key": uuid.uuid4().hex}
        first = client.post("/api/v1/tasks", json={"title": "Ship API"}, headers=headers)
        assert first.status_code == 201
        second = client.post("/api/v1/tasks", json={"title": "Ship API"}, headers=headers)
        assert second.status_code == 200
        assert second.headers["X-Idempotent-Replay"] == "true"
        assert second.json()["id"] == first.json()["id"]
