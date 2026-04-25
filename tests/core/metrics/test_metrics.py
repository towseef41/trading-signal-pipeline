from trading_signal_pipeline.application.metrics.metrics import TotalReturn, WinRate, MaxDrawdown, NumTrades
from trading_signal_pipeline.application.metrics.registry import MetricsEngine
from trading_signal_pipeline.domain.trade import Trade
from trading_signal_pipeline.domain.value_objects import Price, Quantity, Symbol


def sample_trades():
    return [
        Trade(symbol=Symbol("AAPL"), side="BUY", entry_price=Price(100), exit_price=Price(110), quantity=Quantity(1.0), pnl=10),
        Trade(symbol=Symbol("AAPL"), side="BUY", entry_price=Price(100), exit_price=Price(95), quantity=Quantity(1.0), pnl=-5),
        Trade(symbol=Symbol("AAPL"), side="BUY", entry_price=Price(100), exit_price=Price(120), quantity=Quantity(1.0), pnl=20),
    ]


def sample_equity():
    return [100000, 110000, 105000, 120000, 90000]


def test_total_return():
    metric = TotalReturn()
    equity = [100000, 110000]
    assert metric.compute([], equity, 100000) == 0.1


def test_win_rate():
    metric = WinRate()
    assert metric.compute(sample_trades(), [], 100000) == 2 / 3


def test_win_rate_empty():
    metric = WinRate()
    assert metric.compute([], [], 100000) == 0.0


def test_max_drawdown():
    metric = MaxDrawdown()
    result = metric.compute([], sample_equity(), 100000)
    assert round(result, 2) == -0.25


def test_num_trades():
    metric = NumTrades()
    assert metric.compute(sample_trades(), [], 100000) == 3


def test_metrics_engine_combines_results():
    engine = MetricsEngine([TotalReturn(), WinRate(), MaxDrawdown(), NumTrades()])
    result = engine.compute_all(sample_trades(), sample_equity(), 100000)
    assert set(result.keys()) == {"total_return", "win_rate", "max_drawdown", "num_trades"}


def test_metrics_engine_values_correct():
    engine = MetricsEngine([TotalReturn(), WinRate()])
    result = engine.compute_all(sample_trades(), [100000, 110000], 100000)
    assert result["total_return"] == 0.1
    assert result["win_rate"] == 2 / 3


class DummyMetric:
    def name(self):
        return "dummy"

    def compute(self, trades, equity_curve, initial_capital):
        return 42


def test_metrics_engine_extensible():
    engine = MetricsEngine([DummyMetric()])
    assert engine.compute_all([], [], 100000)["dummy"] == 42
