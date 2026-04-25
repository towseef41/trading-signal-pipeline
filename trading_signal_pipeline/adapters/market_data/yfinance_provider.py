"""
Market data provider adapters.

YFinanceMarketDataProvider loads OHLCV candles from yfinance and converts them
to the domain Candle representation.
"""

from __future__ import annotations

from datetime import datetime
from typing import cast

import yfinance as yf
import requests

from trading_signal_pipeline.domain.market import Candle, MarketSeries
from trading_signal_pipeline.ports.market_data_provider import MarketDataProvider
from trading_signal_pipeline.domain.value_objects import Price, Volume


class YFinanceMarketDataProvider(MarketDataProvider):
    """Market data provider backed by Yahoo Finance via `yfinance`.

    Notes:
        Yahoo/yfinance can be rate limited or blocked in some environments (429/403),
        and may fail timezone metadata lookups (`YFTzMissingError`). This adapter
        uses a requests Session + fallback to `Ticker().history()` to improve
        reliability, but callers should prefer the `binance` or `csv` providers
        when deterministic runs are required.
    """

    def __init__(self, default_timezone: str | None = None):
        """
        Args:
            default_timezone: Optional timezone to use when Yahoo timezone metadata
                cannot be fetched (e.g., temporary blocking/rate limiting).

                Example: "America/New_York".

        Notes:
            This can help avoid `YFTzMissingError` in some environments, but it
            cannot fix upstream rate limiting (HTTP 429).
        """
        self.default_timezone = default_timezone

    def load(self, symbol: str, start: str, end: str, interval: str) -> MarketSeries:
        """
        Load a candle series from Yahoo Finance.

        Args:
            symbol: Market symbol.
            start: Start date string.
            end: End date string.
            interval: Interval string accepted by yfinance (e.g. "1d").

        Returns:
            MarketSeries.

        Raises:
            ValueError: If no data is returned.
        """
        # A custom session with a realistic User-Agent reduces the chance of getting blocked
        # by upstreams that dislike default Python clients.
        session = requests.Session()
        session.headers.update(
            {
                "User-Agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/124.0.0.0 Safari/537.36"
                )
            }
        )

        try:
            df = yf.download(
                symbol,
                start=start,
                end=end,
                interval=interval,
                group_by="column",
                auto_adjust=False,
                threads=False,
                ignore_tz=True,
                progress=False,
                timeout=30,
                session=session,
            )
        except Exception as e:  # yfinance raises a few different exception types depending on failure mode
            raise ValueError(
                f"Failed to download data for {symbol} from yfinance: {e}. "
                "This is commonly caused by rate limiting (HTTP 429), a temporary Yahoo outage, "
                "or an invalid symbol."
            ) from e

        # Fallback: yfinance.download() can return empty on some failure modes (e.g. Yahoo returns HTML / 429).
        # history() sometimes succeeds in those cases.
        if df is None or df.empty:
            try:
                t = yf.Ticker(symbol, session=session)
                if self.default_timezone:
                    # yfinance uses this field to short-circuit timezone fetch.
                    t._tz = self.default_timezone  # type: ignore[attr-defined]

                df = t.history(
                    start=start,
                    end=end,
                    interval=interval,
                    auto_adjust=False,
                    actions=False,
                    prepost=False,
                    repair=True,
                    timeout=30,
                )
            except Exception:
                # Keep original empty df for the error message below.
                pass

        if df is None or df.empty:
            raise ValueError(
                f"No data found for {symbol} from yfinance (start={start}, end={end}, interval={interval}). "
                "If you are rate limited (HTTP 429) wait a bit and retry, or use the CLI `--data-file` option "
                "to run against a local CSV (offline-friendly)."
            )

        series: MarketSeries = []
        for idx, row in df.iterrows():
            # yfinance can return pandas.Timestamp; normalize to datetime.
            t = cast(datetime, getattr(idx, "to_pydatetime", lambda: idx)())
            series.append(
                Candle(
                    time=t,
                    open=Price(float(row["Open"])),
                    high=Price(float(row["High"])),
                    low=Price(float(row["Low"])),
                    close=Price(float(row["Close"])),
                    volume=Volume(float(row.get("Volume", 0.0))),
                )
            )
        return series
