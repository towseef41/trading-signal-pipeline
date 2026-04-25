"""
Market data provider adapter (CSV).

This provider enables offline/local backtests by loading candles from a CSV file.
Expected columns (case-sensitive):
  - Date (ISO-8601 or any format `datetime.fromisoformat` can parse)
  - Open, High, Low, Close
  - Volume (optional; defaults to 0)
"""

from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path

from trading_signal_pipeline.domain.market import Candle, MarketSeries
from trading_signal_pipeline.domain.value_objects import Price, Volume
from trading_signal_pipeline.ports.market_data_provider import MarketDataProvider


class CsvMarketDataProvider(MarketDataProvider):
    """Load OHLCV candles from a local CSV file."""

    def __init__(self, path: str):
        self.path = Path(path)

    def load(self, symbol: str, start: str, end: str, interval: str) -> MarketSeries:
        """
        Load a MarketSeries from a CSV file.

        Notes:
            This adapter ignores (start/end/interval) because the file is assumed to
            already contain the desired range/granularity.
        """
        if not self.path.exists():
            raise ValueError(f"CSV file not found: {self.path}")

        series: MarketSeries = []
        with self.path.open("r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if not row:
                    continue
                t = datetime.fromisoformat(row["Date"])
                series.append(
                    Candle(
                        time=t,
                        open=Price(float(row["Open"])),
                        high=Price(float(row["High"])),
                        low=Price(float(row["Low"])),
                        close=Price(float(row["Close"])),
                        volume=Volume(float(row.get("Volume", 0.0) or 0.0)),
                    )
                )

        if not series:
            raise ValueError(f"CSV file contains no rows: {self.path}")
        return series

