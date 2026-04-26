"""
Domain event names.

Centralizes event name strings to avoid sprinkling hardcoded values across
application services and tests.
"""

from __future__ import annotations

from enum import Enum


class EventName(str, Enum):
    """Canonical event names emitted to the outbox/event bus."""

    BACKTEST_COMPLETED = "backtest.completed"
    SIGNAL_INGESTED = "signal.ingested"
    SIGNAL_EXECUTED = "signal.executed"

