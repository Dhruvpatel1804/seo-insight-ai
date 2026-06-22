# High-Level Design (HLD) — SEO Insight AI

## 1. Overview

SEO Insight AI is a FastAPI-based service that performs automated SEO audits for a single webpage URL. It combines deterministic scraping and validation with external performance data (Google PageSpeed Insights) and generative AI analysis (OpenAI) to produce a structured JSON audit report.

## 2. Goals

- Accept a public webpage URL and return a downloadable SEO audit report
- Provide reliable Core Web Vitals using Google PageSpeed Insights
- Generate actionable SEO recommendations using structured AI output
- Follow async, service-oriented, production-oriented design principles

## 3. System Context

```text
User / API Client
      |
      v
SEO Insight AI (FastAPI)
      |------> Target Website (HTML scraping)
      |------> Google PageSpeed Insights API
      |------> OpenAI API
      v
Persisted JSON Report
```

## 4. Major Components

| Component | Responsibility |
|-----------|----------------|
| API Layer | Exposes audit and report download endpoints |
| Audit Service | Orchestrates the end-to-end audit workflow |
| Scraper Service | Fetches and parses webpage SEO metadata |
| SEO Validator | Applies rule-based SEO checks |
| PageSpeed Service | Retrieves Lighthouse performance metrics |
| OpenAI Analyzer | Generates structured AI recommendations |
| Report Store | Saves audit output as JSON files |

## 5. High-Level Workflow

1. Client submits a URL to `POST /api/v1/audit`
2. URL is validated for format and SSRF safety
3. Scraping and PageSpeed collection run concurrently
4. SEO validation rules are applied to scraped data
5. OpenAI analyzes the structured audit inputs
6. A canonical JSON report is generated and saved
7. Client receives an `audit_id` and download URL
8. Client downloads the report via `GET /api/v1/reports/{audit_id}`

## 6. External Dependencies

- **Target Website**: Source HTML content for SEO metadata
- **Google PageSpeed Insights API**: Standardized Lighthouse metrics for mobile and desktop
- **OpenAI API**: Structured SEO analysis and recommendations

## 7. Non-Functional Requirements

- Fully async service execution
- Strong typing with Pydantic models
- Structured JSON logging
- Meaningful API error responses
- URL validation and request limits to reduce SSRF risk
- Token-efficient OpenAI prompts (metadata only, no raw HTML)

## 8. Deployment View

- Containerized FastAPI app using Docker
- Environment-based configuration for API keys and limits
- Local filesystem storage for generated reports
- Optional Docker Compose deployment for local/demo use

## 9. Out of Scope

- User authentication
- Database persistence
- Multi-page crawling
- Background job queues
- Caching layers
- Observability stack integration

These are documented as future production enhancements in the README.
