import io
import os
import tempfile
import unittest
from unittest.mock import patch

from v2.app import create_app


class FlaskApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.app = create_app()
        self.app.config.update(TESTING=True)
        self.client = self.app.test_client()

    def test_health_endpoint(self) -> None:
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"status": "ok"})

    def test_parse_requires_uploaded_file(self) -> None:
        response = self.client.post("/api/parse")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json(), {"success": False, "message": "No file uploaded"})

    def test_parse_rejects_non_pdf_files(self) -> None:
        data = {"resume": (io.BytesIO(b"not a pdf"), "resume.txt")}
        response = self.client.post("/api/parse", data=data, content_type="multipart/form-data")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json(), {"success": False, "message": "Only PDF files are allowed"})

    def test_parse_returns_parser_output(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch("v2.routes.extract_pdf_text", return_value="Jane Doe\nEngineer") as extract_text_mock, patch(
                "v2.routes.parse_resume_v2", return_value={"name": "Jane Doe"}
            ) as parse_resume_mock:
                data = {"resume": (io.BytesIO(b"%PDF-1.4"), "resume.pdf")}
                response = self.client.post("/api/parse", data=data, content_type="multipart/form-data")

            self.assertEqual(response.status_code, 200)
            self.assertEqual(
                response.get_json(),
                {"success": True, "data": {"name": "Jane Doe"}},
            )
            extract_text_mock.assert_called_once()
            parse_resume_mock.assert_called_once_with("Jane Doe\nEngineer")


if __name__ == "__main__":
    unittest.main()
