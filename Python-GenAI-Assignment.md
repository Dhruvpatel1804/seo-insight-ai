**Assignment: AI-Powered SEO Page Auditor**

**Objective**

Build a Python application that analyzes a webpage and generates an SEO
audit report using Generative AI and Core Web Vitals (CWV) data.

**Input**

**The application should accept a webpage URL as input from the user.**

**Example:**

**https://www.milestoneinternet.com/**

**Candidates may use any publicly accessible webpage URL for testing and
demonstration. Only homepage need to used for testing not all pages.**

**Requirements**

**1. Webpage Scraping**

Extract the following information:

-   Page Title

-   Meta Description

-   H1 Tags

-   H2 Tags

-   Canonical URL

-   Number of Images

-   Number of Images Missing ALT Text

-   Total Word Count

**2. SEO Validation**

Perform SEO checks and capture findings for:

-   Title availability

-   Meta Description availability

-   H1 tag presence

-   Missing ALT attributes

-   Content word count

Store all findings in a structured format.

**3. Core Web Vitals & Page Performance**

Retrieve and report page performance metrics using PageSpeed Insights
API or an equivalent approach.

Capture:

-   Performance Score

-   Largest Contentful Paint (LCP)

-   Interaction to Next Paint (INP) / Total Blocking Time (TBT)

-   Cumulative Layout Shift (CLS)

-   First Contentful Paint (FCP)

-   Speed Index

Include both:

-   Mobile Results

-   Desktop Results

**4. GenAI Analysis**

Using the scraped content, SEO findings, and PageSpeed metrics,
generate:

-   Technical SEO Findings

-   Content SEO Findings

-   Core Web Vitals Findings

-   Recommended Improvements

-   Suggested Meta Description

-   Suggested Page Title

The AI response must be returned in structured JSON format.

**5. Output**

Generate a JSON report in the following structure:

{

\"url\": \"\",

\"page_details\": {},

\"seo_checks\": {},

\"pagespeed\": {

\"mobile\": {},

\"desktop\": {}

},

\"ai_analysis\": {}

}

Save the file as:

seo_audit_report.json

**Deliverables**

-   Python Source Code

-   README with setup instructions

-   Generated seo_audit_report.json
