# core/metrics/base.py

from abc import ABC, abstractmethod
from typing import List, Dict


class Metric(ABC):
    """
    Base interface for all performance metrics.
    """

    @abstractmethod
    def compute(
        self,
        trades: List[Dict],
        equity_curve: List[float],
        initial_capital: float,
    ) -> float:
        pass

    @abstractmethod
    def name(self) -> str:
        pass