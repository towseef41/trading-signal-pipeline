"""
Trade domain model.

Trade is produced by the backtesting execution policy when a position is closed.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from trading_signal_pipeline.domain.types import Side
from trading_signal_pipeline.domain.value_objects import Price, Quantity, Symbol


@dataclass(frozen=True)
class Trade:
    """
    Domain Trade entity capturing an opened and closed position.
    """

    symbol: Symbol
    side: Side
    entry_price: Price
    exit_price: Price
    quantity: Quantity
    pnl: float
    entry_time: Optional[datetime] = None
    exit_time: Optional[datetime] = None

    def __post_init__(self) -> None:
        """Validate trade invariants."""
        # Symbol/Price/Quantity validate their own invariants.
        pass
