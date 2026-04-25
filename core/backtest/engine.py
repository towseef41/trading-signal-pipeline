import pandas as pd
from typing import List, Dict

from core.models.signal import SignalType
from core.backtest.execution import ExecutionModel
from core.backtest.position import Position
from core.backtest.portfolio import Portfolio


class BacktestResult:
    def __init__(self, trades: List[Dict], equity_curve: List[float]):
        self.trades = trades
        self.equity_curve = equity_curve


class BacktestEngine:
    """
    Orchestrates backtesting using pluggable execution model.
    """

    def __init__(self, execution_model: ExecutionModel, initial_capital=100000):
        self.execution_model = execution_model
        self.initial_capital = initial_capital

    def run(self, data: pd.DataFrame, strategy) -> BacktestResult:
        df = strategy.generate_signals(data)

        # Validate contract
        valid_signals = {s.value for s in SignalType}
        if not set(df["signal"].unique()).issubset(valid_signals):
            raise ValueError("Invalid signal values")

        position = Position()
        portfolio = Portfolio(self.initial_capital)

        trades: List[Dict] = []
        equity_curve: List[float] = []

        for time, row in df.iterrows():
            price = row["Close"]
            signal = row["signal"]

            # Execution logic
            self.execution_model.on_tick(
                time, price, signal, position, portfolio, trades
            )

            # Equity tracking
            unrealized = 0.0
            if position.is_open:
                unrealized = price - position.entry_price

            equity_curve.append(portfolio.current_value(unrealized))

        return BacktestResult(trades, equity_curve)