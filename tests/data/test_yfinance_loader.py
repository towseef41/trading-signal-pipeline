from datetime import datetime, timezone

import pandas as pd
import pytest

from trading_signal_pipeline.adapters.market_data.yfinance_provider import YFinanceMarketDataProvider
from trading_signal_pipeline.domain.market import Candle


class MockYF:
    @staticmethod
    def download(*args, **kwargs):
        idx = pd.to_datetime(
            [datetime(2024, 1, 1, tzinfo=timezone.utc), datetime(2024, 1, 2, tzinfo=timezone.utc)]
        )
        return pd.DataFrame(
            {
                "Open": [100, 101],
                "High": [102, 103],
                "Low": [99, 100],
                "Close": [101, 102],
                "Volume": [1000, 1100],
            },
            index=idx,
        )


class EmptyYF:
    @staticmethod
    def download(*args, **kwargs):
        return pd.DataFrame()


def test_load_returns_series(monkeypatch):
    import trading_signal_pipeline.adapters.market_data.yfinance_provider as provider_module

    monkeypatch.setattr(provider_module, "yf", MockYF)

    provider = YFinanceMarketDataProvider()
    series = provider.load("AAPL", start="2024-01-01", end="2024-01-10", interval="1d")

    assert isinstance(series, list)
    assert series
    assert isinstance(series[0], Candle)


def test_empty_data_raises(monkeypatch):
    import trading_signal_pipeline.adapters.market_data.yfinance_provider as provider_module

    monkeypatch.setattr(provider_module, "yf", EmptyYF)

    provider = YFinanceMarketDataProvider()
    with pytest.raises(ValueError):
        provider.load("AAPL", start="2024-01-01", end="2024-01-10", interval="1d")
