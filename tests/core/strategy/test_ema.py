from datetime import datetime, timedelta, timezone

from trading_signal_pipeline.domain.market import Candle
from trading_signal_pipeline.domain.signal import SignalType
from trading_signal_pipeline.domain.strategies.ema_crossover import EMACrossoverStrategy
from trading_signal_pipeline.domain.value_objects import Price, Volume


def make_series(prices):
    t0 = datetime(2024, 1, 1, tzinfo=timezone.utc)
    out = []
    for i, p in enumerate(prices):
        out.append(
            Candle(
                time=t0 + timedelta(days=i),
                open=Price(float(p)),
                high=Price(float(p)),
                low=Price(float(p)),
                close=Price(float(p)),
                volume=Volume(1.0),
            )
        )
    return out


def test_output_length_matches_input():
    series = make_series([100, 101, 102, 103])
    strategy = EMACrossoverStrategy()
    signals = strategy.generate(series)
    assert len(signals) == len(series)


def test_signal_values_are_valid():
    series = make_series([100, 102, 101, 103, 99])
    strategy = EMACrossoverStrategy()
    signals = strategy.generate(series)
    assert set(signals).issubset({SignalType.BUY, SignalType.SELL, SignalType.HOLD})


def test_empty_series():
    strategy = EMACrossoverStrategy()
    assert strategy.generate([]) == []


def test_crossover_generates_signal():
    series = make_series([100, 100, 100, 110, 120, 130])
    strategy = EMACrossoverStrategy(short_window=2, long_window=3)
    signals = strategy.generate(series)
    assert any(s != SignalType.HOLD for s in signals)
