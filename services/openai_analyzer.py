import time

from openai import AsyncOpenAI

from core.config import settings
from core.exceptions import OpenAIAnalysisError
from core.logging import get_logger, log_openai_latency
from models.report import AiAnalysis, CoreWebVitals, PageDetails, SeoChecks
from prompts.seo_analysis import SYSTEM_PROMPT, build_user_prompt
from util.langfuse_tracing import langfuse_enabled, traced, update_current_generation

logger = get_logger(__name__)


@traced("openai-seo-analysis", as_type="generation")
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

    if langfuse_enabled():
        update_current_generation(
            model=settings.OPENAI_MODEL,
            metadata={"temperature": settings.OPENAI_TEMPERATURE, "url": url, "audit_id": audit_id},
        )

    client = AsyncOpenAI(
        api_key=settings.OPENAI_API_KEY,
        timeout=settings.OPENAI_TIMEOUT_SECONDS,
        max_retries=settings.OPENAI_MAX_RETRIES,
    )
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": build_user_prompt(
                url=url,
                page_details=page_details.model_dump(),
                seo_checks=seo_checks.model_dump(),
                core_web_vitals=core_web_vitals.model_dump(),
            ),
        },
    ]

    started_at = time.perf_counter()
    response = None
    try:
        response = await client.beta.chat.completions.parse(
            model=settings.OPENAI_MODEL,
            temperature=settings.OPENAI_TEMPERATURE,
            messages=messages,
            response_format=AiAnalysis,
        )
    except Exception as exc:
        if langfuse_enabled():
            update_current_generation(
                level="ERROR",
                status_message=str(exc),
            )
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

    if langfuse_enabled():
        update_current_generation(
            input=messages,
            output=message.parsed.model_dump(),
            usage={
                "input": usage.prompt_tokens,
                "output": usage.completion_tokens,
                "total": usage.total_tokens,
            }
            if usage
            else None,
            metadata={"openai_latency_ms": round(latency_ms, 2)},
        )

    return message.parsed
