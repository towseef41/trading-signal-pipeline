"""
Report composer port.

This port abstracts report composition given metrics, trades, and signals.
It keeps use-cases independent from a specific report engine implementation.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List

from trading_signal_pipeline.domain.trade import Trade


class ReportComposer(ABC):
    """Compose a report from computed metrics and stored domain data."""

    @abstractmethod
    def generate(
        self,
        metrics: Dict[str, Any],
        trades: List[Trade],
        signals: List[Any],
    ) -> Dict[str, Any]:
        """
        Generate a JSON-serializable report.

        Args:
            metrics: Metric name -> value.
            trades: Completed trades.
            signals: Ingested signals (primitive dicts).

        Returns:
            Report dictionary.
        """
        raise NotImplementedError

