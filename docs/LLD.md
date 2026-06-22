# Low-Level Design (LLD) — SEO Insight AI

## 1. Module Structure

```text
main.py
api/
  route.py              # Mounts /api/v1 routers
  ui.py                 # Serves static/index.html at /
  v1/
    audit.py            # POST /audit, GET /health/
    reports.py          # GET /reports/{audit_id}
core/
  config.py             # pydantic-settings (loads .env)
  logging.py            # JSON structured logging helpers
  exceptions.py         # Domain exceptions
models/
  requests.py           # AuditRequest
  responses.py          # AuditResponse, AuditSummary
  report.py             # SeoAuditReport and sub-models
services/
  audit_service.py      # Orchestration, persistence, summary building
  scraper.py            # HTML fetch + parse
  seo_validator.py      # Rule-based SEO checks
  pagespeed.py          # PageSpeed Insights integration
  openai_analyzer.py    # OpenAI structured analysis
prompts/
  seo_analysis.py       # System/user prompt templates
util/
  url_validator.py      # URL validation + SSRF checks
  http_client.py        # Shared httpx.AsyncClient factory
  cache.py              # Redis cache + URL normalization
  langfuse_tracing.py   # Langfuse init + trace helpers
  common.py             # HTTP exception handler
static/
  index.html            # Web UI
tests/
  test_audit.py
  test_models.py
  test_pagespeed.py
  test_services.py
  test_url_validator.py
```

## 2. API Contracts

### GET `/`

Serves the Web UI (`static/index.html`). Not included in OpenAPI schema.

### GET `/api/v1/health/`

**Response**

```json
{
  "status": "healthy",
  "service": "SEO Insight AI"
}
```

### POST `/api/v1/audit`

**Request**

```json
{
  "url": "https://www.milestoneinternet.com/"
}
```

`url` is validated as a Pydantic `HttpUrl` before reaching the audit service.

**Response**

```json
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
      "content_length_check": "PASS"
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
    "suggested_meta_description": "Optimized meta description."
  }
}
```

### GET `/api/v1/reports/{audit_id}`

Returns `seo_audit_report.json` as a downloadable file. `audit_id` must be a valid UUID v4.

## 3. Core Data Models

### `PageDetails`

- `title`, `meta_description`, `canonical_url`
- `h1_tags`, `h2_tags`
- `image_count`, `missing_alt_count`, `word_count`

### `SeoChecks`

- `title_check`, `meta_description_check`, `h1_check`, `alt_text_check`, `content_length_check`

Allowed values: `PASS`, `FAIL`, `WARNING`

### `PerformanceMetrics`

- `performance_score`
- `lcp`, `cls`, `fcp`, `speed_index`, `inp_or_tbt`

### `CoreWebVitals`

- `mobile` — `PerformanceMetrics`
- `desktop` — `PerformanceMetrics`

### `AiAnalysis`

- `technical_seo_findings`, `content_findings`, `core_web_vitals_findings`
- `recommended_improvements`
- `suggested_title`, `suggested_meta_description`

### `AuditSummary`

Condensed view built from `SeoAuditReport` for inline API responses. Includes page metadata, SEO check counts, performance scores, key findings, and top recommendations.

### `SeoAuditReport`

Full persisted report combining `url`, `generated_at`, `page_details`, `seo_checks`, `core_web_vitals`, and `ai_analysis`.

## 4. Audit Service Flow

```python
@traced("seo-audit", as_type="span")
async def run_audit(url):
    audit_id = uuid4()
    with langfuse_session(session_id=audit_id, metadata={...}, tags=["seo-audit"]):
        return await _run_audit_workflow(url, audit_id, started_at)

async def _run_audit_workflow(url, audit_id, started_at):
    normalized_url = normalize_audit_url(url)

    # 1. Cache lookup (before URL validation)
    cached = await _lookup_cached_audit(normalized_url, ...)
    if cached:
        flush_langfuse()
        return cached

    # 2. Validate URL (SSRF-safe)
    validated_url = validate_url(url)
    normalized_url = normalize_audit_url(validated_url)

    # 3. Fallback cache lookup if normalization changed
    ...

    log_audit_start(...)

    # 4. Concurrent data collection (separate HTTP clients)
    http_client = create_http_client()
    pagespeed_client = create_http_client(timeout_seconds=PAGESPEED_TIMEOUT_SECONDS)
    page_details, core_web_vitals = await asyncio.gather(...)

    # 5. Analysis and persistence
    seo_checks = validate_seo(page_details)
    ai_analysis = await analyze_seo(...)   # @traced generation span
    report = SeoAuditReport(...)
    save_report(audit_id, report)

    response = build_audit_response(audit_id, report)
    await set_cached_audit(normalized_url, response.model_dump(mode="json"))
    log_audit_complete(...)
    flush_langfuse()
    return response
```

`main.py` calls `init_langfuse()` on startup and `shutdown_langfuse()` on shutdown (flushes pending traces).

## 5. Redis Cache Design

Configured via `REDIS_URL` and `AUDIT_CACHE_TTL_SECONDS` (default 86400s).

| Concern | Implementation |
|---------|----------------|
| Cache key | `audit-cache:{normalized_url}` |
| URL normalization | Lowercase host, strip `www.`, strip trailing slash, remove query/fragment |
| Stored value | Full `AuditResponse` JSON (including `summary`) |
| Cache hit | Return cached response; load report from disk if `summary` is missing (legacy entries) |
| Redis unavailable | Log warning, skip cache read/write, audit proceeds normally |

## 6. Langfuse Cloud Tracing

All Langfuse settings live in the shared `.env` file (see `example.env`).

