from fastapi import APIRouter, HTTPException, status

from core.exceptions import (
    InvalidURLError,
    OpenAIAnalysisError,
    PageSpeedError,
    ScrapingError,
)
from core.logging import get_logger, log_error
from models.requests import AuditRequest
from models.responses import AuditResponse
from services.audit_service import run_audit

logger = get_logger(__name__)

router = APIRouter()


@router.get("/health/")
async def health():
    return {"status": "healthy", "service": "SEO Insight AI"}


@router.post("/audit", response_model=AuditResponse, status_code=status.HTTP_200_OK)
async def create_audit(request: AuditRequest) -> AuditResponse:
    url = str(request.url)

    try:
        return await run_audit(url)
    except InvalidURLError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=exc.message) from exc
    except ScrapingError as exc:
        status_code = (
            status.HTTP_504_GATEWAY_TIMEOUT
            if "timed out" in exc.message.lower()
            else status.HTTP_502_BAD_GATEWAY
        )
        log_error(logger, message=exc.message, url=url)
        raise HTTPException(status_code=status_code, detail=exc.message) from exc
    except PageSpeedError as exc:
        log_error(logger, message=exc.message, url=url)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=exc.message,
        ) from exc
    except OpenAIAnalysisError as exc:
        log_error(logger, message=exc.message, url=url)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=exc.message,
        ) from exc
    except Exception as exc:
        log_error(logger, message=str(exc), url=url)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while running the audit",
        ) from exc
