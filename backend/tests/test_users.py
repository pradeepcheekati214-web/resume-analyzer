"""Tests for user profile endpoints."""


class TestUserProfile:
    def test_get_profile(self, client, auth_headers, test_user):
        response = client.get("/api/v1/users/profile", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user.email
        assert data["full_name"] == test_user.full_name
        assert "hashed_password" not in data

    def test_update_profile_name(self, client, auth_headers):
        response = client.put("/api/v1/users/profile",
            json={"full_name": "Updated Name"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["full_name"] == "Updated Name"

    def test_update_profile_email(self, client, auth_headers):
        response = client.put("/api/v1/users/profile",
            json={"email": "updated@example.com"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["email"] == "updated@example.com"

    def test_update_profile_duplicate_email(self, client, auth_headers, db_session):
        from app.core.security import hash_password
        from app.models.user import User
        other = User(email="other@example.com", hashed_password=hash_password("Pass123!"), is_active=True)
        db_session.add(other)
        db_session.commit()

        response = client.put("/api/v1/users/profile",
            json={"email": "other@example.com"},
            headers=auth_headers,
        )
        assert response.status_code == 409

    def test_update_profile_unauthenticated(self, client):
        response = client.put("/api/v1/users/profile", json={"full_name": "Hacker"})
        assert response.status_code == 401
