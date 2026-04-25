"""
No-op EventPublisher adapter used for tests.
"""

from __future__ import annotations

from trading_signal_pipeline.domain.events import DomainEvent
from trading_signal_pipeline.ports.event_publisher import EventPublisher


class NoOpEventPublisher(EventPublisher):
    def publish(self, event: DomainEvent) -> None:
        """Discard the event."""
        return
