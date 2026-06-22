# SEO Insight AI

AI-powered SEO page auditor built with FastAPI. The application scrapes a webpage, validates on-page SEO signals, retrieves Core Web Vitals from Google PageSpeed Insights, generates AI recommendations with OpenAI, and returns a downloadable JSON audit report with an inline summary.

## Features

- Webpage scraping (title, meta description, headings, images, word count, canonical URL)
- SEO validation checks (`PASS`, `FAIL`, `WARNING`)
- Core Web Vitals via Google PageSpeed Insights (mobile and desktop)
- AI-powered SEO analysis with structured JSON output
- Inline audit summary in API responses (scores, checks, recommendations)
- Downloadable full report as `seo_audit_report.json`
- Web UI with audit summary dashboard at `/`
- Optional Redis caching for repeated audits of the same URL
- Optional Langfuse Cloud integration for LLM tracing and token usage (free plan)

## Tech Stack

- Python 3.10+
- FastAPI
- Pydantic v2
- httpx (async)
- BeautifulSoup4
- OpenAI SDK
- Redis (optional cache)
- Langfuse Cloud (optional, free plan)
- Pipenv
- Docker

## Prerequisites

- Python 3.10+
- [Pipenv](https://pipenv.pypa.io/)
- OpenAI API key
- Google PageSpeed Insights API key
- Redis (optional, for audit caching)

## Setup

1. Clone the repository and enter the project directory.

2. Install dependencies:

```bash
pipenv install
```

3. Create environment file:

```bash
cp example.env .env
```

4. Configure `.env` using `example.env` as the reference template:

| Section | Key variables |
|---------|----------------|
| Application | `PROJECT_NAME`, `PROJECT_VERSION`, `DEBUG` |
| API server | `API_HOST`, `API_PORT`, `API_RELOAD`, `API_DOCS_ENABLED` |
| CORS | `API_CORS_ORIGINS`, `CORS_ALLOW_CREDENTIALS` |
| Logging | `LOG_LEVEL`, `LOG_DIR`, `LOG_MAX_BYTES`, `LOG_BACKUP_COUNT` |
| OpenAI | `OPENAI_API_KEY`, `OPENAI_MODEL`, `OPENAI_TEMPERATURE` |
| Redis cache | `REDIS_URL`, `AUDIT_CACHE_TTL_SECONDS` |
| Langfuse | `LANGFUSE_ENABLED`, `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`, `LANGFUSE_HOST` |
| PageSpeed | `PAGESPEED_API_KEY`, `PAGESPEED_API_URL`, `PAGESPEED_TIMEOUT_SECONDS` |
| HTTP / security | `HTTP_TIMEOUT_SECONDS`, `HTTP_USER_AGENT`, `MAX_RESPONSE_BYTES`, `MAX_REDIRECTS` |
| Storage | `REPORTS_DIR` |

Redis is optional. Leave `REDIS_URL` empty or unset to disable caching. When enabled, repeated audits of the same normalized URL return instantly from cache.

Langfuse is optional. Sign up at [Langfuse Cloud](https://cloud.langfuse.com), create a project, and add the keys to the **same `.env` file** as all other variables (see below).

> **Important:** API keys alone are not enough — you must set `LANGFUSE_ENABLED=true` or tracing is silently disabled.

## Langfuse Cloud (LLM Observability)

Uses the [Langfuse free plan](https://langfuse.com/pricing). No self-hosted Postgres, ClickHouse, or extra Docker services — traces are sent to Langfuse Cloud over HTTPS.

### Setup

1. Sign up at [https://cloud.langfuse.com](https://cloud.langfuse.com) and create a project.
2. Copy the project **Public Key** and **Secret Key** from project settings.
3. Add to your `.env`:

```env
LANGFUSE_ENABLED=true
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_HOST=https://cloud.langfuse.com
```

4. Restart the app. On startup you should see `Langfuse tracing enabled` in the logs.
5. Run a **new** audit (not a Redis cache hit) and view traces at [https://cloud.langfuse.com](https://cloud.langfuse.com) → **Tracing**.

**US region:** use `LANGFUSE_HOST=https://us.cloud.langfuse.com` if your project is on the US cloud.

### What is traced

| Trace | Type | Captures |
|-------|------|----------|
| `seo-audit` | Span | Full audit run, URL, audit ID, session, cache hits |
| `openai-seo-analysis` | Generation | Model, messages, response, token usage, latency |

Structured JSON logs (`openai_latency` events) are still written to `logs/app.log`.

### Troubleshooting

| Symptom | Fix |
|---------|-----|
| No traces in dashboard | Set `LANGFUSE_ENABLED=true` and restart the server |
| Keys set but no traces | Check logs for `Langfuse API keys are set but LANGFUSE_ENABLED=false` |
| Only cache hits, no generations | Cached audits skip OpenAI; run a new URL or clear Redis cache |
| Wrong project / region | Match `LANGFUSE_HOST` to EU vs US cloud and verify keys belong to that project |

Leave `LANGFUSE_ENABLED=false` to disable tracing entirely.

## Run Locally

```bash
pipenv run python main.py
```

Or explicitly:

```bash
pipenv run uvicorn main:app --host 0.0.0.0 --port 8000
```

Server host, port, and reload behavior can also be controlled via `API_HOST`, `API_PORT`, and `API_RELOAD` in `.env`.

- Web UI: [http://localhost:8000/](http://localhost:8000/)
- Swagger UI: [http://localhost:8000/swagger-docs/](http://localhost:8000/swagger-docs/)
- ReDoc: [http://localhost:8000/custom-docs/](http://localhost:8000/custom-docs/)

## API Usage

### Health Check

```bash
curl http://localhost:8000/api/v1/health/
```

### Run SEO Audit

```bash
curl -X POST http://localhost:8000/api/v1/audit \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.milestoneinternet.com/"}'
```

Example response:

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

### Download Report

```bash
curl -OJ http://localhost:8000/api/v1/reports/{audit_id}
```

The downloaded file is named `seo_audit_report.json`.

## Docker

Build and run with Docker Compose:

```bash
docker compose up --build
```

The API and Web UI will be available at [http://localhost:8000](http://localhost:8000).

Reports and logs are persisted via volume mounts (`./reports`, `./logs`). Use host Redis for audit caching (`REDIS_URL`) if needed. Langfuse uses the hosted cloud — no extra Docker services required.

## Project Structure

```
api/            # FastAPI routes (REST + UI)
core/           # Config, logging, exceptions
models/         # Pydantic request/response/report schemas
services/       # Scraper, SEO validator, PageSpeed, OpenAI, audit orchestration
prompts/        # OpenAI prompt templates
util/           # URL validation, HTTP client, Redis cache, Langfuse tracing
static/         # Web UI
reports/        # Persisted audit JSON files (runtime)
logs/           # Application logs (runtime)
docs/           # HLD, LLD, architecture diagram
tests/          # Unit tests
```

## Response Schemas

### Audit API response (`AuditResponse`)

| Field | Description |
|-------|-------------|
| `audit_id` | UUID for this audit |
| `status` | Always `"completed"` |
| `download_url` | Path to download the full report |
| `summary` | Inline `AuditSummary` (see below) |

### Audit summary (`AuditSummary`)

Key fields: `page_title`, `meta_description`, `word_count`, `seo_checks`, `seo_pass_count`, `mobile_performance_score`, `desktop_performance_score`, `key_findings`, `recommended_improvements`, `suggested_title`, `suggested_meta_description`.

### Full report (`SeoAuditReport`)

```json
{
  "url": "",
  "generated_at": "",
  "page_details": {},
  "seo_checks": {},
  "core_web_vitals": {
    "mobile": {},
    "desktop": {}
  },
  "ai_analysis": {}
}
```

## Tests

```bash
pipenv run python -m unittest discover -s tests -v
```

## Production Enhancements (Future)

- Celery/RQ for background audit processing
- OpenTelemetry distributed tracing (beyond Langfuse)
- Prometheus metrics and Grafana dashboards
- Azure deployment with managed scaling
- Multi-page auditing
- Batch processing for large site audits

## Documentation

- [High-Level Design](docs/HLD.md)
- [Low-Level Design](docs/LLD.md)
- [Architecture Diagram](docs/architecture.md)

## License

Internal assignment project.
