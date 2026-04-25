"""
Signal domain model.

This module contains the signal enum used by strategies/backtesting and the
SignalEvent entity created when ingesting webhooks.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import IntEnum

from trading_signal_pipeline.domain.types import Side
from trading_signal_pipeline.domain.value_objects import Price, Quantity, Symbol


class SignalType(IntEnum):
    """Discrete strategy/backtesting signals."""

    BUY = 1
    SELL = -1
    HOLD = 0


@dataclass(frozen=True)
class SignalEvent:
    """
    Domain representation of an ingested trade signal.
    """

    symbol: Symbol
    side: Side
    qty: Quantity
    price: Price
    received_at: datetime
    idempotency_key: str

    def __post_init__(self) -> None:
        """Validate event invariants."""
        # Symbol/Price/Quantity validate their own invariants.
        if not self.idempotency_key or not self.idempotency_key.strip():
            raise ValueError("idempotency_key must be non-empty")
