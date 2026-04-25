"""
Market data domain model.

The domain represents market data as a list of Candle objects, independent from
pandas or any specific data provider.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Iterable, List

from trading_signal_pipeline.domain.value_objects import Price, Volume

@dataclass(frozen=True)
class Candle:
    """
    Domain representation of OHLCV market data.
    """

    time: datetime
    open: Price
    high: Price
    low: Price
    close: Price
    volume: Volume

    def __post_init__(self) -> None:
        """Validate candle invariants (OHLC consistency)."""
        # Keep invariants lightweight; value objects validate sign already.
        if float(self.high) < max(float(self.open), float(self.close), float(self.low)):
            raise ValueError("high must be >= open/close/low")
        if float(self.low) > min(float(self.open), float(self.close), float(self.high)):
            raise ValueError("low must be <= open/close/high")


MarketSeries = List[Candle]


def closes(series: Iterable[Candle]) -> List[float]:
    """Extract close prices from a candle series."""
    return [float(c.close) for c in series]
