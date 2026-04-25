"""
FastAPI application entrypoint.
"""

from fastapi import FastAPI
from trading_signal_pipeline.interfaces.api.v1.ingestion import router as webhook_router
from trading_signal_pipeline.interfaces.api.v1.reporting import router as reporting_router

app = FastAPI(title="Signal Ingestion API")


@app.get("/health")
def health():
    """Health check endpoint."""
    return {"status": "ok"}

app.include_router(webhook_router)
app.include_router(reporting_router)
