#!/usr/bin/env python3
"""Generate a sample SEO audit report for the assignment homepage."""

import asyncio
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from core.config import settings
from core.logging import setup_logging
from models.report import AiAnalysis, SeoAuditReport
from services.audit_service import get_report_path, run_audit, save_report
from services.pagespeed import fetch_core_web_vitals
from services.scraper import scrape_page
from services.seo_validator import validate_seo
from util.http_client import create_http_client

SAMPLE_URL = "https://www.milestoneinternet.com/"
OUTPUT_DIR = Path("output")
SAMPLE_REPORT_NAME = "seo_audit_report.json"


def _build_deterministic_ai_analysis(page_details, seo_checks, core_web_vitals) -> AiAnalysis:
    technical_findings: list[str] = []
    content_findings: list[str] = []
    cwv_findings: list[str] = []
    improvements: list[str] = []

    if seo_checks.title_check != "PASS":
        technical_findings.append(f"Title check result: {seo_checks.title_check}.")
        improvements.append("Add or refine the page title to meet SEO length guidelines.")
    if seo_checks.meta_description_check != "PASS":
        technical_findings.append(f"Meta description check result: {seo_checks.meta_description_check}.")
        improvements.append("Add or refine the meta description to meet SEO length guidelines.")
    if seo_checks.h1_check != "PASS":
        content_findings.append(f"H1 check result: {seo_checks.h1_check}.")
        improvements.append("Ensure the page has a single clear H1 heading.")
    if seo_checks.alt_text_check != "PASS":
        technical_findings.append(
            f"Alt text check result: {seo_checks.alt_text_check} "
            f"({page_details.missing_alt_count} of {page_details.image_count} images missing alt text)."
        )
        improvements.append("Add descriptive alt text to images missing alt attributes.")
    if seo_checks.content_length_check != "PASS":
        content_findings.append(
            f"Content length check result: {seo_checks.content_length_check} "
            f"(word count: {page_details.word_count})."
        )
        improvements.append("Increase on-page content depth to improve topical coverage.")

    if page_details.canonical_url:
        technical_findings.append("Canonical URL is present.")
    else:
        technical_findings.append("Canonical URL is missing.")
        improvements.append("Add a canonical link element to reduce duplicate-content risk.")

    for strategy, metrics in (
        ("mobile", core_web_vitals.mobile),
        ("desktop", core_web_vitals.desktop),
    ):
        if metrics.performance_score is not None:
            cwv_findings.append(
                f"{strategy.capitalize()} performance score: {metrics.performance_score}."
            )
        if metrics.lcp:
            cwv_findings.append(f"{strategy.capitalize()} LCP: {metrics.lcp}.")
        if metrics.cls:
            cwv_findings.append(f"{strategy.capitalize()} CLS: {metrics.cls}.")

    suggested_title = page_details.title or "Add a descriptive, keyword-focused page title"
    suggested_meta_description = (
        page_details.meta_description
        or "Add a compelling meta description between 50 and 160 characters."
    )

    return AiAnalysis(
        technical_seo_findings=technical_findings,
        content_findings=content_findings,
        core_web_vitals_findings=cwv_findings,
        recommended_improvements=improvements,
        suggested_title=suggested_title,
        suggested_meta_description=suggested_meta_description,
    )


async def _generate_without_openai(audit_id: str) -> Path:
    if not settings.PAGESPEED_API_KEY:
        raise SystemExit("PAGESPEED_API_KEY is required.")

    client = create_http_client()
    try:
        page_details = await scrape_page(SAMPLE_URL, client=client)
        core_web_vitals = await fetch_core_web_vitals(SAMPLE_URL, audit_id)
    finally:
        await client.aclose()

    seo_checks = validate_seo(page_details)
    ai_analysis = _build_deterministic_ai_analysis(page_details, seo_checks, core_web_vitals)
    report = SeoAuditReport(
        url=SAMPLE_URL,
        generated_at=datetime.now(timezone.utc),
        page_details=page_details,
        seo_checks=seo_checks,
        core_web_vitals=core_web_vitals,
        ai_analysis=ai_analysis,
    )
    return save_report(audit_id, report)


def _copy_report(report_path: Path) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    destination = OUTPUT_DIR / SAMPLE_REPORT_NAME
    root_destination = Path(SAMPLE_REPORT_NAME)
    shutil.copyfile(report_path, destination)
    shutil.copyfile(report_path, root_destination)
    print(f"Sample report saved to: {destination}")
    print(f"Copy also saved to: {root_destination}")


async def main() -> None:
    setup_logging()
    print(f"Running SEO audit for {SAMPLE_URL}...")

    if settings.OPENAI_API_KEY:
        response = await run_audit(SAMPLE_URL)
        report_path = get_report_path(response.audit_id)
        if report_path is None:
            raise SystemExit("Audit completed but report file was not found.")
        print(f"Audit ID: {response.audit_id}")
        _copy_report(report_path)
        return

    print("OPENAI_API_KEY not set. Generating sample with deterministic analysis fallback.")
    audit_id = "sample-milestone-audit"
    report_path = await _generate_without_openai(audit_id)
    print(f"Audit ID: {audit_id}")
    _copy_report(report_path)


if __name__ == "__main__":
    asyncio.run(main())
