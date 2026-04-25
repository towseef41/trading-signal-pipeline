"""
Metrics engine.

Computes a collection of Metric implementations and returns a dict of results.
"""

from typing import List, Dict

from trading_signal_pipeline.ports.metric import Metric
from trading_signal_pipeline.ports.metrics_calculator import MetricsCalculator


class MetricsEngine(MetricsCalculator):
    """
    Executes a collection of metrics.
    """

    def __init__(self, metrics: List[Metric]):
        """
        Args:
            metrics: Metric implementations to compute.
        """
        self.metrics = metrics

    def compute_all(self, trades, equity_curve, initial_capital) -> Dict:
        """
        Compute all configured metrics.

        Args:
            trades: Completed trades.
            equity_curve: Per-tick equity values.
            initial_capital: Starting capital.

        Returns:
            Dict of metric name -> metric value.
        """
        results = {}

        for metric in self.metrics:
            results[metric.name()] = metric.compute(
                trades, equity_curve, initial_capital
            )

        return results
