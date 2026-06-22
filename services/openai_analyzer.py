import time

from openai import AsyncOpenAI

from core.config import settings
from core.exceptions import OpenAIAnalysisError
from core.logging import get_logger, log_openai_latency
from models.report import AiAnalysis, CoreWebVitals, PageDetails, SeoChecks
from prompts.seo_analysis import SYSTEM_PROMPT, build_user_prompt

logger = get_logger(__name__)


async def analyze_seo(
    *,
    audit_id: str,
    url: str,
    page_details: PageDetails,
    seo_checks: SeoChecks,
    core_web_vitals: CoreWebVitals,
) -> AiAnalysis:
    if not settings.OPENAI_API_KEY:
        raise OpenAIAnalysisError("OpenAI API key is not configured")

    client = AsyncOpenAI(
        api_key=settings.OPENAI_API_KEY,
        timeout=settings.OPENAI_TIMEOUT_SECONDS,
        max_retries=settings.OPENAI_MAX_RETRIES,
    )
    user_prompt = build_user_prompt(
        url=url,
        page_details=page_details.model_dump(),
        seo_checks=seo_checks.model_dump(),
        core_web_vitals=core_web_vitals.model_dump(),
    )

    started_at = time.perf_counter()
    response = None
    try:
        response = await client.beta.chat.completions.parse(
            model=settings.OPENAI_MODEL,
            temperature=settings.OPENAI_TEMPERATURE,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            response_format=AiAnalysis,
        )
    except Exception as exc:
        raise OpenAIAnalysisError(f"OpenAI analysis request failed: {exc}") from exc
    finally:
        latency_ms = (time.perf_counter() - started_at) * 1000
        usage = response.usage if response else None
        log_openai_latency(
            logger,
            audit_id=audit_id,
            openai_latency_ms=latency_ms,
            prompt_tokens=usage.prompt_tokens if usage else 0,
            completion_tokens=usage.completion_tokens if usage else 0,
            total_tokens=usage.total_tokens if usage else 0,
        )

    message = response.choices[0].message
    if message.parsed is None:
        raise OpenAIAnalysisError("OpenAI returned an invalid analysis response")

    return message.parsed
