import asyncio
import time

import httpx

from core.config import settings
from core.exceptions import PageSpeedError
from core.logging import get_logger, log_pagespeed_latency
from models.report import CoreWebVitals, PerformanceMetrics
from util.http_client import create_http_client

logger = get_logger(__name__)


def parse_pagespeed_response(payload: dict) -> PerformanceMetrics:
    lighthouse = payload.get("lighthouseResult", {})
    categories = lighthouse.get("categories", {})
    audits = lighthouse.get("audits", {})

    performance_score = None
    performance = categories.get("performance", {})
    if performance.get("score") is not None:
        performance_score = round(float(performance["score"]) * 100, 1)

    inp_audit = audits.get("experimental-interaction-to-next-paint") or audits.get(
        "interaction-to-next-paint"
    )
    tbt_audit = audits.get("total-blocking-time")
    inp_or_tbt = _audit_display_value(inp_audit) or _audit_display_value(tbt_audit)

    return PerformanceMetrics(
        performance_score=performance_score,
        lcp=_audit_display_value(audits.get("largest-contentful-paint")),
        cls=_audit_display_value(audits.get("cumulative-layout-shift")),
        fcp=_audit_display_value(audits.get("first-contentful-paint")),
        speed_index=_audit_display_value(audits.get("speed-index")),
        inp_or_tbt=inp_or_tbt,
    )


def _audit_display_value(audit: dict | None) -> str | None:
    if not audit:
        return None

    display_value = audit.get("displayValue")
    if display_value:
        return str(display_value)

    numeric_value = audit.get("numericValue")
    if numeric_value is None:
        return None

    numeric_unit = audit.get("numericUnit", "")
    if numeric_unit:
        return f"{numeric_value} {numeric_unit}".strip()

    return str(numeric_value)


async def fetch_core_web_vitals(
    url: str,
    audit_id: str,
    client: httpx.AsyncClient | None = None,
) -> CoreWebVitals:
    if not settings.PAGESPEED_API_KEY:
        raise PageSpeedError("PageSpeed API key is not configured")

    owns_client = client is None
    if owns_client:
        client = create_http_client(timeout_seconds=settings.PAGESPEED_TIMEOUT_SECONDS)

    try:
        mobile_task = _fetch_strategy(url, "mobile", audit_id, client)
        desktop_task = _fetch_strategy(url, "desktop", audit_id, client)
        mobile, desktop = await asyncio.gather(mobile_task, desktop_task)
        return CoreWebVitals(mobile=mobile, desktop=desktop)
    finally:
        if owns_client and client is not None:
            await client.aclose()


async def _fetch_strategy(
    url: str,
    strategy: str,
    audit_id: str,
    client: httpx.AsyncClient,
) -> PerformanceMetrics:
    params = {
        "url": url,
        "strategy": strategy,
        "category": settings.PAGESPEED_CATEGORY,
        "key": settings.PAGESPEED_API_KEY,
    }

    started_at = time.perf_counter()
    try:
        response = await client.get(settings.PAGESPEED_API_URL, params=params)
        response.raise_for_status()
        payload = response.json()
        return parse_pagespeed_response(payload)
    except httpx.TimeoutException as exc:
        raise PageSpeedError(
            f"PageSpeed Insights request timed out for {strategy}"
        ) from exc
    except httpx.HTTPStatusError as exc:
        raise PageSpeedError(
            f"PageSpeed Insights returned HTTP {exc.response.status_code} for {strategy}"
        ) from exc
    except httpx.RequestError as exc:
        raise PageSpeedError(
            f"Unable to reach PageSpeed Insights API for {strategy}: {exc}"
        ) from exc
    except Exception as exc:
        raise PageSpeedError(
            f"Failed to parse PageSpeed Insights response for {strategy}: {exc}"
        ) from exc
    finally:
        latency_ms = (time.perf_counter() - started_at) * 1000
        log_pagespeed_latency(
            logger,
            audit_id=audit_id,
            strategy=strategy,
            pagespeed_latency_ms=latency_ms,
        )
