import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from core.config import settings
from core.exceptions import InvalidURLError
from main import app
from models.report import (
    AiAnalysis,
    CoreWebVitals,
    PageDetails,
    PerformanceMetrics,
    SeoAuditReport,
    SeoChecks,
)
from models.responses import AuditResponse
from services.audit_service import get_report_path, run_audit, save_report


class TestAuditService(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.reports_dir = Path(self.temp_dir.name)
        self.settings_patch = patch.object(settings, "REPORTS_DIR", str(self.reports_dir))
        self.settings_patch.start()

    def tearDown(self):
        self.settings_patch.stop()
        self.temp_dir.cleanup()

    def test_save_and_get_report_path(self):
        report = SeoAuditReport(
            url="https://www.example.com/",
            generated_at=datetime.now(timezone.utc),
            page_details=PageDetails(title="Test"),
            seo_checks=SeoChecks(
                title_check="PASS",
                meta_description_check="PASS",
                h1_check="PASS",
                alt_text_check="PASS",
                content_length_check="PASS",
            ),
            core_web_vitals=CoreWebVitals(),
            ai_analysis=AiAnalysis(),
        )

        save_report("550e8400-e29b-41d4-a716-446655440000", report)
        path = get_report_path("550e8400-e29b-41d4-a716-446655440000")

        self.assertIsNotNone(path)
        payload = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(payload["url"], "https://www.example.com/")
        self.assertIn("core_web_vitals", payload)

    @patch("services.audit_service.analyze_seo", new_callable=AsyncMock)
    @patch("services.audit_service.fetch_core_web_vitals", new_callable=AsyncMock)
    @patch("services.audit_service.scrape_page", new_callable=AsyncMock)
    @patch("services.audit_service.validate_url")
    async def test_run_audit_orchestrates_workflow(
        self,
        mock_validate_url,
        mock_scrape_page,
        mock_fetch_core_web_vitals,
        mock_analyze_seo,
    ):
        mock_validate_url.return_value = "https://www.example.com/"
        mock_scrape_page.return_value = PageDetails(title="Test Page", word_count=400)
        mock_fetch_core_web_vitals.return_value = CoreWebVitals(
            mobile=PerformanceMetrics(performance_score=80.0),
            desktop=PerformanceMetrics(performance_score=90.0),
        )
        mock_analyze_seo.return_value = AiAnalysis(
            technical_seo_findings=["Canonical URL is present."],
            suggested_title="Optimized Title",
        )

        response = await run_audit("https://www.example.com/")

        self.assertIsInstance(response, AuditResponse)
        self.assertEqual(response.status, "completed")
        self.assertTrue(response.download_url.endswith(response.audit_id))
        self.assertIsNotNone(get_report_path(response.audit_id))
        mock_analyze_seo.assert_awaited_once()


class TestAuditApi(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.reports_dir = Path(self.temp_dir.name)
        self.settings_patch = patch.object(settings, "REPORTS_DIR", str(self.reports_dir))
        self.settings_patch.start()
        self.client = TestClient(app)

    def tearDown(self):
        self.settings_patch.stop()
        self.temp_dir.cleanup()

    @patch("api.v1.audit.run_audit", new_callable=AsyncMock)
    def test_create_audit_returns_response(self, mock_run_audit):
        mock_run_audit.return_value = AuditResponse(
            audit_id="550e8400-e29b-41d4-a716-446655440000",
            download_url="/api/v1/reports/550e8400-e29b-41d4-a716-446655440000",
        )

        response = self.client.post(
            "/api/v1/audit",
            json={"url": "https://www.milestoneinternet.com/"},
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["status"], "completed")
        self.assertIn("audit_id", payload)
        self.assertIn("download_url", payload)

    @patch("api.v1.audit.run_audit", new_callable=AsyncMock)
    def test_create_audit_maps_invalid_url_to_400(self, mock_run_audit):
        mock_run_audit.side_effect = InvalidURLError("URL must use http or https scheme")

        response = self.client.post("/api/v1/audit", json={"url": "https://www.example.com/"})

        self.assertEqual(response.status_code, 400)

    def test_download_report_returns_file(self):
        audit_id = "550e8400-e29b-41d4-a716-446655440000"
        report = SeoAuditReport(
            url="https://www.example.com/",
            generated_at=datetime.now(timezone.utc),
            page_details=PageDetails(title="Test"),
            seo_checks=SeoChecks(
                title_check="PASS",
                meta_description_check="PASS",
                h1_check="PASS",
                alt_text_check="PASS",
                content_length_check="PASS",
            ),
            core_web_vitals=CoreWebVitals(),
            ai_analysis=AiAnalysis(),
        )
        save_report(audit_id, report)

        response = self.client.get(f"/api/v1/reports/{audit_id}")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["content-type"], "application/json")
        self.assertIn("seo_audit_report.json", response.headers.get("content-disposition", ""))

    def test_download_report_not_found(self):
        response = self.client.get("/api/v1/reports/550e8400-e29b-41d4-a716-446655440000")
        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()
