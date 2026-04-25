from datetime import datetime, timedelta, timezone

import pytest

from trading_signal_pipeline.domain.backtesting.backtester import Backtester
from trading_signal_pipeline.domain.backtesting.execution import LongOnlyExecution
from trading_signal_pipeline.domain.market import Candle
from trading_signal_pipeline.domain.strategies.ema_crossover import EMACrossoverStrategy
from trading_signal_pipeline.domain.signal import SignalType
from trading_signal_pipeline.domain.value_objects import Price, Volume


def make_series(prices):
    t0 = datetime(2024, 1, 1, tzinfo=timezone.utc)
    return [
        Candle(
            time=t0 + timedelta(days=i),
            open=Price(float(p)),
            high=Price(float(p)),
            low=Price(float(p)),
            close=Price(float(p)),
            volume=Volume(1.0),
        )
        for i, p in enumerate(prices)
    ]


def test_backtest_runs():
    series = make_series([100, 102, 101, 103])
    backtester = Backtester(execution=LongOnlyExecution(quantity=1.0), initial_capital=100000)
    strategy = EMACrossoverStrategy()

    result = backtester.run(symbol="AAPL", series=series, strategy=strategy)

    assert result is not None
    assert isinstance(result.trades, list)
    assert isinstance(result.equity_curve, list)
    assert isinstance(result.fills, list)


def test_equity_curve_length():
    series = make_series([100, 101, 102])
    backtester = Backtester(execution=LongOnlyExecution(), initial_capital=100000)
    result = backtester.run("AAPL", series, EMACrossoverStrategy())
    assert len(result.equity_curve) == len(series)


def test_no_trades_on_flat_data():
    series = make_series([100, 100, 100, 100])
    backtester = Backtester(execution=LongOnlyExecution(), initial_capital=100000)
    result = backtester.run("AAPL", series, EMACrossoverStrategy())
    assert len(result.trades) == 0


def test_trade_generation():
    series = make_series([100, 100, 100, 110, 120, 130, 90])
    backtester = Backtester(execution=LongOnlyExecution(), initial_capital=100000)
    strategy = EMACrossoverStrategy(short_window=2, long_window=3)
    result = backtester.run("AAPL", series, strategy)
    assert len(result.trades) >= 1
    # Every completed trade should have both a BUY fill (entry) and SELL fill (exit).
    assert len(result.fills) >= 2 * len(result.trades)
    for trade in result.trades:
        assert trade.entry_time is not None
        assert trade.exit_time is not None
        assert any(
            f.side == "BUY"
            and f.symbol == trade.symbol
            and f.time == trade.entry_time
            and float(f.quantity) == float(trade.quantity)
            for f in result.fills
        )
        assert any(
            f.side == "SELL"
            and f.symbol == trade.symbol
            and f.time == trade.exit_time
            and float(f.quantity) == float(trade.quantity)
            for f in result.fills
        )


def test_pnl_calculation():
    series = make_series([100, 110, 90, 120])
    backtester = Backtester(execution=LongOnlyExecution(), initial_capital=100000)
    strategy = EMACrossoverStrategy(short_window=1, long_window=2)
    result = backtester.run("AAPL", series, strategy)

    if result.trades:
        trade = result.trades[0]
        assert trade.pnl == (float(trade.exit_price) - float(trade.entry_price)) * float(trade.quantity)


def test_invalid_strategy_length_raises():
    class BadStrategy:
        def generate(self, series):
            return [SignalType.HOLD]  # wrong length

    series = make_series([100, 101, 102])
    backtester = Backtester(execution=LongOnlyExecution(), initial_capital=100000)

    with pytest.raises(ValueError):
        backtester.run("AAPL", series, BadStrategy())
