from pydantic import BaseModel, Field
from typing import Literal


class TradeSignal(BaseModel):
    """
    Incoming webhook signal schema.
    """

    symbol: str = Field(..., json_schema_extra={"example": "AAPL"})
    side: Literal["BUY", "SELL"]
    qty: float = Field(..., gt=0)
    price: float = Field(..., gt=0)