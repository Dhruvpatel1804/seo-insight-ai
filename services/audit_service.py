import asyncio
import json
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

from core.config import settings
from core.exceptions import InvalidURLError
from core.logging import (
    get_logger,
    log_audit_complete,
    log_audit_start,
    log_cache_event,
    log_error,
)
from models.report import SeoAuditReport
from models.responses import AuditResponse, AuditSummary
from services.openai_analyzer import analyze_seo
from services.pagespeed import fetch_core_web_vitals
from services.scraper import scrape_page
from services.seo_validator import validate_seo
from util.cache import get_audit_cache_key, get_cached_audit, normalize_audit_url, set_cached_audit
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


def load_report(audit_id: str) -> SeoAuditReport | None:
    path = get_report_path(audit_id)
    if path is None:
        return None
    return SeoAuditReport.model_validate_json(path.read_text(encoding="utf-8"))


def _count_seo_statuses(seo_checks) -> tuple[int, int, int]:
    statuses = seo_checks.model_dump().values()
    return (
        sum(status == "PASS" for status in statuses),
        sum(status == "WARNING" for status in statuses),
        sum(status == "FAIL" for status in statuses),
    )


def _build_key_findings(ai_analysis) -> list[str]:
    findings: list[str] = []
    for field_name in (
        "technical_seo_findings",
        "content_findings",
        "core_web_vitals_findings",
    ):
        for finding in getattr(ai_analysis, field_name):
            if finding and finding not in findings:
                findings.append(finding)
            if len(findings) >= 5:
                return findings
    return findings


def build_audit_summary(report: SeoAuditReport) -> AuditSummary:
    pass_count, warning_count, fail_count = _count_seo_statuses(report.seo_checks)
    return AuditSummary(
        url=report.url,
        generated_at=report.generated_at,
        page_title=report.page_details.title,
        meta_description=report.page_details.meta_description,
        word_count=report.page_details.word_count,
        image_count=report.page_details.image_count,
        missing_alt_count=report.page_details.missing_alt_count,
        seo_checks=report.seo_checks,
        seo_pass_count=pass_count,
        seo_warning_count=warning_count,
        seo_fail_count=fail_count,
        mobile_performance_score=report.core_web_vitals.mobile.performance_score,
        desktop_performance_score=report.core_web_vitals.desktop.performance_score,
        mobile_lcp=report.core_web_vitals.mobile.lcp,
        desktop_lcp=report.core_web_vitals.desktop.lcp,
        key_findings=_build_key_findings(report.ai_analysis),
        recommended_improvements=report.ai_analysis.recommended_improvements[:5],
        suggested_title=report.ai_analysis.suggested_title,
        suggested_meta_description=report.ai_analysis.suggested_meta_description,
    )


def build_audit_response(audit_id: str, report: SeoAuditReport) -> AuditResponse:
    return AuditResponse(
        audit_id=audit_id,
        download_url=f"/api/v1/reports/{audit_id}",
        summary=build_audit_summary(report),
    )


def response_from_cache(cached_audit: dict) -> AuditResponse:
    response = AuditResponse(**cached_audit)
    if response.summary is not None:
        return response

    report = load_report(response.audit_id)
    if report is None:
        return response
    return build_audit_response(response.audit_id, report)


async def _lookup_cached_audit(
    normalized_url: str,
    *,
    audit_id: str,
    log_url: str,
) -> AuditResponse | None:
    cache_key = get_audit_cache_key(normalized_url)
    try:
        cached_audit = await get_cached_audit(normalized_url)
    except Exception as exc:
        log_error(logger, message=f"Redis cache lookup failed: {exc}", url=log_url)
        return None

    if not cached_audit:
        log_cache_event(
            logger,
            "audit_cache_miss",
            audit_id=audit_id,
            url=log_url,
            normalized_url=normalized_url,
            cache_key=cache_key,
        )
        return None

    log_cache_event(
        logger,
        "audit_cache_hit",
        audit_id=cached_audit.get("audit_id"),
        url=log_url,
        normalized_url=normalized_url,
        cache_key=cache_key,
    )
    return response_from_cache(cached_audit)


async def run_audit(url: str) -> AuditResponse:
    started_at = time.perf_counter()
    audit_id = str(uuid.uuid4())
    normalized_input_url = normalize_audit_url(url)

    cached_response = await _lookup_cached_audit(
        normalized_input_url,
        audit_id=audit_id,
        log_url=url,
    )
    if cached_response:
        return cached_response

    try:
        validated_url = validate_url(url)
    except InvalidURLError as exc:
        log_error(logger, message=exc.message, audit_id=audit_id, url=url)
        raise

    normalized_url = normalize_audit_url(validated_url)
    if normalized_url != normalized_input_url:
        cached_response = await _lookup_cached_audit(
            normalized_url,
            audit_id=audit_id,
            log_url=validated_url,
        )
        if cached_response:
            return cached_response

    log_audit_start(logger, audit_id=audit_id, url=validated_url)

    http_client = create_http_client()
    pagespeed_client = create_http_client(timeout_seconds=settings.PAGESPEED_TIMEOUT_SECONDS)
    try:
        page_details, core_web_vitals = await asyncio.gather(
            scrape_page(validated_url, client=http_client),
            fetch_core_web_vitals(validated_url, audit_id, client=pagespeed_client),
        )
    finally:
        await asyncio.gather(http_client.aclose(), pagespeed_client.aclose())

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

    response = build_audit_response(audit_id, report)
    try:
        await set_cached_audit(normalized_url, response.model_dump(mode="json"))
        log_cache_event(
            logger,
            "audit_cache_write",
            audit_id=audit_id,
            url=validated_url,
            normalized_url=normalized_url,
            cache_key=get_audit_cache_key(normalized_url),
            ttl_seconds=settings.AUDIT_CACHE_TTL_SECONDS,
        )
    except Exception as exc:
        log_error(logger, message=f"Redis cache write failed: {exc}", url=validated_url)
    return response
