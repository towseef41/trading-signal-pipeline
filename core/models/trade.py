from dataclasses import dataclass


@dataclass
class Trade:
    """
    Represents a single executed trade.
    """

    symbol: str
    side: str
    entry_price: float
    exit_price: float
    quantity: float
    pnl: float