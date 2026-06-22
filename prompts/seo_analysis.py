SYSTEM_PROMPT = """You are an expert SEO auditor.
Analyze only the supplied audit data.
Do not invent metrics, page content, or issues that are not supported by the input.
Return findings grounded strictly in the provided SEO checks, page details, and Core Web Vitals.
"""


def build_user_prompt(
    url: str,
    page_details: dict,
    seo_checks: dict,
    core_web_vitals: dict,
) -> str:
    return f"""Analyze the following SEO audit data for {url}.

Page details:
- title: {page_details.get("title", "")}
- meta_description: {page_details.get("meta_description", "")}
- canonical_url: {page_details.get("canonical_url", "")}
- h1_tags: {page_details.get("h1_tags", [])}
- h2_tags: {page_details.get("h2_tags", [])}
- image_count: {page_details.get("image_count", 0)}
- missing_alt_count: {page_details.get("missing_alt_count", 0)}
- word_count: {page_details.get("word_count", 0)}

SEO checks:
- title_check: {seo_checks.get("title_check")}
- meta_description_check: {seo_checks.get("meta_description_check")}
- h1_check: {seo_checks.get("h1_check")}
- alt_text_check: {seo_checks.get("alt_text_check")}
- content_length_check: {seo_checks.get("content_length_check")}

Core Web Vitals:
- mobile: {core_web_vitals.get("mobile", {})}
- desktop: {core_web_vitals.get("desktop", {})}

Provide:
1. technical_seo_findings
2. content_findings
3. core_web_vitals_findings
4. recommended_improvements
5. suggested_title
6. suggested_meta_description
"""
