from core.metrics.metrics import (
    TotalReturn,
    WinRate,
    MaxDrawdown,
    NumTrades,
)
from core.metrics.registry import MetricsEngine
from core.models.trade import Trade


# --- Sample Data ---
def sample_trades():
    return [
        Trade(symbol="AAPL", side="BUY", entry_price=100, exit_price=110, quantity=1.0, pnl=10),
        Trade(symbol="AAPL", side="BUY", entry_price=100, exit_price=95, quantity=1.0, pnl=-5),
        Trade(symbol="AAPL", side="BUY", entry_price=100, exit_price=120, quantity=1.0, pnl=20),
    ]


def sample_equity():
    return [100000, 110000, 105000, 120000, 90000]


# ----------------------------
# Individual Metric Tests
# ----------------------------

def test_total_return():
    metric = TotalReturn()
    equity = [100000, 110000]

    result = metric.compute([], equity, 100000)

    assert result == 0.1


def test_win_rate():
    metric = WinRate()
    trades = sample_trades()

    result = metric.compute(trades, [], 100000)

    assert result == 2 / 3


def test_win_rate_empty():
    metric = WinRate()

    result = metric.compute([], [], 100000)

    assert result == 0.0


def test_max_drawdown():
    metric = MaxDrawdown()
    equity = sample_equity()

    result = metric.compute([], equity, 100000)

    # peak = 120000 → drop to 90000 → -25%
    assert round(result, 2) == -0.25


def test_num_trades():
    metric = NumTrades()
    trades = sample_trades()

    result = metric.compute(trades, [], 100000)

    assert result == 3


# ----------------------------
# Metrics Engine Tests
# ----------------------------

def test_metrics_engine_combines_results():
    engine = MetricsEngine([
        TotalReturn(),
        WinRate(),
        MaxDrawdown(),
        NumTrades(),
    ])

    trades = sample_trades()
    equity = sample_equity()

    result = engine.compute_all(trades, equity, 100000)

    assert "total_return" in result
    assert "win_rate" in result
    assert "max_drawdown" in result
    assert "num_trades" in result


def test_metrics_engine_values_correct():
    engine = MetricsEngine([
        TotalReturn(),
        WinRate(),
    ])

    trades = sample_trades()
    equity = [100000, 110000]

    result = engine.compute_all(trades, equity, 100000)

    assert result["total_return"] == 0.1
    assert result["win_rate"] == 2 / 3


# ----------------------------
# Extensibility Test (Important)
# ----------------------------

class DummyMetric:
    def name(self):
        return "dummy"

    def compute(self, trades, equity_curve, initial_capital):
        return 42


def test_metrics_engine_extensible():
    engine = MetricsEngine([DummyMetric()])

    result = engine.compute_all([], [], 100000)

    assert result["dummy"] == 42