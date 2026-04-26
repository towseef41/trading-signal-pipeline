from datetime import datetime, timedelta, timezone

from trading_signal_pipeline.domain.backtesting.backtester import Backtester
from trading_signal_pipeline.domain.backtesting.cost_models import BpsSlippageAndFees, NoCosts
from trading_signal_pipeline.domain.backtesting.execution import LongOnlyExecution
from trading_signal_pipeline.domain.backtesting.fill_models import NextBarOpenFillModel, SameBarCloseFillModel
from trading_signal_pipeline.domain.market import Candle
from trading_signal_pipeline.domain.signal import SignalType
from trading_signal_pipeline.domain.strategy import Strategy
from trading_signal_pipeline.domain.value_objects import Price, Volume


class FixedSignals(Strategy):
    """Test helper strategy that returns a fixed signal sequence."""

    def __init__(self, signals):
        self._signals = signals

    def generate(self, series):
        return list(self._signals)


def make_series(ohlc):
    t0 = datetime(2024, 1, 1, tzinfo=timezone.utc)
    out = []
    for i, (o, c) in enumerate(ohlc):
        out.append(
            Candle(
                time=t0 + timedelta(days=i),
                open=Price(float(o)),
                high=Price(max(float(o), float(c))),
                low=Price(min(float(o), float(c))),
                close=Price(float(c)),
                volume=Volume(1.0),
            )
        )
    return out


def test_next_open_fill_model_uses_next_bar_open_for_entry_and_exit():
    series = make_series([(100, 101), (110, 111), (120, 121)])
    # BUY signal on bar 0, SELL signal on bar 1 -> fills happen on bar 1 open and bar 2 open.
    strategy = FixedSignals([SignalType.BUY, SignalType.SELL, SignalType.HOLD])

    exec_model = LongOnlyExecution(
        quantity=1.0,
        fill_model=NextBarOpenFillModel(),
        cost_model=NoCosts(),
    )
    backtester = Backtester(execution=exec_model, initial_capital=100000)
    result = backtester.run(symbol="AAPL", series=series, strategy=strategy)

    assert len(result.trades) == 1
    trade = result.trades[0]
    assert float(trade.entry_price) == float(series[1].open)
    assert float(trade.exit_price) == float(series[2].open)
    assert trade.entry_time == series[1].time
    assert trade.exit_time == series[2].time


def test_slippage_and_fees_reduce_pnl_vs_no_costs():
    series = make_series([(100, 100), (110, 110), (120, 120)])
    strategy = FixedSignals([SignalType.BUY, SignalType.SELL, SignalType.HOLD])

    base_exec = LongOnlyExecution(quantity=1.0, fill_model=SameBarCloseFillModel(), cost_model=NoCosts())
    cost_exec = LongOnlyExecution(
        quantity=1.0,
        fill_model=SameBarCloseFillModel(),
        cost_model=BpsSlippageAndFees(slippage_bps=10, fee_bps=10),
    )

    base = Backtester(execution=base_exec, initial_capital=100000).run("AAPL", series, strategy)
    cost = Backtester(execution=cost_exec, initial_capital=100000).run("AAPL", series, strategy)

    assert len(base.trades) == 1
    assert len(cost.trades) == 1
    assert cost.trades[0].pnl < base.trades[0].pnl

