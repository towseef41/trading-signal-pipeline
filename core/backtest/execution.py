from abc import ABC, abstractmethod
from typing import List, Dict

from core.models.signal import SignalType
from core.backtest.position import Position
from core.backtest.portfolio import Portfolio


class ExecutionModel(ABC):
    """
    Defines how signals are translated into trades.
    """

    @abstractmethod
    def on_tick(
        self,
        time,
        price: float,
        signal: int,
        position: Position,
        portfolio: Portfolio,
        trades: List[Dict],
    ):
        pass

class SimpleLongOnlyExecution(ExecutionModel):
    """
    Basic execution model:
    - Long-only
    - Single position
    """

    def on_tick(self, time, price, signal, position, portfolio, trades):

        # BUY
        if signal == SignalType.BUY.value and not position.is_open:
            position.is_open = True
            position.entry_price = price
            position.entry_time = time

        # SELL
        elif signal == SignalType.SELL.value and position.is_open:
            pnl = price - position.entry_price
            portfolio.update(pnl)

            trades.append({
                "entry_time": position.entry_time,
                "exit_time": time,
                "entry_price": position.entry_price,
                "exit_price": price,
                "pnl": pnl
            })

            position.is_open = False
            position.entry_price = None
            position.entry_time = None