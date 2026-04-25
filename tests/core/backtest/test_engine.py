import pandas as pd

from core.backtest.engine import BacktestEngine
from core.backtest.execution import SimpleLongOnlyExecution
from core.strategy.ema import EMACrossoverStrategy


def create_data(prices):
    return pd.DataFrame({"Close": prices})


def test_backtest_runs():
    data = create_data([100, 102, 101, 103])

    engine = BacktestEngine(execution_model=SimpleLongOnlyExecution())
    strategy = EMACrossoverStrategy()

    result = engine.run(data, strategy)

    assert result is not None
    assert isinstance(result.trades, list)
    assert isinstance(result.equity_curve, list)


def test_equity_curve_length():
    data = create_data([100, 101, 102])

    engine = BacktestEngine(execution_model=SimpleLongOnlyExecution())
    strategy = EMACrossoverStrategy()

    result = engine.run(data, strategy)

    assert len(result.equity_curve) == len(data)


def test_no_trades_on_flat_data():
    data = create_data([100, 100, 100, 100])

    engine = BacktestEngine(execution_model=SimpleLongOnlyExecution())
    strategy = EMACrossoverStrategy()

    result = engine.run(data, strategy)

    assert len(result.trades) == 0


def test_trade_generation():
    data = create_data([100, 100, 100, 110, 120, 130, 90])

    engine = BacktestEngine(execution_model=SimpleLongOnlyExecution())
    strategy = EMACrossoverStrategy(short_window=2, long_window=3)

    result = engine.run(data, strategy)

    assert len(result.trades) >= 1


def test_pnl_calculation():
    data = create_data([100, 110, 90, 120])

    engine = BacktestEngine(execution_model=SimpleLongOnlyExecution())
    strategy = EMACrossoverStrategy(short_window=1, long_window=2)

    result = engine.run(data, strategy)

    if result.trades:
        trade = result.trades[0]
        assert trade.pnl == trade.exit_price - trade.entry_price


def test_invalid_signal_raises():
    data = pd.DataFrame({
        "Close": [100, 101, 102],
        "signal": [99, 99, 99],
    })

    class BadStrategy:
        def generate_signals(self, data):
            return data

    engine = BacktestEngine(execution_model=SimpleLongOnlyExecution())

    try:
        engine.run(data, BadStrategy())
        assert False, "Expected ValueError"
    except ValueError:
        assert True