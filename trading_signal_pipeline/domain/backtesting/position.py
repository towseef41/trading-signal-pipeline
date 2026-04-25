"""
Position domain model for backtesting.

Represents a single open position (or flat) for the simplified engine.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from trading_signal_pipeline.domain.value_objects import Price, Quantity, Symbol


@dataclass
class Position:
    """Mutable position state used during a backtest run."""

    symbol: Symbol = Symbol("UNKNOWN")
    quantity: Optional[Quantity] = None
    entry_price: Optional[Price] = None
    entry_time: Optional[datetime] = None

    @property
    def is_open(self) -> bool:
        """Return True if the position is open (has quantity and entry_price)."""
        return self.quantity is not None and self.entry_price is not None
