"""
Cost model implementations (domain policies).
"""

from __future__ import annotations

from dataclasses import dataclass

from trading_signal_pipeline.domain.types import Side
from trading_signal_pipeline.domain.value_objects import Price, Quantity
from trading_signal_pipeline.ports.cost_model import CostModel, FillCost


@dataclass(frozen=True)
class NoCosts(CostModel):
    """No slippage and no fees."""

    def apply(self, *, side: Side, price: Price, quantity: Quantity) -> FillCost:
        return FillCost(price=price, fee=0.0)


@dataclass(frozen=True)
class BpsSlippageAndFees(CostModel):
    """
    Apply slippage and fee in basis points.

    - slippage_bps: adjusts price against the trader (BUY higher, SELL lower)
    - fee_bps: a fee applied on notional for each fill
    """

    slippage_bps: float = 0.0
    fee_bps: float = 0.0

    def apply(self, *, side: Side, price: Price, quantity: Quantity) -> FillCost:
        raw = float(price)
        slip = float(self.slippage_bps) / 10000.0

        if side == "BUY":
            adj = raw * (1.0 + slip)
        else:
            adj = raw * (1.0 - slip)

        notional = adj * float(quantity)
        fee = notional * (float(self.fee_bps) / 10000.0)
        return FillCost(price=Price(adj), fee=float(fee))

