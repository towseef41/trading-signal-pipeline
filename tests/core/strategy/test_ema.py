import pandas as pd
import pytest

from core.strategy.ema import EMACrossoverStrategy


def create_test_data(prices):
    """Helper to create OHLCV-like DataFrame"""
    return pd.DataFrame({
        "Close": prices
    })


def test_generate_signals_basic_structure():
    """
    Strategy should return DataFrame with required columns.
    """
    data = create_test_data([100, 101, 102, 103, 104])

    strategy = EMACrossoverStrategy()
    result = strategy.generate_signals(data)

    assert "signal" in result.columns
    assert "ema_short" in result.columns
    assert "ema_long" in result.columns


def test_generate_signals_no_exception_on_valid_data():
    """
    Strategy should run without errors on valid input.
    """
    data = create_test_data([100, 101, 99, 102, 98, 105])

    strategy = EMACrossoverStrategy()
    result = strategy.generate_signals(data)

    assert len(result) == len(data)


def test_missing_close_column_raises_error():
    """
    Strategy should fail if required column is missing.
    """
    data = pd.DataFrame({"Open": [1, 2, 3]})

    strategy = EMACrossoverStrategy()

    with pytest.raises(ValueError):
        strategy.generate_signals(data)


def test_signal_values_are_valid():
    """
    Signals should only be -1, 0, or 1.
    """
    data = create_test_data([100, 102, 101, 103, 99, 105])

    strategy = EMACrossoverStrategy()
    result = strategy.generate_signals(data)

    assert set(result["signal"].unique()).issubset({-1, 0, 1})


def test_crossover_generates_signal():
    """
    Strategy should generate at least one signal when crossover occurs.
    """
    # Artificial data to force crossover
    prices = [100, 100, 100, 110, 120, 130]
    data = create_test_data(prices)

    strategy = EMACrossoverStrategy(short_window=2, long_window=3)
    result = strategy.generate_signals(data)

    assert (result["signal"] != 0).any()


def test_no_crossover_means_no_signal():
    """
    Flat price should result in no signals.
    """
    prices = [100, 100, 100, 100, 100]
    data = create_test_data(prices)

    strategy = EMACrossoverStrategy()
    result = strategy.generate_signals(data)

    assert (result["signal"] == 0).all()