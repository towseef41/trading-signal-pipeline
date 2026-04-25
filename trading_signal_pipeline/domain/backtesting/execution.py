"""
Backtesting execution policies.

ExecutionModel is a domain policy that translates signals into trades and
position changes.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List

from trading_signal_pipeline.domain.fill import Fill
from trading_signal_pipeline.domain.signal import SignalType
from trading_signal_pipeline.domain.trade import Trade
from trading_signal_pipeline.domain.backtesting.position import Position
from trading_signal_pipeline.domain.backtesting.portfolio import Portfolio
from trading_signal_pipeline.domain.market import Candle
from trading_signal_pipeline.domain.value_objects import Quantity, Symbol


class ExecutionModel(ABC):
    """
    Domain policy translating signals into position changes/trades.
    """

    @abstractmethod
    def on_candle(
        self,
        candle: Candle,
        signal: SignalType,
        position: Position,
        portfolio: Portfolio,
        trades: List[Trade],
        fills: List[Fill],
    ) -> None:
        """
        Apply execution logic for a single candle.

        Args:
            candle: Current candle.
            signal: Signal for this candle.
            position: Mutable position state.
            portfolio: Portfolio state.
            trades: Output list to append completed trades to.
            fills: Output list to append fills (BUY/SELL legs) to.
        """
        raise NotImplementedError


@dataclass(frozen=True)
class LongOnlyExecution(ExecutionModel):
    """
    Long-only execution:
    - Buy opens a position of fixed quantity if flat
    - Sell closes the full position if open
    """

    quantity: Quantity = Quantity(1.0)

    def on_candle(self, candle, signal, position, portfolio, trades, fills) -> None:
        """
        Long-only execution:
        - BUY opens a position if flat
        - SELL closes the position if open
        """
        # Open
        if signal == SignalType.BUY and not position.is_open:
            position.quantity = self.quantity
            position.entry_price = candle.close
            position.entry_time = candle.time
            fills.append(
                Fill(
                    symbol=position.symbol,
                    side="BUY",
                    price=candle.close,
                    quantity=self.quantity,
                    time=candle.time,
                )
            )
            return

        # Close
        if signal == SignalType.SELL and position.is_open and position.entry_price is not None:
            assert position.quantity is not None
            pnl = (float(candle.close) - float(position.entry_price)) * float(position.quantity)
            portfolio.apply_pnl(pnl)

            trades.append(
                Trade(
                    symbol=position.symbol,
                    side="SELL",
                    entry_price=position.entry_price,
                    exit_price=candle.close,
                    quantity=position.quantity,
                    pnl=pnl,
                    entry_time=position.entry_time,
                    exit_time=candle.time,
                )
            )
            fills.append(
                Fill(
                    symbol=position.symbol,
                    side="SELL",
                    price=candle.close,
                    quantity=position.quantity,
                    time=candle.time,
                )
            )

            position.quantity = None
            position.entry_price = None
            position.entry_time = None
