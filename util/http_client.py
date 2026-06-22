import httpx

from core.config import settings


def create_http_client(*, timeout_seconds: int | None = None) -> httpx.AsyncClient:
    return httpx.AsyncClient(
        timeout=httpx.Timeout(timeout_seconds or settings.HTTP_TIMEOUT_SECONDS),
        follow_redirects=True,
        max_redirects=settings.MAX_REDIRECTS,
        headers={"User-Agent": settings.HTTP_USER_AGENT},
    )
