import uuid

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.mark.integration
def test_register_login_and_me_flow():
    email = f"ci-{uuid.uuid4().hex}@example.com"
    password = "integration-password"
    with TestClient(app) as client:
        register = client.post("/api/v1/auth/register", json={"email": email, "password": password})
        assert register.status_code == 201
        login = client.post("/api/v1/auth/login", json={"email": email, "password": password})
        assert login.status_code == 200
        token = login.json()["access_token"]
        me = client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {token}"})
        assert me.status_code == 200
        assert me.json()["email"] == email
