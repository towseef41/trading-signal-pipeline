"""
Logging configuration.

Used by the FastAPI interface layer to log inbound webhook traffic.
"""

from __future__ import annotations

import json
import logging
import time
from typing import Any, Dict

from trading_signal_pipeline.adapters.logging.request_context import get_request_id


class RequestContextFilter(logging.Filter):
    """Attach request-scoped context to log records."""

    def filter(self, record: logging.LogRecord) -> bool:  # noqa: A003 - filter is the stdlib name
        record.request_id = get_request_id()
        return True


class JsonFormatter(logging.Formatter):
    """Minimal JSON log formatter (single line)."""

    def format(self, record: logging.LogRecord) -> str:
        payload: Dict[str, Any] = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(record.created)),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": getattr(record, "request_id", None),
        }

        # Include selected custom fields passed via `extra=...`.
        for key, value in record.__dict__.items():
            if key in payload:
                continue
            if key.startswith("_"):
                continue
            if key in {
                "args",
                "asctime",
                "created",
                "exc_info",
                "exc_text",
                "filename",
                "funcName",
                "levelname",
                "levelno",
                "lineno",
                "module",
                "msecs",
                "msg",
                "name",
                "pathname",
                "process",
                "processName",
                "relativeCreated",
                "stack_info",
                "thread",
                "threadName",
                "request_id",
            }:
                continue
            payload[key] = value

        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)

        return json.dumps(payload, separators=(",", ":"), ensure_ascii=True)


logger = logging.getLogger("signal_api")
logger.setLevel(logging.INFO)

if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    handler.addFilter(RequestContextFilter())
    logger.addHandler(handler)
    logger.propagate = False
