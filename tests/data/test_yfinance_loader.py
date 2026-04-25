import pandas as pd
import pytest

from data.yfinance_loader import YFinanceDataLoader


# ----------------------------
# Mock yfinance
# ----------------------------

class MockYF:
    @staticmethod
    def download(*args, **kwargs):
        return pd.DataFrame({
            "Open": [100, 101],
            "High": [102, 103],
            "Low": [99, 100],
            "Close": [101, 102],
            "Volume": [1000, 1100],
        })


class EmptyYF:
    @staticmethod
    def download(*args, **kwargs):
        return pd.DataFrame()


# ----------------------------
# Tests
# ----------------------------

def test_load_returns_dataframe(monkeypatch):
    import data.yfinance_loader as loader_module

    monkeypatch.setattr(loader_module, "yf", MockYF)

    loader = YFinanceDataLoader()
    df = loader.load("AAPL")

    assert isinstance(df, pd.DataFrame)
    assert not df.empty


def test_required_columns_exist(monkeypatch):
    import data.yfinance_loader as loader_module

    monkeypatch.setattr(loader_module, "yf", MockYF)

    loader = YFinanceDataLoader()
    df = loader.load("AAPL")

    required_columns = {"Open", "High", "Low", "Close", "Volume"}

    assert required_columns.issubset(df.columns)


def test_empty_data_raises(monkeypatch):
    import data.yfinance_loader as loader_module

    monkeypatch.setattr(loader_module, "yf", EmptyYF)

    loader = YFinanceDataLoader()

    with pytest.raises(ValueError):
        loader.load("AAPL")