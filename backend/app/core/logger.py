import json
import logging
import sys
from datetime import UTC, datetime
from typing import Any


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        extra = getattr(record, "extra", None)
        if isinstance(extra, dict):
            payload.update(extra)

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        return json.dumps(payload, default=str)


def configure_logging(level: int = logging.INFO) -> None:
    root_logger = logging.getLogger()
    if getattr(root_logger, "_vector_agents_configured", False):
        return

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())

    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(level)
    setattr(root_logger, "_vector_agents_configured", True)


class BoundLogger:
    def __init__(self, logger: logging.Logger) -> None:
        self._logger = logger

    def _log(self, level: int, message: str, **extra: Any) -> None:
        self._logger.log(level, message, extra={"extra": extra})

    def info(self, message: str, **extra: Any) -> None:
        self._log(logging.INFO, message, **extra)

    def warning(self, message: str, **extra: Any) -> None:
        self._log(logging.WARNING, message, **extra)

    def error(self, message: str, **extra: Any) -> None:
        self._log(logging.ERROR, message, **extra)

    def exception(self, message: str, **extra: Any) -> None:
        self._logger.exception(message, extra={"extra": extra})


def get_logger(name: str) -> BoundLogger:
    return BoundLogger(logging.getLogger(name))

