"""
Primitive mappers for domain objects.

These functions convert domain objects to/from JSON-serializable primitives.
This keeps serialization concerns out of the domain model.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional

from trading_signal_pipeline.domain.backtest_result import BacktestResult
from trading_signal_pipeline.domain.execution import ExecutionResult
from trading_signal_pipeline.domain.fill import Fill
from trading_signal_pipeline.domain.signal import SignalEvent
from trading_signal_pipeline.domain.trade import Trade
from trading_signal_pipeline.domain.value_objects import Price, Quantity, Symbol, Volume


def _dt_to_str(dt: datetime) -> str:
    """Convert a datetime to ISO-8601 string."""
    return dt.isoformat()


def _dt_from_str(s: str) -> datetime:
    """Parse an ISO-8601 datetime string."""
    return datetime.fromisoformat(s)


def signal_event_to_dict(e: SignalEvent) -> Dict[str, Any]:
    """Convert SignalEvent to primitive dict."""
    return {
        "symbol": str(e.symbol),
        "side": e.side,
        "qty": float(e.qty),
        "price": float(e.price),
        "received_at": _dt_to_str(e.received_at),
        "idempotency_key": e.idempotency_key,
    }


def signal_event_from_dict(d: Dict[str, Any]) -> SignalEvent:
    """Convert primitive dict to SignalEvent."""
    return SignalEvent(
        symbol=Symbol(d["symbol"]),
        side=d["side"],
        qty=Quantity(float(d["qty"])),
        price=Price(float(d["price"])),
        received_at=_dt_from_str(d["received_at"]),
        idempotency_key=d["idempotency_key"],
    )


def execution_result_to_dict(r: ExecutionResult) -> Dict[str, Any]:
    """Convert ExecutionResult to primitive dict."""
    return {
        "status": r.status,
        "symbol": str(r.symbol),
        "side": r.side,
        "qty": float(r.qty),
        "price": float(r.price),
    }


def trade_to_dict(t: Trade) -> Dict[str, Any]:
    """Convert Trade to primitive dict."""
    return {
        "symbol": str(t.symbol),
        "side": t.side,
        "entry_price": float(t.entry_price),
        "exit_price": float(t.exit_price),
        "quantity": float(t.quantity),
        "pnl": float(t.pnl),
        "entry_time": _dt_to_str(t.entry_time) if t.entry_time else None,
        "exit_time": _dt_to_str(t.exit_time) if t.exit_time else None,
    }


def trade_from_dict(d: Dict[str, Any]) -> Trade:
    """Convert primitive dict to Trade."""
    return Trade(
        symbol=Symbol(d["symbol"]),
        side=d["side"],
        entry_price=Price(float(d["entry_price"])),
        exit_price=Price(float(d["exit_price"])),
        quantity=Quantity(float(d["quantity"])),
        pnl=float(d["pnl"]),
        entry_time=_dt_from_str(d["entry_time"]) if d.get("entry_time") else None,
        exit_time=_dt_from_str(d["exit_time"]) if d.get("exit_time") else None,
    )


def fill_to_dict(f: Fill) -> Dict[str, Any]:
    """Convert Fill to primitive dict."""
    return {
        "symbol": str(f.symbol),
        "side": f.side,
        "price": float(f.price),
        "quantity": float(f.quantity),
        "time": _dt_to_str(f.time),
    }


def fill_from_dict(d: Dict[str, Any]) -> Fill:
    """Convert primitive dict to Fill."""
    return Fill(
        symbol=Symbol(d["symbol"]),
        side=d["side"],
        price=Price(float(d["price"])),
        quantity=Quantity(float(d["quantity"])),
        time=_dt_from_str(d["time"]),
    )


def backtest_result_to_dict(r: BacktestResult) -> Dict[str, Any]:
    """Convert BacktestResult to primitive dict."""
    return {
        "equity_curve": [float(x) for x in r.equity_curve],
        "trades": [trade_to_dict(t) for t in r.trades],
        "fills": [fill_to_dict(f) for f in r.fills],
    }


def backtest_result_from_dict(d: Dict[str, Any]) -> BacktestResult:
    """Convert primitive dict to BacktestResult."""
    return BacktestResult(
        trades=[trade_from_dict(t) for t in d.get("trades", [])],
        equity_curve=[float(x) for x in d.get("equity_curve", [])],
        fills=[fill_from_dict(f) for f in d.get("fills", [])],
    )
