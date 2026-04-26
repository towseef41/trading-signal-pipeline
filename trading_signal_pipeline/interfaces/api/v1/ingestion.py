"""
Webhook ingestion endpoints.
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi import Header

from trading_signal_pipeline.interfaces.api.v1.schemas import (
    ApiResponse,
    ErrorResponse,
    IngestSignalOut,
    SignalEventOut,
    TradeSignal,
)
from trading_signal_pipeline.interfaces.api.v1.dependencies import get_ingest_signal_service
from trading_signal_pipeline.interfaces.api.v1.auth import require_api_key
from trading_signal_pipeline.application.ingest_signal import DuplicateSignalError, IngestSignalService
from trading_signal_pipeline.adapters.logging.logger import logger
from trading_signal_pipeline.adapters.logging.request_context import get_request_id
from trading_signal_pipeline.serialization.primitives import execution_result_to_dict

router = APIRouter(prefix="/v1", tags=["signals"])


def _handle_signal(
    signal: TradeSignal,
    idempotency_key: str | None,
    _auth: None = Depends(require_api_key),
    service: IngestSignalService = Depends(get_ingest_signal_service),
):
    """
    Receives trading signals via webhook.

    Args:
        signal: Validated webhook payload.
        store: SignalRepository dependency.
        broker: Broker dependency.
        publisher: EventPublisher dependency.

    Returns:
        JSON response describing the execution result.
    """

    try:
        event, execution = service.ingest(
            symbol=signal.symbol,
            side=signal.side,
            qty=signal.qty,
            price=signal.price,
            idempotency_key=idempotency_key,
            correlation_id=get_request_id(),
        )
    except DuplicateSignalError as e:
        raise HTTPException(status_code=400, detail={"code": "duplicate_signal", "message": str(e)}) from e

    logger.info(
        "signal_received",
        extra={
            "event": "signal_received",
            "symbol": str(event.symbol),
            "side": event.side,
            "qty": float(event.qty),
            "price": float(event.price),
            "idempotency_key": event.idempotency_key,
        },
    )

    payload = IngestSignalOut(
        signal=SignalEventOut(
            symbol=str(event.symbol),
            side=event.side,
            qty=float(event.qty),
            price=float(event.price),
            received_at=event.received_at,
            idempotency_key=event.idempotency_key,
        ),
        execution=execution_result_to_dict(execution),
    )
    return ApiResponse[IngestSignalOut](data=payload)


@router.post(
    "/signals",
    response_model=ApiResponse[IngestSignalOut],
    responses={
        400: {"model": ErrorResponse},
        401: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
def create_signal(
    signal: TradeSignal,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    _auth: None = Depends(require_api_key),
    service: IngestSignalService = Depends(get_ingest_signal_service),
):
    """
    Ingest a trade signal.

    This is the supported endpoint for signal ingestion.
    """
    return _handle_signal(signal, idempotency_key, _auth=_auth, service=service)


#
# Note: no backwards-compatible `/webhook` alias. The supported endpoint is `/v1/signals`.
