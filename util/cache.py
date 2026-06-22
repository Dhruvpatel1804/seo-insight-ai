import json
from urllib.parse import urlparse, urlunparse

from core.config import settings
from core.logging import get_logger

logger = get_logger(__name__)

_redis_client = None
_redis_unavailable_reason: str | None = None


def normalize_audit_url(url: str) -> str:
    parsed = urlparse(url.strip())
    hostname = (parsed.hostname or "").lower()
    if hostname.startswith("www."):
        hostname = hostname[4:]

    port = parsed.port
    if (parsed.scheme == "http" and port == 80) or (parsed.scheme == "https" and port == 443):
        port = None

    netloc = hostname
    if port is not None:
        netloc = f"{hostname}:{port}"

    path = parsed.path.rstrip("/")
    if not path:
        path = ""

    normalized = parsed._replace(
        netloc=netloc,
        path=path,
        params="",
        query="",
        fragment="",
    )
    return urlunparse(normalized)


def get_audit_cache_key(url: str) -> str:
    return f"audit-cache:{normalize_audit_url(url)}"


async def get_redis_client():
    global _redis_client, _redis_unavailable_reason

    if not settings.REDIS_URL:
        return None

    if _redis_client is not None:
        return _redis_client

    if _redis_unavailable_reason is not None:
        return None

    try:
        from redis.asyncio import Redis
    except ModuleNotFoundError:
        _redis_unavailable_reason = "redis package is not installed"
        logger.warning(
            "Redis caching is disabled: %s (install with `pipenv install redis`)",
            _redis_unavailable_reason,
            extra={"structured": {"event": "redis_cache_disabled", "reason": _redis_unavailable_reason}},
        )
        return None

    try:
        _redis_client = Redis.from_url(settings.REDIS_URL, decode_responses=True)
        await _redis_client.ping()
    except Exception as exc:
        _redis_unavailable_reason = str(exc)
        logger.warning(
            "Redis caching is disabled: unable to connect to %s (%s)",
            settings.REDIS_URL,
            exc,
            extra={
                "structured": {
                    "event": "redis_cache_disabled",
                    "redis_url": settings.REDIS_URL,
                    "reason": str(exc),
                }
            },
        )
        _redis_client = None
        return None

    return _redis_client


async def get_cached_audit(url: str) -> dict | None:
    client = await get_redis_client()
    if client is None:
        return None

    cached_value = await client.get(get_audit_cache_key(url))
    if not cached_value:
        return None

    return json.loads(cached_value)


async def set_cached_audit(url: str, payload: dict) -> None:
    client = await get_redis_client()
    if client is None:
        return

    await client.set(
        get_audit_cache_key(url),
        json.dumps(payload),
        ex=settings.AUDIT_CACHE_TTL_SECONDS,
    )
