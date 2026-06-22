# SEO Insight AI

AI-powered SEO page auditor built with FastAPI. The application scrapes a webpage, validates on-page SEO signals, retrieves Core Web Vitals from Google PageSpeed Insights, generates AI recommendations with OpenAI, and returns a downloadable JSON audit report.

## Features

- Webpage scraping (title, meta description, headings, images, word count, canonical URL)
- SEO validation checks (`PASS`, `FAIL`, `WARNING`)
- Core Web Vitals via Google PageSpeed Insights (mobile and desktop)
- AI-powered SEO analysis with structured JSON output
- Downloadable `seo_audit_report.json`

## Tech Stack

- Python 3.10+
- FastAPI
- Pydantic v2
- httpx (async)
- BeautifulSoup4
- OpenAI SDK
- Pipenv
- Docker

## Prerequisites

- Python 3.10+
- [Pipenv](https://pipenv.pypa.io/)
- OpenAI API key
- Google PageSpeed Insights API key

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

4. Configure `.env` using `example.env` as the reference template. All supported variables are documented there, grouped by concern:

| Section | Key variables |
|---------|----------------|
| Application | `PROJECT_NAME`, `PROJECT_VERSION`, `DEBUG` |
| API server | `API_HOST`, `API_PORT`, `API_RELOAD`, `API_DOCS_ENABLED` |
| CORS | `API_CORS_ORIGINS`, `CORS_ALLOW_CREDENTIALS` |
| Logging | `LOG_LEVEL`, `LOG_DIR`, `LOG_MAX_BYTES`, `LOG_BACKUP_COUNT` |
| OpenAI | `OPENAI_API_KEY`, `OPENAI_MODEL`, `OPENAI_TEMPERATURE` |
| PageSpeed | `PAGESPEED_API_KEY`, `PAGESPEED_API_URL`, `PAGESPEED_TIMEOUT_SECONDS` |
| HTTP / security | `HTTP_TIMEOUT_SECONDS`, `HTTP_USER_AGENT`, `MAX_RESPONSE_BYTES`, `MAX_REDIRECTS` |
| Storage | `REPORTS_DIR` |


## Run Locally

```bash
pipenv run python main.py
```

Or explicitly:

```bash
pipenv run uvicorn main:app --host 0.0.0.0 --port 8000
```

Server host, port, and reload behavior can also be controlled via `API_HOST`, `API_PORT`, and `API_RELOAD` in `.env`.

API documentation:

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
  "download_url": "/api/v1/reports/550e8400-e29b-41d4-a716-446655440000"
}
```

### Download Report

```bash
curl -OJ http://localhost:8000/api/v1/reports/{audit_id}
```

The downloaded file is named `seo_audit_report.json`.

## Generate Sample Report

Generate the assignment sample report for `https://www.milestoneinternet.com/`:

```bash
pipenv run python scripts/generate_sample_report.py
```

If `OPENAI_API_KEY` is configured, the script runs the full AI-powered audit. Otherwise, it generates a sample report using real scraped and PageSpeed data with a deterministic analysis fallback.

Output files:

- `output/seo_audit_report.json`
- `seo_audit_report.json` (project root copy)

## Docker

Build and run with Docker Compose:

```bash
docker compose up --build
```

The API will be available at [http://localhost:8000](http://localhost:8000).

## Project Structure

```
api/            # FastAPI routes
core/           # Config, logging, exceptions
models/         # Pydantic request/response/report schemas
services/       # Scraper, SEO validator, PageSpeed, OpenAI, audit orchestration
prompts/        # OpenAI prompt templates
util/           # URL validation, HTTP client helpers
reports/        # Persisted audit JSON files
output/         # Sample report output
docs/           # HLD, LLD, architecture diagram
tests/          # Unit tests
```

## Report Schema

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

The following are documented for future production hardening but are not implemented in this version:

- Redis caching for PageSpeed and audit results
- Celery/RQ for background audit processing
- OpenTelemetry distributed tracing
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
