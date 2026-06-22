import json
import logging
import os
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler
from typing import Any

from core.config import settings


class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        if hasattr(record, "structured"):
            payload.update(record.structured)

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        return json.dumps(payload, default=str)


def setup_logging() -> logging.Logger:
    os.makedirs(settings.LOG_DIR, exist_ok=True)

    formatter = JSONFormatter()
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.LOG_LEVEL))

    if not root_logger.handlers:
        app_log_path = os.path.join(settings.LOG_DIR, "app.log")
        error_log_path = os.path.join(settings.LOG_DIR, "error.log")

        app_handler = RotatingFileHandler(
            app_log_path,
            maxBytes=settings.LOG_MAX_BYTES,
            backupCount=settings.LOG_BACKUP_COUNT,
        )
        app_handler.setLevel(logging.DEBUG)
        app_handler.setFormatter(formatter)

        error_handler = RotatingFileHandler(
            error_log_path,
            maxBytes=settings.LOG_MAX_BYTES,
            backupCount=settings.LOG_BACKUP_COUNT,
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, settings.LOG_LEVEL))
        console_handler.setFormatter(formatter)

        root_logger.addHandler(app_handler)
        root_logger.addHandler(error_handler)
        root_logger.addHandler(console_handler)

    logging.getLogger("httpx").setLevel(getattr(logging, settings.LOG_HTTPX_LEVEL))

    return root_logger


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


def _log_structured(logger: logging.Logger, level: int, message: str, **fields: Any) -> None:
    record = logger.makeRecord(
        logger.name,
        level,
        "(structured)",
        0,
        message,
        (),
        None,
    )
    record.structured = fields
    logger.handle(record)


def log_audit_start(logger: logging.Logger, *, audit_id: str, url: str) -> None:
    _log_structured(logger, logging.INFO, "audit_start", event="audit_start", audit_id=audit_id, url=url)


def log_audit_complete(
    logger: logging.Logger,
    *,
    audit_id: str,
    url: str,
    audit_duration_ms: float,
) -> None:
    _log_structured(
        logger,
        logging.INFO,
        "audit_complete",
        event="audit_complete",
        audit_id=audit_id,
        url=url,
        audit_duration_ms=round(audit_duration_ms, 2),
    )


def log_pagespeed_latency(
    logger: logging.Logger,
    *,
    audit_id: str,
    strategy: str,
    pagespeed_latency_ms: float,
) -> None:
    _log_structured(
        logger,
        logging.INFO,
        "pagespeed_latency",
        event="pagespeed_latency",
        audit_id=audit_id,
        strategy=strategy,
        pagespeed_latency_ms=round(pagespeed_latency_ms, 2),
    )


def log_openai_latency(
    logger: logging.Logger,
    *,
    audit_id: str,
    openai_latency_ms: float,
    prompt_tokens: int,
    completion_tokens: int,
    total_tokens: int,
) -> None:
    _log_structured(
        logger,
        logging.INFO,
        "openai_latency",
        event="openai_latency",
        audit_id=audit_id,
        openai_latency_ms=round(openai_latency_ms, 2),
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        total_tokens=total_tokens,
    )


def log_error(
    logger: logging.Logger,
    *,
    message: str,
    audit_id: str | None = None,
    **fields: Any,
) -> None:
    _log_structured(
        logger,
        logging.ERROR,
        message,
        event="error",
        audit_id=audit_id,
        error=message,
        **fields,
    )


def log_event(logger: logging.Logger, event: str, **fields: Any) -> None:
    _log_structured(logger, logging.INFO, event, event=event, **fields)


def log_cache_event(logger: logging.Logger, event: str, **fields: Any) -> None:
    log_event(logger, event, **fields)
