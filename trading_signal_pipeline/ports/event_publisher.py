"""
Event publishing port.

Used by application services to publish DomainEvent objects (outbox/event bus).
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from trading_signal_pipeline.domain.events import DomainEvent


class EventPublisher(ABC):
    """
    Outbound port for publishing domain events.
    """

    @abstractmethod
    def publish(self, event: DomainEvent) -> None:
        """
        Publish a domain event.

        Implementations may write to an outbox, publish to a broker, etc.
        """
        raise NotImplementedError
