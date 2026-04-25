"""
No-op EventPublisher adapter used for tests.
"""

from __future__ import annotations

from trading_signal_pipeline.domain.events import DomainEvent
from trading_signal_pipeline.ports.event_publisher import EventPublisher


class NoOpEventPublisher(EventPublisher):
    """Event publisher that intentionally discards all events.

    Useful for tests and local runs where you don't want to persist/emit outbox events.
    """

    def publish(self, event: DomainEvent) -> None:
        """Discard the event."""
        return
