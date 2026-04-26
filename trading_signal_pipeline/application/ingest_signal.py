"""
Signal ingestion use-case.

This application service:
  - constructs a SignalEvent from primitives
  - enforces idempotency via SignalRepository
  - calls a Broker port to execute
  - publishes domain events via EventPublisher
"""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from typing import Tuple, Optional

from trading_signal_pipeline.domain.execution import ExecutionResult
from trading_signal_pipeline.domain.events import DomainEvent
from trading_signal_pipeline.domain.signal import SignalEvent
from trading_signal_pipeline.ports.signal_repository import SignalRepository
from trading_signal_pipeline.ports.broker import Broker
from trading_signal_pipeline.domain.value_objects import Price, Quantity, Symbol
from trading_signal_pipeline.ports.event_publisher import EventPublisher
from trading_signal_pipeline.serialization.primitives import execution_result_to_dict, signal_event_to_dict


class DuplicateSignalError(Exception):
    """Raised when a signal is rejected due to idempotency/duplication."""

    pass


class IngestSignalService:
    """
    Application service for webhook signal ingestion.
    """

    def __init__(self, repo: SignalRepository, broker: Broker, publisher: EventPublisher):
        """
        Args:
            repo: SignalRepository for idempotency and persistence.
            broker: Broker port for execution.
            publisher: EventPublisher for outbox/event emission.
        """
        self.repo = repo
        self.broker = broker
        self.publisher = publisher

    def ingest(
        self,
        symbol: str,
        side: str,
        qty: float,
        price: float,
        idempotency_key: Optional[str] = None,
        correlation_id: Optional[str] = None,
    ) -> Tuple[SignalEvent, ExecutionResult]:
        """
        Ingest and execute a trade signal.

        Args:
            symbol: Market symbol (e.g. "AAPL").
            side: "BUY" or "SELL".
            qty: Quantity (> 0).
            price: Price (> 0).
            idempotency_key: Optional caller-provided idempotency key (preferred in production).
            correlation_id: Optional correlation id used for event publishing (e.g. request id).

        Returns:
            Tuple of (SignalEvent, ExecutionResult).

        Raises:
            DuplicateSignalError: If the signal is a duplicate.
            ValueError: If value object validation fails.
        """
        received_at = datetime.now(timezone.utc)
        idem = idempotency_key or self._idempotency_key(symbol, side, qty, price)

        event = SignalEvent(
            symbol=Symbol(symbol),
            side=side,  # type: ignore[arg-type]
            qty=Quantity(qty),
            price=Price(price),
            received_at=received_at,
            idempotency_key=idem,
        )

        if self.repo.is_duplicate(event):
            raise DuplicateSignalError("Duplicate signal")

        self.repo.add(event)
        execution = self.broker.execute(event)

        corr = correlation_id or event.idempotency_key
        self.publisher.publish(
            DomainEvent.now(
                name="signal.ingested",
                payload={"signal": signal_event_to_dict(event)},
                correlation_id=corr,
            )
        )
        self.publisher.publish(
            DomainEvent.now(
                name="signal.executed",
                payload={"signal": signal_event_to_dict(event), "execution": execution_result_to_dict(execution)},
                correlation_id=corr,
            )
        )

        return event, execution

    def _idempotency_key(self, symbol: str, side: str, qty: float, price: float) -> str:
        """
        Create a deterministic hash for idempotency.

        The current scheme uses the tuple (symbol, side, qty, price).
        """
        payload = {"symbol": symbol, "side": side, "qty": qty, "price": price}
        raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        return hashlib.sha256(raw).hexdigest()
