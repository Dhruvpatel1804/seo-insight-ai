# High-Level Design (HLD) — SEO Insight AI

## 1. Overview

SEO Insight AI is a FastAPI-based service that performs automated SEO audits for a single webpage URL. It combines deterministic scraping and validation with external performance data (Google PageSpeed Insights) and generative AI analysis (OpenAI) to produce a structured JSON audit report.

The application exposes both a REST API and a browser UI. API responses include an inline audit summary so clients can display key results without downloading the full report. Optional Redis caching avoids re-running expensive audits for the same normalized URL within a configurable TTL.

## 2. Goals

- Accept a public webpage URL and return a downloadable SEO audit report
- Provide reliable Core Web Vitals using Google PageSpeed Insights
- Generate actionable SEO recommendations using structured AI output
- Return a concise audit summary in the API response for immediate review
- Cache completed audits in Redis when configured
- Trace LLM usage and audit runs via Langfuse Cloud when enabled
- Follow async, service-oriented, production-oriented design principles

## 3. System Context

```text
User / API Client / Web UI
            |
            v
   SEO Insight AI (FastAPI)
      |------> Target Website (HTML scraping)
      |------> Google PageSpeed Insights API
      |------> OpenAI API
      |------> Redis (optional audit cache)
      |------> Langfuse Cloud (optional LLM tracing)
      v
Persisted JSON Report (local filesystem)
```

## 4. Major Components

| Component | Responsibility |
|-----------|----------------|
| API Layer | Exposes audit, report download, and health endpoints |
| Web UI | Serves `static/index.html` at `/` with summary dashboard |
| Audit Service | Orchestrates cache lookup, validation, scraping, analysis, and persistence |
| Scraper Service | Fetches and parses webpage SEO metadata |
| SEO Validator | Applies rule-based SEO checks |
| PageSpeed Service | Retrieves Lighthouse performance metrics (mobile + desktop) |
| OpenAI Analyzer | Generates structured AI recommendations |
| Cache Layer | Optional Redis cache keyed by normalized audit URL |
| Observability | Optional Langfuse Cloud tracing for audit spans and LLM generations |
| Report Store | Saves full audit output as JSON files under `reports/` |

## 5. High-Level Workflow

1. Client submits a URL to `POST /api/v1/audit` (or via the Web UI at `/`)
2. Audit service checks Redis for a cached result using a normalized URL key
3. On cache hit, returns the cached `AuditResponse` (summary enriched from disk if needed)
4. On cache miss, URL is validated for format and SSRF safety
5. Scraping and PageSpeed collection run concurrently (separate HTTP clients with appropriate timeouts)
6. SEO validation rules are applied to scraped data
7. OpenAI analyzes the structured audit inputs
8. A canonical JSON report is generated and saved to `reports/{audit_id}.json`
9. Client receives `audit_id`, `download_url`, and an inline `summary`
10. Response is written to Redis when `REDIS_URL` is configured
11. Traces are sent to Langfuse Cloud when `LANGFUSE_ENABLED=true` and API keys are set
12. Client downloads the full report via `GET /api/v1/reports/{audit_id}`

## 6. External Dependencies

| Dependency | Purpose |
|------------|---------|
| Target Website | Source HTML content for SEO metadata |
| Google PageSpeed Insights API | Lighthouse metrics for mobile and desktop |
| OpenAI API | Structured SEO analysis and recommendations |
| Redis (optional) | Audit response caching by normalized URL |
| Langfuse Cloud (optional) | LLM tracing and token usage (free plan, no local DB) |

## 7. Non-Functional Requirements

- Fully async service execution
- Strong typing with Pydantic v2 models
- Structured JSON logging (audit, cache, PageSpeed, OpenAI events)
- Optional Langfuse Cloud tracing (SDK sends traces to hosted Langfuse; no local database)
- Meaningful API error responses with consistent JSON shape
- URL validation and request limits to reduce SSRF risk
- Token-efficient OpenAI prompts (metadata only, no raw HTML)
- Graceful degradation when Redis is unavailable (audit still runs, cache is skipped)
- Graceful degradation when Langfuse is unavailable (audit still runs, tracing is skipped)

## 8. Deployment View

- Containerized FastAPI app using Docker
- Single `.env` file for all configuration (`example.env` as template)
- Local filesystem storage for generated reports (`reports/`)
- Optional Docker Compose deployment for local/demo use
- Redis optional for audit caching only (`REDIS_URL`)
- Langfuse Cloud optional for observability (no self-hosted Langfuse stack)

## 9. Out of Scope

- User authentication in the SEO Insight AI app
- Database persistence for reports (filesystem + optional Redis cache only)
- Self-hosted Langfuse infrastructure (Postgres, ClickHouse, MinIO)
- Multi-page crawling
- Background job queues
- Full observability stack (OpenTelemetry, Prometheus) beyond Langfuse Cloud

These are documented as future production enhancements in the README.
