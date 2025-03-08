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


def test_signup_duplicate_user():
    # Create first user
    response = client.post(
        "/api/v1/auth/signup",
        json={
            "email": "duplicate@example.com",
            "full_name": "Test User",
            "password": "secret123",
        },
    )
    assert response.status_code == 201

    # Try to create duplicate user
    response = client.post(
        "/api/v1/auth/signup",
        json={
            "email": "duplicate@example.com",
            "full_name": "Test User 2",
            "password": "secret456",
        },
    )
    assert response.status_code == 400


def test_get_me_endpoint():
    # First create and login user
    client.post(
        "/api/v1/auth/signup",
        json={
            "email": "me@example.com",
            "full_name": "Test User",
            "password": "secret123",
        },
    )

    login_response = client.post(
        "/api/v1/auth/login",
        data={"username": "me@example.com", "password": "secret123"},
    )
    access_token = login_response.json()["access_token"]

    # Test /me endpoint with valid token
    response = client.get(
        "/api/v1/auth/me", headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "me@example.com"
    assert data["full_name"] == "Test User"


def test_get_me_invalid_token():
    response = client.get(
        "/api/v1/auth/me", headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 401


def test_refresh_token():
    # First create and login user
    client.post(
        "/api/v1/auth/signup",
        json={
            "email": "refresh@example.com",
            "full_name": "Test User",
            "password": "secret123",
        },
    )

    login_response = client.post(
        "/api/v1/auth/login",
        data={"username": "refresh@example.com", "password": "secret123"},
    )
    access_token = login_response.json()["access_token"]

    # Test refresh token endpoint
    response = client.post("/api/v1/auth/refresh", json={"refresh_token": access_token})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_refresh_token_invalid():
    response = client.post(
        "/api/v1/auth/refresh", json={"refresh_token": "invalid_token"}
    )
    assert response.status_code == 401


def test_signup_validation():
    # Test with invalid email
    response = client.post(
        "/api/v1/auth/signup",
        json={
            "email": "invalid-email",
            "full_name": "Test User",
            "password": "secret123",
        },
    )
    assert response.status_code == 422

    # Test with short password
    response = client.post(
        "/api/v1/auth/signup",
        json={
            "email": "valid@example.com",
            "full_name": "Test User",
            "password": "12345",  # less than min_length=6
        },
    )
    assert response.status_code == 422
