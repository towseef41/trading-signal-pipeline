"""
API request/response schemas (Pydantic).
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Generic, Literal, Optional, TypeVar

from pydantic import BaseModel, Field


class TradeSignal(BaseModel):
    """
    Incoming webhook signal schema.
    """

    symbol: str = Field(..., json_schema_extra={"example": "AAPL"})
    side: Literal["BUY", "SELL"]
    qty: float = Field(..., gt=0)
    price: float = Field(..., gt=0)


class ApiError(BaseModel):
    """Standard API error payload."""

    code: str
    message: str
    details: Optional[Any] = None


class ErrorResponse(BaseModel):
    """Standard API error envelope."""

    error: ApiError


T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    """Standard API success envelope."""

    data: T


class ExecutionResultOut(BaseModel):
    """Execution result returned from the broker adapter."""

    status: str
    symbol: str
    side: Literal["BUY", "SELL"]
    qty: float
    price: float


class SignalEventOut(BaseModel):
    """Signal event returned from ingestion."""

    symbol: str
    side: Literal["BUY", "SELL"]
    qty: float
    price: float
    received_at: datetime
    idempotency_key: str


class IngestSignalOut(BaseModel):
    """Response payload for signal ingestion."""

    signal: SignalEventOut
    execution: ExecutionResultOut


class TradeOut(BaseModel):
    """Serialized trade used in report responses."""

    symbol: str
    side: Literal["BUY", "SELL"]
    entry_price: float
    exit_price: float
    quantity: float
    pnl: float
    entry_time: Optional[datetime] = None
    exit_time: Optional[datetime] = None


class PerformanceOut(BaseModel):
    """Performance metrics section in the report."""

    total_return: float
    win_rate: float
    max_drawdown: float
    num_trades: int


class TradesSummaryOut(BaseModel):
    """Trades summary section in the report."""

    total_trades: int
    last_trade: Optional[TradeOut] = None


class SignalsSummaryOut(BaseModel):
    """Signals summary section in the report."""

    total_signals: int
    last_signal: Optional[SignalEventOut] = None


class ReportOut(BaseModel):
    """Top-level report response."""

    performance: PerformanceOut
    trades_summary: TradesSummaryOut
    signals_summary: SignalsSummaryOut
