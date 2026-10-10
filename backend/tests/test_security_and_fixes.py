import io
import os
import unittest
from datetime import datetime, timezone
from fastapi.testclient import TestClient
from docx import Document

os.environ["ENVIRONMENT"] = "development"
os.environ["JWT_SECRET_KEY"] = "test-secret-key-12345678901234567890"

import app.main as main
from app.database import Base, engine, SessionLocal
from app.models.user import User
from app.models.analysis import ResumeAnalysis


class TestSecurityAndFixes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Base.metadata.create_all(bind=engine)
        cls.client = TestClient(main.app)

    def setUp(self):
        self.db = SessionLocal()
        self.db.query(ResumeAnalysis).delete()
        self.db.query(User).delete()
        self.db.commit()

    def tearDown(self):
        self.db.close()

    def create_dummy_docx(self, text="John Doe. Software Engineer with Python and React.") -> bytes:
        doc = Document()
        doc.add_paragraph(text)
        buf = io.BytesIO()
        doc.save(buf)
        return buf.getvalue()

    def test_password_change_invalidates_prior_tokens(self):
        # 1. Register user
        reg_res = self.client.post("/auth/register", json={
            "full_name": "Security User",
            "email": "sec@example.com",
            "password": "Password123!"
        })
        self.assertEqual(reg_res.status_code, 201)
        old_token = reg_res.json()["access_token"]

        # 2. Access /auth/me with initial token
        me_res = self.client.get("/auth/me", headers={"Authorization": f"Bearer {old_token}"})
        self.assertEqual(me_res.status_code, 200)

        # 3. Change password
        chg_res = self.client.post(
            "/auth/change-password",
            json={
                "current_password": "Password123!",
                "new_password": "NewSecretPassword123!",
                "confirm_password": "NewSecretPassword123!"
            },
            headers={"Authorization": f"Bearer {old_token}"}
        )
        self.assertEqual(chg_res.status_code, 200)

        # 4. Old token MUST now be rejected with 401
        me_after_res = self.client.get("/auth/me", headers={"Authorization": f"Bearer {old_token}"})
        self.assertEqual(me_after_res.status_code, 401)
        self.assertIn("Password was changed", me_after_res.json()["detail"])

        # 5. Logging in with new password grants fresh working token
        login_res = self.client.post("/auth/login", json={
            "email": "sec@example.com",
            "password": "NewSecretPassword123!"
        })
        self.assertEqual(login_res.status_code, 200)
        new_token = login_res.json()["access_token"]

        me_new_res = self.client.get("/auth/me", headers={"Authorization": f"Bearer {new_token}"})
        self.assertEqual(me_new_res.status_code, 200)

    def test_pro_quota_rollback_on_bad_file(self):
        # Register user with 5 pro uses
        reg_res = self.client.post("/auth/register", json={
            "full_name": "Pro User",
            "email": "pro@example.com",
            "password": "Password123!"
        })
        token = reg_res.json()["access_token"]

        # Send invalid file content with docx extension to trigger 400 after quota check
        files = {
            "file": ("corrupt.docx", b"PKFakeCorruptBinaryNotReadable", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        }
        data = {
            "job_description": "We need a Python React Developer with 3 years experience.",
            "target_role": "Software Engineer"
        }
        res = self.client.post(
            "/api/pro/analyze",
            files=files,
            data=data,
            headers={"Authorization": f"Bearer {token}"}
        )
        self.assertEqual(res.status_code, 400)

        # Verify quota remained 5 (was rolled back, not decremented)
        status_res = self.client.get("/api/pro/status", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(status_res.status_code, 200)
        self.assertEqual(status_res.json()["pro_uses_remaining"], 5)


if __name__ == "__main__":
    unittest.main()
