import os
from contextlib import contextmanager
from typing import Any, Iterator

from core.config import settings
from core.logging import get_logger

logger = get_logger(__name__)


def langfuse_enabled() -> bool:
    return bool(
        settings.LANGFUSE_ENABLED
        and settings.LANGFUSE_PUBLIC_KEY
        and settings.LANGFUSE_SECRET_KEY
    )


def init_langfuse() -> None:
    if not langfuse_enabled():
        os.environ["LANGFUSE_TRACING_ENABLED"] = "false"
        if settings.LANGFUSE_ENABLED and not (
            settings.LANGFUSE_PUBLIC_KEY and settings.LANGFUSE_SECRET_KEY
        ):
            logger.warning(
                "Langfuse is enabled but API keys are missing. "
                "Set LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY in .env"
            )
        elif settings.LANGFUSE_PUBLIC_KEY and settings.LANGFUSE_SECRET_KEY and not settings.LANGFUSE_ENABLED:
            logger.warning(
                "Langfuse API keys are set but LANGFUSE_ENABLED=false. "
                "Set LANGFUSE_ENABLED=true to send traces to the dashboard."
            )
        return

    os.environ["LANGFUSE_TRACING_ENABLED"] = "true"
    os.environ["LANGFUSE_PUBLIC_KEY"] = settings.LANGFUSE_PUBLIC_KEY or ""
    os.environ["LANGFUSE_SECRET_KEY"] = settings.LANGFUSE_SECRET_KEY or ""
    os.environ["LANGFUSE_BASE_URL"] = settings.LANGFUSE_HOST
    os.environ["LANGFUSE_HOST"] = settings.LANGFUSE_HOST
    logger.info(
        "Langfuse tracing enabled",
        extra={
            "structured": {
                "event": "langfuse_enabled",
                "host": settings.LANGFUSE_HOST,
            }
        },
    )


def flush_langfuse() -> None:
    if not langfuse_enabled():
        return

    from langfuse import get_client

    get_client().flush()


def shutdown_langfuse() -> None:
    flush_langfuse()


@contextmanager
def langfuse_session(
    *,
    session_id: str,
    metadata: dict[str, Any] | None = None,
    tags: list[str] | None = None,
) -> Iterator[None]:
    if not langfuse_enabled():
        yield
        return

    from langfuse import propagate_attributes

    with propagate_attributes(session_id=session_id, metadata=metadata, tags=tags):
        yield


def update_current_span_attrs(**kwargs: Any) -> None:
    if not langfuse_enabled():
        return

    from langfuse import get_client

    metadata = kwargs.pop("metadata", None)
    session_id = kwargs.pop("session_id", None)
    tags = kwargs.pop("tags", None)

    span_metadata = dict(metadata or {})
    if session_id:
        span_metadata["session_id"] = session_id
    if tags:
        span_metadata["tags"] = tags

    get_client().update_current_span(
        metadata=span_metadata or None,
        **kwargs,
    )


def update_current_generation(**kwargs: Any) -> None:
    if not langfuse_enabled():
        return

    usage = kwargs.pop("usage", None)
    if usage is not None:
        kwargs["usage_details"] = usage

    from langfuse import get_client

    get_client().update_current_generation(**kwargs)


def traced(name: str, *, as_type: str = "span"):
    from langfuse import observe

    return observe(name=name, as_type=as_type)