| Variable | Purpose |
|----------|---------|
| `LANGFUSE_ENABLED` | Must be `true` to send traces (keys alone are not enough) |
| `LANGFUSE_PUBLIC_KEY` | Project public key from Langfuse Cloud |
| `LANGFUSE_SECRET_KEY` | Project secret key from Langfuse Cloud |
| `LANGFUSE_HOST` | `https://cloud.langfuse.com` (EU) or `https://us.cloud.langfuse.com` (US) |

Uses the Langfuse **free cloud plan** — no self-hosted Postgres, ClickHouse, Redis, or MinIO for Langfuse. The Python SDK (`langfuse` package) sends traces directly to Langfuse Cloud.

### Implementation (`util/langfuse_tracing.py`)

| Function | Purpose |
|----------|---------|
| `init_langfuse()` | Sets SDK env vars on startup; logs warning if keys set but `LANGFUSE_ENABLED=false` |
| `shutdown_langfuse()` | Flushes pending traces on app shutdown |
| `flush_langfuse()` | Flushes traces after each audit |
| `langfuse_session()` | Wraps audit with `propagate_attributes` (session ID, metadata, tags) |
| `traced()` | Applies Langfuse `@observe` decorator to spans/generations |
| `update_current_span_attrs()` | Updates span metadata (e.g. cache hits) |
| `update_current_generation()` | Records model, I/O, token `usage_details`, errors |

### Traced observations

| Observation | Type | Module | Captures |
|-------------|------|--------|----------|
| `seo-audit` | Span | `audit_service.run_audit` | URL, audit ID, session, cache hits |
| `openai-seo-analysis` | Generation | `openai_analyzer.analyze_seo` | Model, messages, output, tokens, latency, errors |

Tracing is active only when `LANGFUSE_ENABLED=true` **and** both API keys are set. Cached audits still create a span but skip the OpenAI generation trace.

## 7. Scraper Design

- Uses shared `create_http_client()` with `HTTP_TIMEOUT_SECONDS`, redirect limit, and user-agent
- Streams response body with `MAX_RESPONSE_BYTES` cap
- Parses HTML with BeautifulSoup
- Extracts SEO metadata only; raw HTML is never sent to OpenAI

### Word Count Logic

- Removes `script`, `style`, and `noscript` tags from parsed content
- Counts remaining visible text words

## 8. SEO Validation Rules

| Check | PASS | WARNING | FAIL |
|-------|------|---------|------|
| Title | 10–60 chars | Present but outside range | Missing |
| Meta description | 50–160 chars | Present but outside range | Missing |
| H1 | Exactly one | Multiple H1 tags | No H1 |
| Alt text | No images or all images have alt | Some images missing alt | All images missing alt |
| Content length | >= 300 words | 100–299 words | < 100 words |

## 9. PageSpeed Integration

- Endpoint: configurable via `PAGESPEED_API_URL` (default Google PageSpeed v5)
- Strategies: `mobile`, `desktop` (fetched concurrently)
- Timeout: `PAGESPEED_TIMEOUT_SECONDS` (default 120s) via dedicated HTTP client
- Lighthouse performance score and audit display values mapped into `PerformanceMetrics`
- Uses INP when available, otherwise TBT

## 10. OpenAI Integration

- Direct OpenAI SDK usage (no LangChain)
- Temperature: `0.2` (configurable)
- Model: `OPENAI_MODEL` (default `gpt-4o-mini`)
- Structured output validated with `AiAnalysis` Pydantic model via `chat.completions.parse`
- Prompt includes only page metadata, SEO check results, and Core Web Vitals metrics

## 11. Logging

Structured JSON logs include:

| Event | When |
|-------|------|
| `application_startup` / `application_shutdown` | App lifespan |
| `langfuse_enabled` | Langfuse tracing initialized successfully |
| `audit_start` | New audit begins (cache miss) |
| `audit_complete` | Audit finished with `audit_duration_ms` |
| `audit_cache_hit` / `audit_cache_miss` / `audit_cache_write` | Redis cache operations |
| `pagespeed_latency` | Per-strategy PageSpeed timing |
| `openai_latency` | OpenAI call timing + token usage |
| `redis_cache_disabled` | Redis configured but unavailable |
| `error` | Failures with context fields |

## 12. Error Handling

| Failure | HTTP Status |
|---------|-------------|
| Invalid URL | 400 |
| Invalid audit ID format | 400 |
| Scrape timeout | 504 |
| Scrape / PageSpeed / OpenAI failure | 502 |
| Missing report | 404 |
| Unexpected server error | 500 |

All HTTP errors return:

```json
{
  "status_code": 400,
  "message": "Error detail",
  "data": null
}
```

## 13. Security Controls

- URL scheme restricted to `http` and `https`
- Hostname/IP SSRF checks (private, loopback, link-local, reserved ranges blocked)
- Embedded credentials in URLs rejected
- Redirect and response size limits on HTTP fetches
- UUID validation before report download

## 14. Persistence

| Store | Location | Content |
|-------|----------|---------|
| Reports | `reports/{audit_id}.json` | Full `SeoAuditReport` |
| Cache | Redis `audit-cache:{normalized_url}` | Full `AuditResponse` with TTL |

## 15. Web UI

`static/index.html` provides:

- URL input and audit trigger
- Summary dashboard (performance scores, SEO checks, recommendations)
- Download link for full report
- Toggle for raw JSON response

## 16. Testing Strategy

Unit tests cover:

- Pydantic model validation (`AuditResponse`, `AuditSummary`, `SeoAuditReport`)
- URL validation and SSRF checks
- HTML parsing
- SEO rule evaluation
- PageSpeed response parsing
- Audit orchestration and API endpoints (mocked external calls)
- Cache hit behavior (mocked Redis)

Run tests:

```bash
pipenv run python -m unittest discover -s tests -v
```
