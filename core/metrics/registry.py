# core/metrics/registry.py

from typing import List, Dict

from core.metrics.base import Metric


class MetricsEngine:
    """
    Executes a collection of metrics.
    """

    def __init__(self, metrics: List[Metric]):
        self.metrics = metrics

    def compute_all(self, trades, equity_curve, initial_capital) -> Dict:
        results = {}

        for metric in self.metrics:
            results[metric.name()] = metric.compute(
                trades, equity_curve, initial_capital
            )

        return results