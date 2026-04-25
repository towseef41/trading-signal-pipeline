"""
Metrics calculator port.

This port abstracts the computation of metrics over trades and an equity curve.
It keeps use-cases independent from a specific "metrics engine" implementation.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List

from trading_signal_pipeline.domain.trade import Trade


class MetricsCalculator(ABC):
    """Compute one or more metrics over a backtest result."""

    @abstractmethod
    def compute_all(
        self,
        trades: List[Trade],
        equity_curve: List[float],
        initial_capital: float,
    ) -> Dict[str, Any]:
        """
        Compute all configured metrics.

        Args:
            trades: Completed trades.
            equity_curve: Per-tick equity values.
            initial_capital: Starting capital.

        Returns:
            Dict of metric name -> metric value.
        """
        raise NotImplementedError

