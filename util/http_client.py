import httpx

from core.config import settings
from util.url_validator import get_http_client_limits


def create_http_client() -> httpx.AsyncClient:
    limits = get_http_client_limits()
    return httpx.AsyncClient(
        timeout=httpx.Timeout(limits["timeout"]),
        follow_redirects=True,
        max_redirects=limits["max_redirects"],
        headers={"User-Agent": settings.HTTP_USER_AGENT},
    )
