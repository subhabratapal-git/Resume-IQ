"""Run from backend: python -m unittest discover -s tests -v.

Uses a temporary SQLite database and the real HTTP/JWT/scoring flow.
"""
import io
import json
import socket
import tempfile
import threading
import time
import unittest
import urllib.error
import urllib.request
from pathlib import Path

import uvicorn
from docx import Document
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import app.main as main
from app.database import Base, get_db


class AnalysisHistoryIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.engine = create_engine(f"sqlite:///{Path(cls.temp.name) / 'test.db'}", connect_args={"check_same_thread": False})
        cls.previous_engine = main.engine
        main.engine = cls.engine
        sessions = sessionmaker(bind=cls.engine)

        def isolated_db():
            with sessions() as db:
                yield db

        main.app.dependency_overrides[get_db] = isolated_db
        cls.sock = socket.socket()
        cls.sock.bind(("127.0.0.1", 0))
        cls.url = f"http://127.0.0.1:{cls.sock.getsockname()[1]}"
        cls.server = uvicorn.Server(uvicorn.Config(main.app, log_level="error"))
        cls.thread = threading.Thread(target=cls.server.run, kwargs={"sockets": [cls.sock]}, daemon=True)
        cls.thread.start()
        for _ in range(100):
            if cls.server.started:
                break
            time.sleep(0.05)
        if not cls.server.started:
            raise RuntimeError("Test server did not start")

    @classmethod
    def tearDownClass(cls):
        cls.server.should_exit = True
        cls.thread.join(timeout=10)
        main.app.dependency_overrides.clear()
        main.engine = cls.previous_engine
        cls.engine.dispose()
        cls.sock.close()
        cls.temp.cleanup()

    def request(self, method, path, data=None, token=None, content_type="application/json"):
        headers = {"Content-Type": content_type}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        body = json.dumps(data).encode() if isinstance(data, dict) else data
        request = urllib.request.Request(self.url + path, data=body, headers=headers, method=method)
        try:
            with urllib.request.urlopen(request, timeout=15) as response:
                return response.status, json.load(response)
        except urllib.error.HTTPError as error:
            return error.code, json.load(error)

    def multipart(self, description="Python SQL React developer", role="Frontend Developer"):
        document = Document()
        for text in ["Test User", "Skills", "Python SQL React JavaScript Git", "Education", "Bachelor of Technology in Computer Science", "Projects", "Built Python APIs reducing processing time by 30%", "Experience", "Software developer 2022 - 2025. Developed React applications."]:
            document.add_paragraph(text)
        buffer = io.BytesIO()
        document.save(buffer)
        boundary = "ResumeIQTestBoundary"
        body = b""
        for name, value in [("job_description", description), ("target_role", role)]:
            body += f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"\r\n\r\n{value}\r\n'.encode()
        body += f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="resume.docx"\r\nContent-Type: application/vnd.openxmlformats-officedocument.wordprocessingml.document\r\n\r\n'.encode()
        body += buffer.getvalue() + f"\r\n--{boundary}--\r\n".encode()
        return body, f"multipart/form-data; boundary={boundary}"

    def test_history_totals_and_owner_access(self):
        self.assertEqual(self.request("GET", "/stats/analyses"), (200, {"total_analyses": 0}))
        status, auth = self.request("POST", "/auth/register", {"full_name": "Test User", "email": "test@example.com", "password": "History-test-2026"})
        self.assertEqual(status, 201)
        token = auth["access_token"]
        self.assertEqual(self.request("GET", "/resume/history", token=token)[1]["total"], 0)
        self.assertIn(self.request("GET", "/resume/history")[0], [401, 403])
        body, content_type = self.multipart()
        status, result = self.request("POST", "/resume/analyze", body, token, content_type)
        self.assertEqual(status, 200)
        self.assertEqual(result["target_role"], "Frontend Developer")
        self.assertEqual(self.request("GET", "/stats/analyses")[1]["total_analyses"], 1)
        status, report = self.request("GET", f'/resume/history/{result["analysis_id"]}', token=token)
        self.assertEqual(status, 200)
        self.assertEqual(report, {key: value for key, value in result.items() if key != "user"})
        self.assertTrue(report["analyzed_at"].endswith("Z"))
        self.assertNotIn("user", report)
        self.assertNotIn("job_description", report)
        failed, failed_type = self.multipart(description=" ")
        self.assertEqual(self.request("POST", "/resume/analyze", failed, token, failed_type)[0], 400)
        self.assertEqual(self.request("POST", "/resume/upload", body, token, content_type)[0], 200)
        self.assertEqual(self.request("GET", "/stats/analyses")[1]["total_analyses"], 1)
        status, second = self.request("POST", "/resume/analyze", body, token, content_type)
        self.assertEqual(status, 200)
        self.assertNotEqual(second["analysis_id"], result["analysis_id"])
        self.assertEqual(second["ats_score_details"], result["ats_score_details"])
        history = self.request("GET", "/resume/history?limit=1", token=token)[1]
        self.assertEqual(history["total"], 2)
        self.assertEqual(history["best_score"], result["ats_score_details"]["ats_score"])
        self.assertEqual(history["items"][0]["id"], second["analysis_id"])
        older = self.request("GET", "/resume/history?offset=1&limit=1", token=token)[1]
        self.assertEqual(older["items"][0]["id"], result["analysis_id"])
        self.assertEqual(self.request("GET", "/resume/history?offset=-1", token=token)[0], 422)
        _, other = self.request("POST", "/auth/register", {"full_name": "Other User", "email": "other@example.com", "password": "History-test-2026"})
        self.assertEqual(self.request("GET", "/resume/history", token=other["access_token"])[1]["total"], 0)
        self.assertEqual(self.request("GET", f'/resume/history/{result["analysis_id"]}', token=other["access_token"])[0], 404)
        _, login = self.request("POST", "/auth/login", {"email": "test@example.com", "password": "History-test-2026"})
        self.assertEqual(self.request("GET", "/resume/history", token=login["access_token"])[1]["total"], 2)
        self.assertEqual(self.request("GET", "/stats/analyses"), (200, {"total_analyses": 2}))
        # Test change password flow
        # 1. Wrong current password fails
        status, res = self.request("POST", "/auth/change-password", {"current_password": "WrongPassword!", "new_password": "NewSecretPassword123", "confirm_password": "NewSecretPassword123"}, token=token)
        self.assertEqual(status, 400)
        # 2. Password mismatch fails
        status, res = self.request("POST", "/auth/change-password", {"current_password": "History-test-2026", "new_password": "NewSecretPassword123", "confirm_password": "DifferentPassword123"}, token=token)
        self.assertEqual(status, 400)
        # 3. Successful password change
        status, res = self.request("POST", "/auth/change-password", {"current_password": "History-test-2026", "new_password": "NewSecretPassword123", "confirm_password": "NewSecretPassword123"}, token=token)
        self.assertEqual(status, 200)
        self.assertEqual(res["message"], "Password changed successfully")
        # 4. Old password can no longer login
        status, _ = self.request("POST", "/auth/login", {"email": "test@example.com", "password": "History-test-2026"})
        self.assertEqual(status, 401)
        # 5. New password logs in successfully
        status, new_login = self.request("POST", "/auth/login", {"email": "test@example.com", "password": "NewSecretPassword123"})
        self.assertEqual(status, 200)

        self.assertEqual(self.request("GET", "/health")[0], 200)
        self.assertEqual(self.request("GET", "/resume/test")[0], 404)


if __name__ == "__main__":
    unittest.main()
