from fastapi import APIRouter

from api.v1 import audit, reports

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(audit.router, tags=["audit"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
