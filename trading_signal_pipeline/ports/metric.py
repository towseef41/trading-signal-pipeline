"""
Metric plugin port.

Metrics are application-level plugins computed from trades and an equity curve.
They are modeled as ports to keep the metrics engine/use-cases independent from
concrete metric implementations.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List

from trading_signal_pipeline.domain.trade import Trade


class Metric(ABC):
    """Interface for a single metric implementation."""

    @abstractmethod
    def compute(
        self,
        trades: List[Trade],
        equity_curve: List[float],
        initial_capital: float,
    ) -> float:
        """
        Compute a metric value.

        Args:
            trades: Completed trades.
            equity_curve: Per-tick equity values.
            initial_capital: Starting capital for normalization.

        Returns:
            Metric value.
        """
        raise NotImplementedError

    @abstractmethod
    def name(self) -> str:
        """Return the metric identifier used as a dictionary key."""
        raise NotImplementedError

