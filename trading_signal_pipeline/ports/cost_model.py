"""
Cost model port.

A cost model adjusts a raw fill price (e.g. for slippage) and returns explicit
transaction costs (e.g. fees/commission).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from trading_signal_pipeline.domain.types import Side
from trading_signal_pipeline.domain.value_objects import Price, Quantity


@dataclass(frozen=True)
class FillCost:
    """Cost result returned by a cost model for a single fill."""

    price: Price
    fee: float


class CostModel(ABC):
    """Port for applying slippage/fees to a raw fill."""

    @abstractmethod
    def apply(self, *, side: Side, price: Price, quantity: Quantity) -> FillCost:
        """
        Apply costs to a raw fill price.

        Args:
            side: "BUY" or "SELL".
            price: Raw fill price from the FillPriceModel.
            quantity: Fill quantity.

        Returns:
            FillCost containing adjusted price and explicit fee in quote currency.
        """
        raise NotImplementedError

