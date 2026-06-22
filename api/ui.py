from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import FileResponse

ui_router = APIRouter(include_in_schema=False)

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"


@ui_router.get("/", response_class=FileResponse)
async def audit_ui() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")
