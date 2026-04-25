import pandas as pd
import pytest

from core.strategy.ema import EMACrossoverStrategy
from core.models.signal import SignalType


def create_data(prices):
    return pd.DataFrame({"Close": prices})


def test_output_structure():
    data = create_data([100, 101, 102, 103])

    strategy = EMACrossoverStrategy()
    result = strategy.generate_signals(data)

    assert "signal" in result.columns
    assert "ema_short" in result.columns
    assert "ema_long" in result.columns


def test_signal_values_are_valid():
    data = create_data([100, 102, 101, 103, 99])

    strategy = EMACrossoverStrategy()
    result = strategy.generate_signals(data)

    valid_values = set(SignalType)
    assert set(result["signal"].unique()).issubset(valid_values)


def test_missing_close_column():
    data = pd.DataFrame({"Open": [1, 2, 3]})
    strategy = EMACrossoverStrategy()

    with pytest.raises(ValueError):
        strategy.generate_signals(data)


def test_crossover_generates_signal():
    prices = [100, 100, 100, 110, 120, 130]
    data = create_data(prices)

    strategy = EMACrossoverStrategy(short_window=2, long_window=3)
    result = strategy.generate_signals(data)

    assert (result["signal"] != SignalType.HOLD).any()


def test_flat_data_produces_no_signal():
    prices = [100, 100, 100, 100]
    data = create_data(prices)

    strategy = EMACrossoverStrategy()
    result = strategy.generate_signals(data)

    assert (result["signal"] == SignalType.HOLD).all()


def test_signal_column_type():
    data = create_data([100, 101, 102, 103])

    strategy = EMACrossoverStrategy()
    result = strategy.generate_signals(data)

    valid_values = {s.value for s in SignalType}
    assert set(result["signal"].unique()).issubset(valid_values)