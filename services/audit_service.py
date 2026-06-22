import asyncio
import json
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

from core.config import settings
from core.exceptions import InvalidURLError
from core.logging import get_logger, log_audit_complete, log_audit_start, log_error
from models.report import SeoAuditReport
from models.responses import AuditResponse
from services.openai_analyzer import analyze_seo
from services.pagespeed import fetch_core_web_vitals
from services.scraper import scrape_page
from services.seo_validator import validate_seo
from util.http_client import create_http_client
from util.url_validator import validate_url

logger = get_logger(__name__)


def _reports_dir() -> Path:
    path = Path(settings.REPORTS_DIR)
    path.mkdir(parents=True, exist_ok=True)
    return path


def _report_path(audit_id: str) -> Path:
    return _reports_dir() / f"{audit_id}.json"


def save_report(audit_id: str, report: SeoAuditReport) -> Path:
    path = _report_path(audit_id)
    path.write_text(
        json.dumps(report.model_dump(mode="json"), indent=2),
        encoding="utf-8",
    )
    return path


def get_report_path(audit_id: str) -> Path | None:
    path = _report_path(audit_id)
    if path.is_file():
        return path
    return None


async def run_audit(url: str) -> AuditResponse:
    started_at = time.perf_counter()
    audit_id = str(uuid.uuid4())

    try:
        validated_url = validate_url(url)
    except InvalidURLError as exc:
        log_error(logger, message=exc.message, audit_id=audit_id, url=url)
        raise

    log_audit_start(logger, audit_id=audit_id, url=validated_url)

    client = create_http_client()
    try:
        page_details, core_web_vitals = await asyncio.gather(
            scrape_page(validated_url, client=client),
            fetch_core_web_vitals(validated_url, audit_id),
        )
    finally:
        await client.aclose()

    seo_checks = validate_seo(page_details)
    ai_analysis = await analyze_seo(
        audit_id=audit_id,
        url=validated_url,
        page_details=page_details,
        seo_checks=seo_checks,
        core_web_vitals=core_web_vitals,
    )

    report = SeoAuditReport(
        url=validated_url,
        generated_at=datetime.now(timezone.utc),
        page_details=page_details,
        seo_checks=seo_checks,
        core_web_vitals=core_web_vitals,
        ai_analysis=ai_analysis,
    )
    save_report(audit_id, report)

    audit_duration_ms = (time.perf_counter() - started_at) * 1000
    log_audit_complete(
        logger,
        audit_id=audit_id,
        url=validated_url,
        audit_duration_ms=audit_duration_ms,
    )

    return AuditResponse(
        audit_id=audit_id,
        download_url=f"/api/v1/reports/{audit_id}",
    )
