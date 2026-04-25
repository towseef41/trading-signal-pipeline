"""
Built-in performance metrics.

All metrics are designed to be side-effect free and computed from:
  - trades: a list of completed trades
  - equity_curve: a list of equity values per tick
"""

from trading_signal_pipeline.ports.metric import Metric


class TotalReturn(Metric):
    """Total return relative to initial capital."""

    def name(self):
        """See base class."""
        return "total_return"

    def compute(self, trades, equity_curve, initial_capital):
        """See base class."""
        if not equity_curve:
            return 0.0
        return (equity_curve[-1] - initial_capital) / initial_capital


class WinRate(Metric):
    """Fraction of trades with positive PnL."""

    def name(self):
        """See base class."""
        return "win_rate"

    def compute(self, trades, equity_curve, initial_capital):
        """See base class."""
        if not trades:
            return 0.0
        wins = sum(1 for t in trades if t.pnl > 0)
        return wins / len(trades)


class MaxDrawdown(Metric):
    """Maximum drawdown over the equity curve (returned as a negative fraction)."""

    def name(self):
        """See base class."""
        return "max_drawdown"

    def compute(self, trades, equity_curve, initial_capital):
        """See base class."""
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
    """Number of completed trades."""

    def name(self):
        """See base class."""
        return "num_trades"

    def compute(self, trades, equity_curve, initial_capital):
        """See base class."""
        return len(trades)
