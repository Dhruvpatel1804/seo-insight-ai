import json
import unittest
from datetime import datetime, timezone

from pydantic import ValidationError

from models import (
    AiAnalysis,
    AuditRequest,
    AuditResponse,
    AuditSummary,
    CoreWebVitals,
    PageDetails,
    PerformanceMetrics,
    SeoAuditReport,
    SeoChecks,
)
from services.audit_service import build_audit_summary


class TestAuditRequest(unittest.TestCase):
    def test_valid_url(self):
        request = AuditRequest(url="https://www.milestoneinternet.com/")
        self.assertEqual(str(request.url), "https://www.milestoneinternet.com/")

    def test_invalid_url(self):
        with self.assertRaises(ValidationError):
            AuditRequest(url="not-a-url")


class TestAuditResponse(unittest.TestCase):
    def test_completed_status(self):
        response = AuditResponse(
            audit_id="abc-123",
            download_url="/api/v1/reports/abc-123",
        )
        self.assertEqual(response.status, "completed")
        self.assertIsNone(response.summary)

    def test_response_includes_summary(self):
        summary = AuditSummary(
            url="https://www.example.com/",
            generated_at=datetime.now(timezone.utc),
            page_title="Example",
            seo_checks=SeoChecks(
                title_check="PASS",
                meta_description_check="PASS",
                h1_check="PASS",
                alt_text_check="PASS",
                content_length_check="PASS",
            ),
            seo_pass_count=5,
            seo_warning_count=0,
            seo_fail_count=0,
        )
        response = AuditResponse(
            audit_id="abc-123",
            download_url="/api/v1/reports/abc-123",
            summary=summary,
        )
        self.assertEqual(response.summary.page_title, "Example")


class TestSeoAuditReport(unittest.TestCase):
    def _sample_report(self) -> SeoAuditReport:
        return SeoAuditReport(
            url="https://www.milestoneinternet.com/",
            generated_at=datetime.now(timezone.utc),
            page_details=PageDetails(
                title="Test",
                meta_description="Desc",
                canonical_url="https://www.milestoneinternet.com/",
                h1_tags=["H1"],
                h2_tags=["H2"],
                image_count=5,
                missing_alt_count=1,
                word_count=300,
            ),
            seo_checks=SeoChecks(
                title_check="PASS",
                meta_description_check="PASS",
                h1_check="PASS",
                alt_text_check="WARNING",
                content_length_check="PASS",
            ),
            core_web_vitals=CoreWebVitals(
                mobile=PerformanceMetrics(performance_score=70.0, lcp="2.5 s"),
                desktop=PerformanceMetrics(performance_score=90.0, lcp="1.5 s"),
            ),
            ai_analysis=AiAnalysis(
                technical_seo_findings=["Finding"],
                content_findings=["Content finding"],
                core_web_vitals_findings=["CWV finding"],
                recommended_improvements=["Improvement"],
                suggested_title="Title",
                suggested_meta_description="Meta",
            ),
        )

    def test_report_serialization_uses_core_web_vitals_key(self):
        report = self._sample_report()
        payload = json.loads(report.model_dump_json())
        self.assertIn("core_web_vitals", payload)
        self.assertNotIn("pagespeed", payload)
        self.assertIn("mobile", payload["core_web_vitals"])
        self.assertIn("desktop", payload["core_web_vitals"])

    def test_report_required_top_level_fields(self):
        report = self._sample_report()
        payload = json.loads(report.model_dump_json())
        self.assertEqual(
            set(payload.keys()),
            {
                "url",
                "generated_at",
                "page_details",
                "seo_checks",
                "core_web_vitals",
                "ai_analysis",
            },
        )

    def test_build_audit_summary_counts_statuses(self):
        summary = build_audit_summary(self._sample_report())
        self.assertEqual(summary.seo_pass_count, 4)
        self.assertEqual(summary.seo_warning_count, 1)
        self.assertEqual(summary.seo_fail_count, 0)
        self.assertEqual(summary.mobile_performance_score, 70.0)
        self.assertIn("Improvement", summary.recommended_improvements)

    def test_seo_checks_reject_invalid_status(self):
        with self.assertRaises(ValidationError):
            SeoChecks(
                title_check="INVALID",
                meta_description_check="PASS",
                h1_check="PASS",
                alt_text_check="PASS",
                content_length_check="PASS",
            )

    def test_ai_analysis_validates_structure(self):
        analysis = AiAnalysis.model_validate(
            {
                "technical_seo_findings": ["Issue"],
                "content_findings": [],
                "core_web_vitals_findings": [],
                "recommended_improvements": [],
                "suggested_title": "",
                "suggested_meta_description": "",
            }
        )
        self.assertEqual(analysis.technical_seo_findings, ["Issue"])


if __name__ == "__main__":
    unittest.main()
