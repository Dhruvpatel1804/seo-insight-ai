from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

CheckStatus = Literal["PASS", "FAIL", "WARNING"]


class PageDetails(BaseModel):
    title: str = ""
    meta_description: str = ""
    canonical_url: str = ""
    h1_tags: list[str] = Field(default_factory=list)
    h2_tags: list[str] = Field(default_factory=list)
    image_count: int = 0
    missing_alt_count: int = 0
    word_count: int = 0


class SeoChecks(BaseModel):
    title_check: CheckStatus
    meta_description_check: CheckStatus
    h1_check: CheckStatus
    alt_text_check: CheckStatus
    content_length_check: CheckStatus


class PerformanceMetrics(BaseModel):
    performance_score: float | None = None
    lcp: str | None = None
    cls: str | None = None
    fcp: str | None = None
    speed_index: str | None = None
    inp_or_tbt: str | None = None


class CoreWebVitals(BaseModel):
    mobile: PerformanceMetrics = Field(default_factory=PerformanceMetrics)
    desktop: PerformanceMetrics = Field(default_factory=PerformanceMetrics)


class AiAnalysis(BaseModel):
    technical_seo_findings: list[str] = Field(default_factory=list)
    content_findings: list[str] = Field(default_factory=list)
    core_web_vitals_findings: list[str] = Field(default_factory=list)
    recommended_improvements: list[str] = Field(default_factory=list)
    suggested_title: str = ""
    suggested_meta_description: str = ""


class SeoAuditReport(BaseModel):
    url: str
    generated_at: datetime
    page_details: PageDetails
    seo_checks: SeoChecks
    core_web_vitals: CoreWebVitals
    ai_analysis: AiAnalysis

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "url": "https://www.milestoneinternet.com/",
                    "generated_at": "2026-06-22T12:00:00+00:00",
                    "page_details": {
                        "title": "Example Title",
                        "meta_description": "Example meta description",
                        "canonical_url": "https://www.milestoneinternet.com/",
                        "h1_tags": ["Welcome"],
                        "h2_tags": ["About Us"],
                        "image_count": 10,
                        "missing_alt_count": 2,
                        "word_count": 500,
                    },
                    "seo_checks": {
                        "title_check": "PASS",
                        "meta_description_check": "PASS",
                        "h1_check": "PASS",
                        "alt_text_check": "WARNING",
                        "content_length_check": "PASS",
                    },
                    "core_web_vitals": {
                        "mobile": {
                            "performance_score": 72.0,
                            "lcp": "2.5 s",
                            "cls": "0.05",
                            "fcp": "1.2 s",
                            "speed_index": "3.1 s",
                            "inp_or_tbt": "150 ms",
                        },
                        "desktop": {
                            "performance_score": 90.0,
                            "lcp": "1.8 s",
                            "cls": "0.02",
                            "fcp": "0.9 s",
                            "speed_index": "2.0 s",
                            "inp_or_tbt": "80 ms",
                        },
                    },
                    "ai_analysis": {
                        "technical_seo_findings": ["Canonical URL is present."],
                        "content_findings": ["H1 tag is present and descriptive."],
                        "core_web_vitals_findings": ["Mobile LCP is within acceptable range."],
                        "recommended_improvements": ["Add alt text to 2 images."],
                        "suggested_title": "Optimized Page Title",
                        "suggested_meta_description": "Optimized meta description for search visibility.",
                    },
                }
            ]
        }
    }
