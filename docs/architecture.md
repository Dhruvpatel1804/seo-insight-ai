# Architecture Diagram — SEO Insight AI

## Component Diagram

```mermaid
flowchart TB
    Browser[Web UI Browser]
    Client[API Client]
    API[FastAPI API Layer]
    UI[UI Router]
    Audit[Audit Service]
    Cache[Redis Cache]
    Scraper[Scraper Service]
    SEO[SEO Validator]
    PSI[PageSpeed Service]
    AI[OpenAI Analyzer]
    Reports[(Report Store)]
    Site[Target Website]
    Google[Google PageSpeed Insights API]
    OpenAI[OpenAI API]

    Browser -->|GET /| UI
    Browser -->|POST /api/v1/audit| API
    Client -->|POST /api/v1/audit| API
    Client -->|GET /api/v1/reports/{audit_id}| API
    UI --> Browser
    API --> Audit
    Audit --> Cache
    Audit --> Scraper
    Audit --> PSI
    Audit --> SEO
    Audit --> AI
    Scraper --> Site
    PSI --> Google
    AI --> OpenAI
    Audit --> Reports
    API --> Reports
```

## Audit Sequence

```mermaid
sequenceDiagram
    participant C as Client / Web UI
    participant A as API
    participant S as Audit Service
    participant R as Redis Cache
    participant W as Website
    participant P as PageSpeed API
    participant O as OpenAI API
    participant FS as Report Store

    C->>A: POST /api/v1/audit {url}
    A->>S: run_audit(url)
    S->>R: get_cached_audit(normalized_url)

    alt Cache hit
        R-->>S: cached AuditResponse
        S->>FS: load_report (if summary missing)
        S-->>A: AuditResponse + summary
        A-->>C: audit_id + download_url + summary
    else Cache miss
        R-->>S: null
        S->>S: validate_url(url)

        par Concurrent collection
            S->>W: scrape_page(url)
            W-->>S: HTML
            S->>S: parse_html()
        and
            S->>P: fetch mobile/desktop metrics
            P-->>S: Lighthouse results
        end

        S->>S: validate_seo(page_details)
        S->>O: analyze_seo(structured data)
        O-->>S: AiAnalysis JSON
        S->>FS: save_report(audit_id)
        S->>R: set_cached_audit(normalized_url, response)
        S-->>A: AuditResponse + summary
        A-->>C: audit_id + download_url + summary
    end

    C->>A: GET /api/v1/reports/{audit_id}
    A->>FS: load report file
    FS-->>A: seo_audit_report.json
    A-->>C: downloadable file
```

## Deployment Diagram

```mermaid
flowchart LR
    User[User / Client]
    Docker[Docker Container]
    App[FastAPI App]
    FS[(Local Filesystem)]
    Redis[(Redis - optional)]
    Ext[External APIs]

    User --> Docker
    Docker --> App
    App --> FS
    App --> Redis
    App --> Ext
```

## Data Flow

```mermaid
flowchart LR
    URL[Input URL]
    PD[PageDetails]
    SC[SeoChecks]
    CWV[CoreWebVitals]
    AI[AiAnalysis]
    REP[SeoAuditReport]
    SUM[AuditSummary]
    RES[AuditResponse]

    URL --> PD
    URL --> CWV
    PD --> SC
    PD --> AI
    SC --> AI
    CWV --> AI
    PD --> REP
    SC --> REP
    CWV --> REP
    AI --> REP
    REP --> SUM
    SUM --> RES
    REP --> FS[(reports/{audit_id}.json)]
    RES --> Redis[(Redis cache)]
```

## API Surface

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/` | Web UI (audit form + summary dashboard) |
| `GET` | `/api/v1/health/` | Health check |
| `POST` | `/api/v1/audit` | Run SEO audit |
| `GET` | `/api/v1/reports/{audit_id}` | Download full JSON report |
