import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from core.config import settings
from api.route import api_router
from util.common import custom_http_exception_handler

# --- Logging Setup ---
def setup_logging():
    log_format = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    formatter = logging.Formatter(log_format)

    # Ensure logs directory exists
    import os
    if not os.path.exists("logs"):
        os.makedirs("logs")

    from logging.handlers import RotatingFileHandler
    
    # Success Logs (INFO)
    success_handler = RotatingFileHandler("logs/success.log", maxBytes=5_000_000, backupCount=5)
    success_handler.setLevel(logging.INFO)
    success_handler.setFormatter(formatter)

    # Warning Logs
    warning_handler = RotatingFileHandler("logs/warning.log", maxBytes=5_000_000, backupCount=5)
    warning_handler.setLevel(logging.WARNING)
    warning_handler.setFormatter(formatter)

    # Error Logs
    error_handler = RotatingFileHandler("logs/error.log", maxBytes=5_000_000, backupCount=5)
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(success_handler)
    logger.addHandler(warning_handler)
    logger.addHandler(error_handler)
    
    return logger

# --- Lifespan ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    setup_logging()
    logging.info("Starting up application...")
    yield
    # Shutdown logic
    logging.info("Shutting down application...")

# --- OpenAPI Customization ---
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=settings.PROJECT_NAME,
        version=settings.PROJECT_VERSION,
        description="This is a full-fledged FastAPI boilerplate with Auth module.",
        routes=app.routes,
    )
    
    # Security Scheme [Swagger UI shows 🔒 Authorize button]
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    openapi_schema["security"] = [{"BearerAuth": []}]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

def start_application():
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.PROJECT_VERSION,
        lifespan=lifespan,
        docs_url="/swagger-docs/",
        redoc_url="/custom-docs/",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    app.add_exception_handler(HTTPException, custom_http_exception_handler)
    app.include_router(api_router)
    
    # Set custom openapi
    app.openapi = custom_openapi
    
    return app

app = start_application()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)