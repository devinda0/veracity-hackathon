"""JSON logger utility with structured key/value support."""

import json
import logging
from datetime import datetime, timezone
from typing import Any


class JSONFormatter(logging.Formatter):
    """Format log records as line-delimited JSON objects."""

    def format(self, record: logging.LogRecord) -> str:
        log_payload: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        extra_fields = getattr(record, "fields", None)
        if isinstance(extra_fields, dict):
            log_payload.update(extra_fields)

        if record.exc_info:
            log_payload["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_payload, default=str)


class StructuredLogger:
    """Thin wrapper that allows logger.info(..., key=value) style calls."""

    def __init__(self, logger: logging.Logger):
        self._logger = logger

    def debug(self, message: str, **fields: Any) -> None:
        self._logger.debug(message, extra={"fields": fields})

    def info(self, message: str, **fields: Any) -> None:
        self._logger.info(message, extra={"fields": fields})

    def warning(self, message: str, **fields: Any) -> None:
        self._logger.warning(message, extra={"fields": fields})

    def error(self, message: str, **fields: Any) -> None:
        self._logger.error(message, extra={"fields": fields})

    def exception(self, message: str, **fields: Any) -> None:
        self._logger.exception(message, extra={"fields": fields})


def get_logger(name: str) -> StructuredLogger:
    """Create or retrieve a structured JSON logger by name."""
    base_logger = logging.getLogger(name)

    if not base_logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(JSONFormatter())
        base_logger.addHandler(handler)
        base_logger.setLevel(logging.INFO)
        base_logger.propagate = False

    return StructuredLogger(base_logger)
