from datetime import datetime, timezone

import pytest

from trading_signal_pipeline.adapters.market_data.binance_provider import BinanceMarketDataProvider
from trading_signal_pipeline.domain.market import Candle


class DummyResponse:
    def __init__(self, status_code, payload):
        self.status_code = status_code
        self._payload = payload
        self.text = str(payload)

    def json(self):
        return self._payload


class DummySession:
    def __init__(self, payload):
        self.payload = payload
        self.calls = 0

    def get(self, url, params=None, timeout=None):
        self.calls += 1
        return DummyResponse(200, self.payload if self.calls == 1 else [])


def test_binance_provider_loads_series():
    # One kline row
    payload = [
        [
            1704067200000,  # 2024-01-01T00:00:00Z
            "100.0",
            "110.0",
            "90.0",
            "105.0",
            "1234.0",
            1704153600000,
            "0",
            0,
            "0",
            "0",
            "0",
        ]
    ]
    provider = BinanceMarketDataProvider(session=DummySession(payload))
    series = provider.load("BTCUSDT", start="2024-01-01", end="2024-01-02", interval="1d")

    assert len(series) == 1
    assert isinstance(series[0], Candle)
    assert series[0].time == datetime(2024, 1, 1, tzinfo=timezone.utc)


def test_binance_provider_empty_raises():
    provider = BinanceMarketDataProvider(session=DummySession([]))
    with pytest.raises(ValueError):
        provider.load("BTCUSDT", start="2024-01-01", end="2024-01-02", interval="1d")

