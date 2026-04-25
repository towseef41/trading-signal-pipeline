# core/metrics/metrics.py

from core.metrics.base import Metric


class TotalReturn(Metric):
    def name(self):
        return "total_return"

    def compute(self, trades, equity_curve, initial_capital):
        if not equity_curve:
            return 0.0
        return (equity_curve[-1] - initial_capital) / initial_capital


class WinRate(Metric):
    def name(self):
        return "win_rate"

    def compute(self, trades, equity_curve, initial_capital):
        if not trades:
            return 0.0
        wins = sum(1 for t in trades if t["pnl"] > 0)
        return wins / len(trades)


class MaxDrawdown(Metric):
    def name(self):
        return "max_drawdown"

    def compute(self, trades, equity_curve, initial_capital):
        if not equity_curve:
            return 0.0

        peak = equity_curve[0]
        max_dd = 0.0

        for value in equity_curve:
            if value > peak:
                peak = value
            dd = (value - peak) / peak
            if dd < max_dd:
                max_dd = dd

        return max_dd


class NumTrades(Metric):
    def name(self):
        return "num_trades"

    def compute(self, trades, equity_curve, initial_capital):
        return len(trades)