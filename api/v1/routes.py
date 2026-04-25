from fastapi import APIRouter, HTTPException, Depends

from api.v1.schemas import TradeSignal
from api.v1.dependencies import get_signal_store, get_broker
from infra.storage.base import SignalStore
from infra.execution.base import Broker
from infra.logging.logger import logger

router = APIRouter(prefix="/v1")


@router.post("/webhook")
def receive_signal(
    signal: TradeSignal,
    store: SignalStore = Depends(get_signal_store),
    broker: Broker = Depends(get_broker),
):
    """
    Receives trading signals via webhook.
    """

    # Duplicate check
    if store.is_duplicate(signal):
        raise HTTPException(status_code=400, detail="Duplicate signal")

    # Store + log
    store.add(signal)
    logger.info(f"Received signal: {signal}")

    # Execute
    execution_result = broker.execute(signal)

    return {
        "message": "Signal processed",
        "execution": execution_result,
    }