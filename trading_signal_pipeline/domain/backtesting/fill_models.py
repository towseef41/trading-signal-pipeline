"""
Fill price model implementations (domain policies).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from trading_signal_pipeline.domain.market import Candle
from trading_signal_pipeline.domain.types import Side
from trading_signal_pipeline.ports.fill_price_model import FillDecision, FillPriceModel


@dataclass(frozen=True)
class SameBarCloseFillModel(FillPriceModel):
    """Fill at the signal candle close (common simplification)."""

    def decide(self, *, side: Side, candle: Candle, next_candle: Optional[Candle]) -> Optional[FillDecision]:
        return FillDecision(price=candle.close, time=candle.time)


@dataclass(frozen=True)
class NextBarOpenFillModel(FillPriceModel):
    """Fill at the next candle open (more realistic than same-bar close)."""

    def decide(self, *, side: Side, candle: Candle, next_candle: Optional[Candle]) -> Optional[FillDecision]:
        if next_candle is None:
            return None
        return FillDecision(price=next_candle.open, time=next_candle.time)

