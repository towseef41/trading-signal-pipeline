"""
Market data provider adapter (Binance).

Loads OHLCV candles from Binance's public REST API (no API key required for
historical klines).

API docs:
  https://binance-docs.github.io/apidocs/spot/en/#kline-candlestick-data

Notes:
  - Symbols are Binance symbols like "BTCUSDT" (not "BTC-USD").
  - The API returns up to 1000 candles per request; this adapter paginates.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

import requests

from trading_signal_pipeline.domain.market import Candle, MarketSeries
from trading_signal_pipeline.domain.value_objects import Price, Volume
from trading_signal_pipeline.ports.market_data_provider import MarketDataProvider


class BinanceMarketDataProvider(MarketDataProvider):
    """Load OHLCV candles from Binance."""

    def __init__(
        self,
        base_url: str = "https://api.binance.com",
        session: Optional[requests.Session] = None,
    ):
        self.base_url = base_url.rstrip("/")
        self.session = session or requests.Session()

    def load(self, symbol: str, start: str, end: str, interval: str) -> MarketSeries:
        """
        Load a candle series from Binance.

        Args:
            symbol: Binance market symbol (e.g. "BTCUSDT").
            start: Start date/time string (ISO date like "2024-01-01" recommended).
            end: End date/time string (ISO date like "2024-02-01" recommended).
            interval: Binance interval (e.g. "1m", "5m", "1h", "1d", "1w").

        Returns:
            MarketSeries.
        """
        start_ms = _to_epoch_ms(start)
        end_ms = _to_epoch_ms(end)
        if end_ms <= start_ms:
            raise ValueError("end must be after start")

        url = f"{self.base_url}/api/v3/klines"

        series: MarketSeries = []
        cursor = start_ms
        limit = 1000

        while cursor < end_ms:
            params = {
                "symbol": symbol.upper(),
                "interval": interval,
                "startTime": cursor,
                "endTime": end_ms,
                "limit": limit,
            }
            resp = self.session.get(url, params=params, timeout=30)
            if resp.status_code != 200:
                raise ValueError(
                    f"Binance kline fetch failed (HTTP {resp.status_code}): {resp.text[:200]}"
                )

            data = resp.json()
            if not data:
                break

            # Each kline:
            # [ openTime, open, high, low, close, volume, closeTime, ... ]
            for k in data:
                t = datetime.fromtimestamp(int(k[0]) / 1000.0, tz=timezone.utc)
                series.append(
                    Candle(
                        time=t,
                        open=Price(float(k[1])),
                        high=Price(float(k[2])),
                        low=Price(float(k[3])),
                        close=Price(float(k[4])),
                        volume=Volume(float(k[5])),
                    )
                )

            # Advance cursor to the next millisecond after the last candle open time
            last_open_time_ms = int(data[-1][0])
            cursor = last_open_time_ms + 1

            # Safety: if Binance returns the same last_open_time repeatedly, avoid infinite loop
            if len(data) == 1 and last_open_time_ms < start_ms:
                break

        if not series:
            raise ValueError(f"No data found for {symbol} on Binance (start={start}, end={end}, interval={interval})")

        return series


def _to_epoch_ms(s: str) -> int:
    """
    Convert an ISO date/time string into epoch milliseconds (UTC).
    """
    dt = datetime.fromisoformat(s)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)
    return int(dt.timestamp() * 1000)

