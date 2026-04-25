from datetime import datetime, timezone

from trading_signal_pipeline.domain.backtest_result import BacktestResult
from trading_signal_pipeline.domain.fill import Fill
from trading_signal_pipeline.domain.trade import Trade
from trading_signal_pipeline.domain.value_objects import Price, Quantity, Symbol
from trading_signal_pipeline.serialization.primitives import backtest_result_from_dict, backtest_result_to_dict


def test_backtest_result_roundtrip_includes_fills():
    t0 = datetime(2024, 1, 1, tzinfo=timezone.utc)
    t1 = datetime(2024, 1, 2, tzinfo=timezone.utc)
    sym = Symbol("AAPL")

    trade = Trade(
        symbol=sym,
        side="SELL",
        entry_price=Price(100.0),
        exit_price=Price(110.0),
        quantity=Quantity(1.0),
        pnl=10.0,
        entry_time=t0,
        exit_time=t1,
    )
    fills = [
        Fill(symbol=sym, side="BUY", price=Price(100.0), quantity=Quantity(1.0), time=t0),
        Fill(symbol=sym, side="SELL", price=Price(110.0), quantity=Quantity(1.0), time=t1),
    ]
    result = BacktestResult(trades=[trade], equity_curve=[100000.0, 100010.0], fills=fills)

    d = backtest_result_to_dict(result)
    loaded = backtest_result_from_dict(d)

    assert loaded == result

