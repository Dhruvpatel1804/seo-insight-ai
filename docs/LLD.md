# Low-Level Design (LLD) — SEO Insight AI

## 1. Module Structure

```text
main.py
api/
  route.py
  ui.py
  v1/
    audit.py
    reports.py
core/
  config.py
  logging.py
  exceptions.py
models/
  requests.py
  responses.py
  report.py
services/
  audit_service.py
  scraper.py
  seo_validator.py
  pagespeed.py
  openai_analyzer.py
prompts/
  seo_analysis.py
util/
  url_validator.py
  http_client.py
  cache.py
static/
  index.html
```

## 2. API Contracts

### POST `/api/v1/audit`

**Request**

```json
{
  "url": "https://www.milestoneinternet.com/"
}
```

**Response**

```json
{
  "audit_id": "uuid",
  "status": "completed",
  "download_url": "/api/v1/reports/{audit_id}",
  "summary": {}
}
```

### GET `/api/v1/reports/{audit_id}`

Returns `seo_audit_report.json` as a downloadable file.

## 3. Core Data Models

### `PageDetails`

- `title`, `meta_description`, `canonical_url`
- `h1_tags`, `h2_tags`
- `image_count`, `missing_alt_count`, `word_count`

### `SeoChecks`

- `title_check`
- `meta_description_check`
- `h1_check`
- `alt_text_check`
- `content_length_check`

Allowed values: `PASS`, `FAIL`, `WARNING`

### `PerformanceMetrics`

- `performance_score`
- `lcp`, `cls`, `fcp`, `speed_index`, `inp_or_tbt`

### `CoreWebVitals`

- `mobile`
- `desktop`

### `AiAnalysis`

- `technical_seo_findings`
- `content_findings`
- `core_web_vitals_findings`
- `recommended_improvements`
- `suggested_title`
- `suggested_meta_description`

## 4. Audit Service Flow

```python
audit_id = uuid4()
validate_url(url)
log_audit_start(...)

async with shared httpx client:
    page_details, core_web_vitals = await asyncio.gather(
        scrape_page(url),
        fetch_core_web_vitals(url, audit_id),
    )

seo_checks = validate_seo(page_details)
ai_analysis = await analyze_seo(...)
report = SeoAuditReport(...)
save_report(audit_id, report)
log_audit_complete(...)
return AuditResponse(...)
```

## 5. Scraper Design

- Uses `httpx.AsyncClient` with timeout, redirect limit, and response size cap
- Parses HTML with BeautifulSoup
- Extracts SEO metadata only
- Does not send raw HTML to OpenAI

### Word Count Logic

- Removes `script`, `style`, and `noscript` tags
- Counts remaining visible text words

## 6. SEO Validation Rules

| Check | PASS | WARNING | FAIL |
|-------|------|---------|------|
| Title | 10–60 chars | Present but outside range | Missing |
| Meta description | 50–160 chars | Present but outside range | Missing |
| H1 | Exactly one | Multiple H1 tags | No H1 |
| Alt text | No images or all images have alt | Some images missing alt | All images missing alt |
| Content length | >= 300 words | 100–299 words | < 100 words |

## 7. PageSpeed Integration

- Endpoint: `https://www.googleapis.com/pagespeedonline/v5/runPagespeed`
- Strategies: `mobile`, `desktop`
- Dedicated timeout via `PAGESPEED_TIMEOUT_SECONDS` (default 120s)
- Both strategies fetched concurrently
- Lighthouse performance score and audit display values mapped into `PerformanceMetrics`
- Uses INP when available, otherwise TBT

## 8. OpenAI Integration

- Direct OpenAI SDK usage (no LangChain)
- Temperature: `0.2`
- Model configured via `OPENAI_MODEL`
- Structured output validated with `AiAnalysis` Pydantic model
- Prompt includes only:
  - page metadata
  - SEO check results
  - Core Web Vitals metrics

## 9. Logging

Structured JSON logs include:

- `audit_start`
- `audit_complete`
- `audit_duration_ms`
- `pagespeed_latency_ms`
- `openai_latency_ms`
- `prompt_tokens`, `completion_tokens`, `total_tokens`
- `error`

## 10. Error Handling

| Failure | HTTP Status |
|---------|-------------|
| Invalid URL | 400 |
| Scrape timeout | 504 |
| Scrape / PageSpeed / OpenAI failure | 502 |
| Missing report | 404 |
| Unexpected server error | 500 |

## 11. Security Controls

- URL scheme restricted to `http` and `https`
- Hostname/IP SSRF checks
- Embedded credentials rejected
- Redirect and response size limits on HTTP fetches
- UUID validation before report download

## 12. Persistence

- Reports stored at `reports/{audit_id}.json`
- Optional Redis cache keyed by normalized audit URL

## 13. Testing Strategy

Unit tests cover:

- Pydantic model validation
- URL validation and SSRF checks
- HTML parsing
- SEO rule evaluation
- PageSpeed response parsing
- Audit orchestration and API endpoints (mocked external calls)
