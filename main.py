from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from api.route import api_router
from api.ui import ui_router
from core.config import settings
from core.logging import get_logger, log_event, setup_logging
from util.common import custom_http_exception_handler
from util.langfuse_tracing import init_langfuse, shutdown_langfuse

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup and shutdown logging."""
    setup_logging()
    init_langfuse()
    log_event(logger, "application_startup")
    yield
    shutdown_langfuse()
    log_event(logger, "application_shutdown")


def start_application():
    """Create and configure the FastAPI application instance."""
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.PROJECT_VERSION,
        description="AI-powered SEO page auditor with Core Web Vitals analysis.",
        lifespan=lifespan,
        docs_url=settings.API_SWAGGER_PATH if settings.API_DOCS_ENABLED else None,
        redoc_url=settings.API_REDOC_PATH if settings.API_DOCS_ENABLED else None,
        debug=settings.DEBUG,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.API_CORS_ORIGINS,
        allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
        allow_methods=settings.CORS_ALLOW_METHODS,
        allow_headers=settings.CORS_ALLOW_HEADERS,
    )

    app.add_exception_handler(HTTPException, custom_http_exception_handler)
    # UI router first and API router second
    app.include_router(ui_router)
    app.include_router(api_router)

    return app


app = start_application()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.API_RELOAD,
    )
