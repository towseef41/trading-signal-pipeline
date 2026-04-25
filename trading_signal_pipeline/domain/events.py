"""
Domain events.

These events are emitted by application services and written to an outbox via
the EventPublisher port.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from uuid import uuid4


@dataclass(frozen=True)
class DomainEvent:
    """
    Minimal domain event for outbox/event-bus publishing.
    Payload must be JSON-serializable primitives.
    """

    name: str
    payload: Dict[str, Any]
    occurred_at: str
    event_id: str
    correlation_id: Optional[str] = None

    @staticmethod
    def now(name: str, payload: Dict[str, Any], correlation_id: Optional[str] = None) -> "DomainEvent":
        """
        Create a DomainEvent with current timestamp and a random event_id.

        Args:
            name: Event name (e.g. "signal.ingested").
            payload: JSON-serializable primitives.
            correlation_id: Optional correlation key for tracing.
        """
        return DomainEvent(
            name=name,
            payload=payload,
            occurred_at=datetime.now(timezone.utc).isoformat(),
            event_id=str(uuid4()),
            correlation_id=correlation_id,
        )
