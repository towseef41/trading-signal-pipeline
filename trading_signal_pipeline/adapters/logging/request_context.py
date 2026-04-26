"""
Request-scoped context helpers.

These utilities provide a lightweight way to attach request context (such as a
request id) to logs and application events without coupling domain code to
FastAPI/Starlette types.
"""

from __future__ import annotations

from contextvars import ContextVar
from typing import Optional

_request_id: ContextVar[Optional[str]] = ContextVar("request_id", default=None)


def set_request_id(value: str) -> None:
    """Set the current request id for the running context."""
    _request_id.set(value)


def get_request_id() -> Optional[str]:
    """Get the current request id (if set)."""
    return _request_id.get()


def clear_request_id() -> None:
    """Clear the current request id for the running context."""
    _request_id.set(None)

