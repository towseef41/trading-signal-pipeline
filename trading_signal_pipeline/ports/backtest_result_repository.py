"""
Backtest result repository port.

This port abstracts persistence of the latest BacktestResult.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from trading_signal_pipeline.domain.backtest_result import BacktestResult


class BacktestResultRepository(ABC):
    """
    Persistence port for backtest results.
    """

    @abstractmethod
    def get_latest(self) -> Optional[BacktestResult]:
        """
        Get the latest stored backtest result.

        Returns:
            BacktestResult or None if not present.
        """
        raise NotImplementedError

    @abstractmethod
    def save_latest(self, result: BacktestResult) -> None:
        """
        Persist the latest backtest result.

        Args:
            result: BacktestResult to persist.
        """
        raise NotImplementedError
