"""
Execution domain model.

ExecutionResult represents the outcome of sending a signal to a broker/execution
adapter (real or mocked).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from trading_signal_pipeline.domain.types import Side
from trading_signal_pipeline.domain.value_objects import Price, Quantity, Symbol


@dataclass(frozen=True)
class ExecutionResult:
    """Result of a broker execution attempt."""

    status: Literal["filled", "rejected", "error"]
    symbol: Symbol
    side: Side
    qty: Quantity
    price: Price

    def __post_init__(self) -> None:
        """Validate result invariants."""
        # Symbol/Price/Quantity validate their own invariants.
        pass
