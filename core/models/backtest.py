from dataclasses import dataclass
from typing import List

from core.models.trade import Trade


@dataclass
class BacktestResult:
    """
    Represents the result of a backtest run.
    """

    trades: List[Trade]
    equity_curve: List[float]
