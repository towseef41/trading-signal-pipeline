"""
Fill price model port.

A fill price model decides *when* and *at what price* a backtest execution fills
an order, given the candle where the signal was observed and (optionally) the
next candle.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from trading_signal_pipeline.domain.market import Candle
from trading_signal_pipeline.domain.types import Side
from trading_signal_pipeline.domain.value_objects import Price


@dataclass(frozen=True)
class FillDecision:
    """Decision returned by a fill model (price + timestamp)."""

    price: Price
    time: datetime


class FillPriceModel(ABC):
    """Port for deciding fill price/time given a signal and candle context."""

    @abstractmethod
    def decide(self, *, side: Side, candle: Candle, next_candle: Optional[Candle]) -> Optional[FillDecision]:
        """
        Decide fill price/time.

        Args:
            side: "BUY" or "SELL".
            candle: The candle that produced the signal.
            next_candle: The next candle (if available).

        Returns:
            FillDecision, or None if no fill is possible (e.g. next candle missing).
        """
        raise NotImplementedError

