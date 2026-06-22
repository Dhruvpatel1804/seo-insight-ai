# SEO Insight AI - Development Instructions

## Objective

Build a production-oriented FastAPI application named "SEO Insight AI" that performs AI-powered SEO auditing for a given webpage URL.

The application should:

1. Accept a webpage URL.
2. Scrape SEO metadata.
3. Perform SEO validation checks.
4. Retrieve Core Web Vitals using Google PageSpeed Insights API.
5. Generate AI-powered SEO recommendations using OpenAI.
6. Generate and persist a downloadable `seo_audit_report.json`.
7. Follow clean architecture and production-grade engineering practices.

---

# Technical Stack

* Python 3.12+
* FastAPI
* Pydantic v2
* httpx (async)
* BeautifulSoup4
* OpenAI SDK
* uv
* Docker

Avoid LangChain.

Reason:
Single LLM call, no agents, no memory, no RAG, no tool calling.

---

# Architecture Principles

* Fully async implementation
* Service-oriented structure
* Strong typing using Pydantic
* Dependency injection where applicable
* Separation of concerns
* Structured logging
* Production-ready error handling

---

# Repository Structure

app/
├── api/
├── services/
├── models/
├── core/
├── utils/
├── prompts/
├── reports/
└── main.py

docs/
tests/
output/

README.md
Dockerfile
.env.example

---

# API Requirements

POST /api/v1/audit

Request:

{
"url": "https://example.com"
}

Response:

{
"audit_id": "...",
"status": "completed",
"download_url": "/api/v1/reports/{audit_id}"
}

---

GET /api/v1/reports/{audit_id}

Returns:

seo_audit_report.json

as downloadable file.

---

# Async Workflow

1. Validate URL.
2. Scrape page metadata.
3. Execute SEO checks.
4. Execute PageSpeed API calls.
5. Run SEO checks and PageSpeed collection concurrently where possible.
6. Invoke OpenAI analysis.
7. Build report.
8. Save report to disk.
9. Return download URL.

Use:

asyncio.gather()

for concurrent operations.

---

# Scraper Requirements

Extract:

* title
* meta_description
* canonical_url
* h1_tags
* h2_tags
* image_count
* missing_alt_count
* word_count

Use BeautifulSoup.

---

# SEO Validation Rules

Validate:

* title_check
* meta_description_check
* h1_check
* alt_text_check
* content_length_check

Possible values:

PASS
FAIL
WARNING

---

# Core Web Vitals

Collect:

Desktop:

* performance_score
* lcp
* cls
* fcp
* speed_index
* inp_or_tbt

Mobile:

* performance_score
* lcp
* cls
* fcp
* speed_index
* inp_or_tbt

Use Google PageSpeed Insights API.

---

# Canonical Report Schema

{
"url": "",
"generated_at": "",

"page_details": {
"title": "",
"meta_description": "",
"canonical_url": "",
"h1_tags": [],
"h2_tags": [],
"image_count": 0,
"missing_alt_count": 0,
"word_count": 0
},

"seo_checks": {
"title_check": "",
"meta_description_check": "",
"h1_check": "",
"alt_text_check": "",
"content_length_check": ""
},

"core_web_vitals": {
"mobile": {},
"desktop": {}
},

"ai_analysis": {
"technical_seo_findings": [],
"content_findings": [],
"core_web_vitals_findings": [],
"recommended_improvements": [],
"suggested_title": "",
"suggested_meta_description": ""
}
}

Use this schema consistently across:

* Pydantic models
* API responses
* JSON file generation
* AI output validation
* Documentation

---

# OpenAI Requirements

Use direct OpenAI SDK.

Temperature:

0.2

Model:

Configurable via environment variable.

Use structured JSON output.

Validate AI response using Pydantic.

No free-form text parsing.

---

# Prompt Requirements

The AI must:

* Analyze SEO findings
* Analyze Core Web Vitals
* Identify technical SEO issues
* Identify content SEO issues
* Recommend improvements
* Suggest optimized title
* Suggest optimized meta description

Rules:

* Only use supplied data
* Do not invent information
* Do not hallucinate
* Return JSON only

---

# Token Optimization

Do NOT send:

* Raw HTML
* Full webpage DOM
* Large content blocks

Only send:

* SEO metadata
* SEO validation results
* Core Web Vital metrics
* Content statistics

Goal:

Minimize token usage and API cost.

---

# Logging Requirements

Log:

* audit_start
* audit_complete
* audit_duration
* pagespeed_latency
* openai_latency
* prompt_tokens
* completion_tokens
* total_tokens
* errors

Structured JSON logging preferred.

---

# Error Handling

Handle:

* Invalid URL
* Network timeout
* Website unavailable
* PageSpeed API failure
* OpenAI API failure
* Invalid AI response

Return meaningful API errors.

---

# Security

Implement:

* URL validation
* Request timeout
* Response size limits
* Redirect limits

Prevent SSRF-style misuse.

---

# Production Enhancements (Document Only)

Mention in README:

* Redis caching
* Celery/RQ
* OpenTelemetry
* Prometheus
* Grafana
* Azure deployment
* Multi-page auditing
* Batch processing

Do not implement unless trivial.

---

# Deliverables

1. Source code
2. Dockerfile
3. README
4. HLD
5. LLD
6. Architecture diagram
7. Sample report
8. API documentation
9. Downloadable seo_audit_report.json
