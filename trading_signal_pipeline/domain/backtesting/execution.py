"""
Backtesting execution policies.

ExecutionModel is a domain policy that translates signals into trades and
position changes.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List

from trading_signal_pipeline.domain.fill import Fill
from trading_signal_pipeline.domain.signal import SignalType
from trading_signal_pipeline.domain.trade import Trade
from trading_signal_pipeline.domain.backtesting.position import Position
from trading_signal_pipeline.domain.backtesting.portfolio import Portfolio
from trading_signal_pipeline.domain.market import Candle
from trading_signal_pipeline.domain.value_objects import Quantity
from trading_signal_pipeline.domain.backtesting.cost_models import NoCosts
from trading_signal_pipeline.domain.backtesting.fill_models import SameBarCloseFillModel
from trading_signal_pipeline.ports.cost_model import CostModel
from trading_signal_pipeline.ports.fill_price_model import FillPriceModel


class ExecutionModel(ABC):
    """
    Domain policy translating signals into position changes/trades.
    """

    @abstractmethod
    def on_candle(
        self,
        candle: Candle,
        next_candle: Candle | None,
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
            next_candle: Next candle (if available). Used by execution models that fill on the next bar.
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
    fill_model: FillPriceModel = field(default_factory=SameBarCloseFillModel)
    cost_model: CostModel = field(default_factory=NoCosts)

    def on_candle(self, candle, next_candle, signal, position, portfolio, trades, fills) -> None:
        """
        Long-only execution:
        - BUY opens a position if flat
        - SELL closes the position if open
        """
        # Open
        if signal == SignalType.BUY and not position.is_open:
            decision = self.fill_model.decide(side="BUY", candle=candle, next_candle=next_candle)
            if decision is None:
                return
            cost = self.cost_model.apply(side="BUY", price=decision.price, quantity=self.quantity)

            position.quantity = self.quantity
            position.entry_price = cost.price
            position.entry_time = decision.time
            position.entry_fee = cost.fee
            # Fees are paid at execution time.
            portfolio.apply_pnl(-cost.fee)
            fills.append(
                Fill(
                    symbol=position.symbol,
                    side="BUY",
                    price=cost.price,
                    quantity=self.quantity,
                    time=decision.time,
                )
            )
            return

        # Close
        if signal == SignalType.SELL and position.is_open and position.entry_price is not None:
            decision = self.fill_model.decide(side="SELL", candle=candle, next_candle=next_candle)
            if decision is None:
                return
            assert position.quantity is not None
            cost = self.cost_model.apply(side="SELL", price=decision.price, quantity=position.quantity)

            assert position.quantity is not None
            gross_pnl = (float(cost.price) - float(position.entry_price)) * float(position.quantity)
            # Pay exit fee now; entry fee was already paid at entry.
            portfolio.apply_pnl(gross_pnl - cost.fee)
            pnl = gross_pnl - float(position.entry_fee) - cost.fee

            trades.append(
                Trade(
                    symbol=position.symbol,
                    side="SELL",
                    entry_price=position.entry_price,
                    exit_price=cost.price,
                    quantity=position.quantity,
                    pnl=pnl,
                    entry_time=position.entry_time,
                    exit_time=decision.time,
                )
            )
            fills.append(
                Fill(
                    symbol=position.symbol,
                    side="SELL",
                    price=cost.price,
                    quantity=position.quantity,
                    time=decision.time,
                )
            )

            position.quantity = None
            position.entry_price = None
            position.entry_time = None
            position.entry_fee = 0.0
