# core/metrics/base.py

from abc import ABC, abstractmethod
from typing import List

from core.models.trade import Trade


class Metric(ABC):
    """
    Base interface for all performance metrics.
    """

    @abstractmethod
    def compute(
        self,
        trades: List[Trade],
        equity_curve: List[float],
        initial_capital: float,
    ) -> float:
        pass

    @abstractmethod
    def name(self) -> str:
        pass