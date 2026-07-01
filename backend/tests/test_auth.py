"""Tests for authentication endpoints."""
import pytest


class TestRegister:
    def test_register_success(self, client):
        response = client.post("/api/v1/auth/register", json={
            "email": "new@example.com",
            "password": "SecurePass123!",
            "full_name": "New User",
        })
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "new@example.com"
        assert data["full_name"] == "New User"
        assert "hashed_password" not in data

    def test_register_duplicate_email(self, client, test_user):
        response = client.post("/api/v1/auth/register", json={
            "email": "test@example.com",
            "password": "AnotherPass123!",
        })
        assert response.status_code == 409

    def test_register_invalid_email(self, client):
        response = client.post("/api/v1/auth/register", json={
            "email": "not-an-email",
            "password": "SecurePass123!",
        })
        assert response.status_code == 422

    def test_register_short_password(self, client):
        response = client.post("/api/v1/auth/register", json={
            "email": "short@example.com",
            "password": "abc",
        })
        assert response.status_code == 422


class TestLogin:
    def test_login_success(self, client, test_user):
        response = client.post("/api/v1/auth/login", data={
            "username": "test@example.com",
            "password": "TestPass123!",
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert "user" in data

    def test_login_wrong_password(self, client, test_user):
        response = client.post("/api/v1/auth/login", data={
            "username": "test@example.com",
            "password": "WrongPassword!",
        })
        assert response.status_code == 401

    def test_login_nonexistent_user(self, client):
        response = client.post("/api/v1/auth/login", data={
            "username": "ghost@example.com",
            "password": "AnyPass123!",
        })
        assert response.status_code == 401


class TestProtectedRoutes:
    def test_get_profile_authenticated(self, client, auth_headers):
        response = client.get("/api/v1/users/profile", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["email"] == "test@example.com"

    def test_get_profile_unauthenticated(self, client):
        response = client.get("/api/v1/users/profile")
        assert response.status_code == 401

    def test_get_profile_invalid_token(self, client):
        response = client.get("/api/v1/users/profile", headers={"Authorization": "Bearer invalid"})
        assert response.status_code == 401

    def test_logout(self, client, auth_headers):
        response = client.post("/api/v1/auth/logout", headers=auth_headers)
        assert response.status_code == 204


class TestChangePassword:
    def test_change_password_success(self, client, auth_headers):
        response = client.post("/api/v1/auth/change-password", json={
            "current_password": "TestPass123!",
            "new_password": "NewSecurePass456!",
        }, headers=auth_headers)
        assert response.status_code == 200

    def test_change_password_wrong_current(self, client, auth_headers):
        response = client.post("/api/v1/auth/change-password", json={
            "current_password": "WrongCurrent!",
            "new_password": "NewPass456!",
        }, headers=auth_headers)
        assert response.status_code == 400
