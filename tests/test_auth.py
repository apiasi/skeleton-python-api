from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_signup_and_login():
    # Signup
    response = client.post(
        "/api/v1/auth/signup",
        json={
            "email": "test@example.com",
            "full_name": "Test User",
            "password": "secret123",
        },
    )
    assert response.status_code == 201

    # Login
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "test@example.com", "password": "secret123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data


def test_invalid_login():
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "nonexistent@example.com", "password": "wrongpassword"},
    )
    assert response.status_code == 400
