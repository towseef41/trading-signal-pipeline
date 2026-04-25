"""
Portfolio domain model for backtesting.

This portfolio is intentionally minimal: it tracks realized cash and exposes
equity = cash + unrealized PnL.
"""

from __future__ import annotations


class Portfolio:
    """
    Minimal portfolio: tracks realized cash and computes equity given unrealized PnL.
    """

    def __init__(self, initial_capital: float):
        """
        Args:
            initial_capital: Starting cash for the backtest.
        """
        self.initial_capital = float(initial_capital)
        self.cash = float(initial_capital)

    def apply_pnl(self, pnl: float) -> None:
        """Apply realized PnL to cash."""
        self.cash += float(pnl)

    def equity(self, unrealized_pnl: float = 0.0) -> float:
        """Return current equity given unrealized PnL."""
        return self.cash + float(unrealized_pnl)
