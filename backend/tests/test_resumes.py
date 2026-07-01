"""Tests for resume upload and management endpoints."""
import io
import pytest


# Minimal valid PDF bytes (not a real PDF, just enough to test upload pipeline)
FAKE_PDF_BYTES = (
    b"%PDF-1.4\n1 0 obj<</Type /Catalog /Pages 2 0 R>>\nendobj\n"
    b"2 0 obj<</Type /Pages /Kids[3 0 R]/Count 1>>\nendobj\n"
    b"3 0 obj<</Type /Page /MediaBox[0 0 612 792] /Parent 2 0 R>>\nendobj\n"
    b"xref\n0 4\n0000000000 65535 f\n"
    b"trailer<</Size 4 /Root 1 0 R>>\nstartxref\n%%EOF"
)


def _upload_resume(client, auth_headers, filename="test_resume.pdf", content=FAKE_PDF_BYTES):
    return client.post(
        "/api/v1/resumes/upload",
        files={"file": (filename, io.BytesIO(content), "application/pdf")},
        headers=auth_headers,
    )


class TestResumeUpload:
    def test_upload_pdf_success(self, client, auth_headers):
        response = _upload_resume(client, auth_headers)
        assert response.status_code == 201
        data = response.json()
        assert data["file_name"] == "test_resume.pdf"
        assert data["file_type"] == "pdf"
        assert "id" in data

    def test_upload_unauthenticated(self, client):
        response = client.post(
            "/api/v1/resumes/upload",
            files={"file": ("test.pdf", io.BytesIO(FAKE_PDF_BYTES), "application/pdf")},
        )
        assert response.status_code == 401

    def test_upload_invalid_extension(self, client, auth_headers):
        response = client.post(
            "/api/v1/resumes/upload",
            files={"file": ("resume.exe", io.BytesIO(b"binary"), "application/octet-stream")},
            headers=auth_headers,
        )
        assert response.status_code == 415

    def test_upload_oversized_file(self, client, auth_headers):
        big_file = b"x" * (11 * 1024 * 1024)  # 11 MB > 10 MB limit
        response = client.post(
            "/api/v1/resumes/upload",
            files={"file": ("big.pdf", io.BytesIO(big_file), "application/pdf")},
            headers=auth_headers,
        )
        assert response.status_code == 413


class TestResumeList:
    def test_list_resumes_empty(self, client, auth_headers):
        response = client.get("/api/v1/resumes/", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0

    def test_list_resumes_with_items(self, client, auth_headers):
        _upload_resume(client, auth_headers, "resume1.pdf")
        _upload_resume(client, auth_headers, "resume2.pdf")
        response = client.get("/api/v1/resumes/", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["total"] == 2


class TestResumeDelete:
    def test_delete_resume(self, client, auth_headers):
        upload_resp = _upload_resume(client, auth_headers)
        resume_id = upload_resp.json()["id"]
        delete_resp = client.delete(f"/api/v1/resumes/{resume_id}", headers=auth_headers)
        assert delete_resp.status_code == 204

    def test_delete_nonexistent_resume(self, client, auth_headers):
        response = client.delete("/api/v1/resumes/nonexistent-id", headers=auth_headers)
        assert response.status_code == 404

    def test_delete_other_users_resume(self, client, auth_headers, db_session):
        """Users cannot delete another user's resume."""
        from app.core.security import hash_password
        from app.models.user import User
        from app.models.resume import Resume
        other_user = User(email="other2@example.com", hashed_password=hash_password("Pass123!"), is_active=True)
        db_session.add(other_user)
        db_session.commit()
        db_session.refresh(other_user)
        other_resume = Resume(owner_id=other_user.id, file_name="other.pdf", file_type="pdf")
        db_session.add(other_resume)
        db_session.commit()

        response = client.delete(f"/api/v1/resumes/{other_resume.id}", headers=auth_headers)
        assert response.status_code == 404
