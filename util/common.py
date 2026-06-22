from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse


async def custom_http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        content={
            "status_code": exc.status_code,
            "message": exc.detail,
            "data": None,
        },
        status_code=exc.status_code,
    )
