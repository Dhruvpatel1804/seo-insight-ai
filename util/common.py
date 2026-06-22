import re
import string
import secrets
import logging
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse

from core.config import settings

logger = logging.getLogger(__name__)

def format_response(response=None, status_code=200, message=""):
    """
    Standardized response format for the application.
    """
    data = response
    if hasattr(response, "json"):
        try:
            data = response.json()
        except Exception:
            data = response.content.decode() if hasattr(response, "content") else str(response)

    return JSONResponse(
        content={
            "status_code": status_code,
            "message": message,
            "data": data
        },
        status_code=status_code
    )

async def custom_http_exception_handler(request: Request, exc: HTTPException):
    """
    Custom handler for HTTPException to match the standard response format.
    """
    return JSONResponse(
        content={
            "status_code": exc.status_code,
            "message": exc.detail,
            "data": None
        },
        status_code=exc.status_code
    )

def generate_random_string(length: int) -> str:
    characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(characters) for _ in range(length))

