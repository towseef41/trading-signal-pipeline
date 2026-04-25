"""
Strategy domain interface.

Strategies are pure functions from a market series to a per-candle signal series.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List

from trading_signal_pipeline.domain.market import MarketSeries
from trading_signal_pipeline.domain.signal import SignalType


class Strategy(ABC):
    """
    Domain strategy contract: pure function from market series to signals.
    """

    @abstractmethod
    def generate(self, series: MarketSeries) -> List[SignalType]:
        """
        Generate a per-candle signal list.

        Args:
            series: Historical candle series.

        Returns:
            List of signals with the same length as ``series``.
        """
        raise NotImplementedError
