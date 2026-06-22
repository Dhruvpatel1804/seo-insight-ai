# Architecture Diagram — SEO Insight AI

## Component Diagram

```mermaid
flowchart TB
    Client[API Client]
    API[FastAPI API Layer]
    Audit[Audit Service]
    Scraper[Scraper Service]
    SEO[SEO Validator]
    PSI[PageSpeed Service]
    AI[OpenAI Analyzer]
  Reports[(Report Store)]
    Site[Target Website]
    Google[Google PageSpeed Insights API]
    OpenAI[OpenAI API]

    Client -->|POST /api/v1/audit| API
    Client -->|GET /api/v1/reports/{audit_id}| API
    API --> Audit
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
    participant C as Client
    participant A as API
    participant S as Audit Service
    participant W as Website
    participant P as PageSpeed API
    participant O as OpenAI API
    participant R as Report Store

    C->>A: POST /api/v1/audit {url}
    A->>S: run_audit(url)
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
    S->>R: save_report(audit_id)
    S-->>A: AuditResponse
    A-->>C: audit_id + download_url

    C->>A: GET /api/v1/reports/{audit_id}
    A->>R: load report
    R-->>A: seo_audit_report.json
    A-->>C: downloadable file
```

## Deployment Diagram

```mermaid
flowchart LR
    User[User / Client]
    Docker[Docker Container]
    App[FastAPI App]
    FS[(Local Filesystem)]
    Ext[External APIs]

    User --> Docker
    Docker --> App
    App --> FS
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
```
