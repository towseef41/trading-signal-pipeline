"""
Backtesting domain service.

Backtester runs a strategy over a candle series using an execution policy and
returns a BacktestResult.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from trading_signal_pipeline.domain.backtest_result import BacktestResult
from trading_signal_pipeline.domain.backtesting.execution import ExecutionModel
from trading_signal_pipeline.domain.backtesting.portfolio import Portfolio
from trading_signal_pipeline.domain.backtesting.position import Position
from trading_signal_pipeline.domain.fill import Fill
from trading_signal_pipeline.domain.market import MarketSeries
from trading_signal_pipeline.domain.strategy import Strategy


@dataclass(frozen=True)
class Backtester:
    """Domain service for running a backtest."""

    execution: ExecutionModel
    initial_capital: float = 100000.0

    def run(self, symbol: str, series: MarketSeries, strategy: Strategy) -> BacktestResult:
        """
        Run a backtest for a single symbol and strategy.

        Args:
            symbol: Symbol identifier for the run.
            series: Candle series.
            strategy: Strategy producing one signal per candle.

        Returns:
            BacktestResult containing trades and an equity curve.

        Raises:
            ValueError: If the strategy does not return one signal per candle.
        """
        signals = strategy.generate(series)
        if len(signals) != len(series):
            raise ValueError("Strategy must return one signal per candle")

        from trading_signal_pipeline.domain.value_objects import Symbol  # local import to avoid cycles

        position = Position(symbol=Symbol(symbol))
        portfolio = Portfolio(self.initial_capital)

        trades = []
        fills: List[Fill] = []
        equity_curve: List[float] = []

        for i, (candle, signal) in enumerate(zip(series, signals)):
            next_candle = series[i + 1] if i + 1 < len(series) else None
            self.execution.on_candle(candle, next_candle, signal, position, portfolio, trades, fills)

            unrealized = 0.0
            if position.is_open and position.entry_price is not None:
                assert position.quantity is not None
                unrealized = (float(candle.close) - float(position.entry_price)) * float(position.quantity)

            equity_curve.append(portfolio.equity(unrealized))

        return BacktestResult(trades=trades, equity_curve=equity_curve, fills=fills)
