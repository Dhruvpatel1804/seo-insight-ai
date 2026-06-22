import re

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import FileResponse

from services.audit_service import get_report_path

router = APIRouter()

AUDIT_ID_PATTERN = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$",
    re.IGNORECASE,
)


@router.get("/{audit_id}")
async def download_report(audit_id: str) -> FileResponse:
    if not AUDIT_ID_PATTERN.match(audit_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid audit ID format",
        )

    report_path = get_report_path(audit_id)
    if report_path is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found",
        )

    return FileResponse(
        path=report_path,
        media_type="application/json",
        filename="seo_audit_report.json",
    )
