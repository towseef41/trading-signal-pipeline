"""
Market data provider port.

Backtesting use-cases call this port to load historical data as a domain candle series.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from trading_signal_pipeline.domain.market import MarketSeries


class MarketDataProvider(ABC):
    """
    Outbound port for loading historical market data.
    """

    @abstractmethod
    def load(
        self,
        symbol: str,
        start: str,
        end: str,
        interval: str,
    ) -> MarketSeries:
        """
        Load historical market data as a candle series.

        Args:
            symbol: Market symbol.
            start: Start date (provider-dependent format).
            end: End date (provider-dependent format).
            interval: Candlestick interval (e.g. "1d").

        Returns:
            MarketSeries.
        """
        raise NotImplementedError
