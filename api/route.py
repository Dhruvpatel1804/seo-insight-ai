from fastapi import APIRouter
from api import user_managementAPI

api_router = APIRouter()

api_router.include_router(user_managementAPI.router, prefix="/auth", tags=["user_management"])
