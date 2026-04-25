"""
Backtest result domain model.

BacktestResult is the output of a backtest run and the input to metrics/reporting.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from trading_signal_pipeline.domain.fill import Fill
from trading_signal_pipeline.domain.trade import Trade


@dataclass(frozen=True)
class BacktestResult:
    """Immutable backtest output (trades and equity curve)."""

    trades: List[Trade]
    equity_curve: List[float]
    fills: List[Fill] = field(default_factory=list)
