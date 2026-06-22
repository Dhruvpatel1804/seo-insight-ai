from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from models.report import SeoChecks


class AuditSummary(BaseModel):
    url: str
    generated_at: datetime
    page_title: str = ""
    meta_description: str = ""
    word_count: int = 0
    image_count: int = 0
    missing_alt_count: int = 0
    seo_checks: SeoChecks
    seo_pass_count: int = 0
    seo_warning_count: int = 0
    seo_fail_count: int = 0
    mobile_performance_score: float | None = None
    desktop_performance_score: float | None = None
    mobile_lcp: str | None = None
    desktop_lcp: str | None = None
    key_findings: list[str] = Field(default_factory=list)
    recommended_improvements: list[str] = Field(default_factory=list)
    suggested_title: str = ""
    suggested_meta_description: str = ""


class AuditResponse(BaseModel):
    audit_id: str
    status: Literal["completed"] = "completed"
    download_url: str
    summary: AuditSummary | None = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "audit_id": "550e8400-e29b-41d4-a716-446655440000",
                    "status": "completed",
                    "download_url": "/api/v1/reports/550e8400-e29b-41d4-a716-446655440000",
                    "summary": {
                        "url": "https://www.milestoneinternet.com/",
                        "generated_at": "2026-06-22T12:00:00+00:00",
                        "page_title": "Example Title",
                        "meta_description": "Example meta description",
                        "word_count": 500,
                        "image_count": 10,
                        "missing_alt_count": 2,
                        "seo_checks": {
                            "title_check": "PASS",
                            "meta_description_check": "PASS",
                            "h1_check": "PASS",
                            "alt_text_check": "WARNING",
                            "content_length_check": "PASS",
                        },
                        "seo_pass_count": 4,
                        "seo_warning_count": 1,
                        "seo_fail_count": 0,
                        "mobile_performance_score": 72.0,
                        "desktop_performance_score": 90.0,
                        "mobile_lcp": "2.5 s",
                        "desktop_lcp": "1.8 s",
                        "key_findings": ["Canonical URL is present."],
                        "recommended_improvements": ["Add alt text to 2 images."],
                        "suggested_title": "Optimized Page Title",
                        "suggested_meta_description": "Optimized meta description.",
                    },
                }
            ]
        }
    }
