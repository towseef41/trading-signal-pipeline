"""
Execution fill domain model.

A Fill represents a single executed action (BUY/SELL) at a specific time/price.
Backtests record fills so evaluators can see both entry and exit legs.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from trading_signal_pipeline.domain.types import Side
from trading_signal_pipeline.domain.value_objects import Price, Quantity, Symbol


@dataclass(frozen=True)
class Fill:
    """A single executed fill (entry/exit leg)."""

    symbol: Symbol
    side: Side
    price: Price
    quantity: Quantity
    time: datetime

