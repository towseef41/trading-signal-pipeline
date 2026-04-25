"""
EMA crossover strategy (domain implementation).

Implements a simple EMA(short) / EMA(long) crossover producing BUY/SELL/HOLD.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from trading_signal_pipeline.domain.market import MarketSeries, closes
from trading_signal_pipeline.domain.signal import SignalType
from trading_signal_pipeline.domain.strategy import Strategy


def _ema(values: List[float], span: int) -> List[float]:
    """
    Compute EMA over a list of values.

    Args:
        values: Price series.
        span: EMA span parameter (must be >= 1).

    Returns:
        EMA series aligned with ``values``.
    """
    if not values:
        return []
    alpha = 2.0 / (span + 1.0)
    out = [values[0]]
    for v in values[1:]:
        out.append(alpha * v + (1.0 - alpha) * out[-1])
    return out


@dataclass(frozen=True)
class EMACrossoverStrategy(Strategy):
    """EMA(short) / EMA(long) crossover strategy."""

    short_window: int = 9
    long_window: int = 21

    def generate(self, series: MarketSeries) -> List[SignalType]:
        """
        Generate crossover signals for a candle series.

        Args:
            series: Candle series.

        Returns:
            List of SignalType for each candle.
        """
        cs = closes(series)
        ema_s = _ema(cs, self.short_window)
        ema_l = _ema(cs, self.long_window)

        signals: List[SignalType] = [SignalType.HOLD for _ in cs]
        for i in range(1, len(cs)):
            prev_s, prev_l = ema_s[i - 1], ema_l[i - 1]
            cur_s, cur_l = ema_s[i], ema_l[i]

            if prev_s <= prev_l and cur_s > cur_l:
                signals[i] = SignalType.BUY
            elif prev_s >= prev_l and cur_s < cur_l:
                signals[i] = SignalType.SELL

        return signals
