"""
FastAPI application entrypoint.
"""

from __future__ import annotations

import uuid

from fastapi import FastAPI
from starlette.requests import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from trading_signal_pipeline.interfaces.api.v1.ingestion import router as webhook_router
from trading_signal_pipeline.interfaces.api.v1.reporting import router as reporting_router
from trading_signal_pipeline.interfaces.api.v1.schemas import ErrorResponse
from trading_signal_pipeline.adapters.logging.request_context import clear_request_id, set_request_id
from trading_signal_pipeline.interfaces.api.v1.constants import HEADER_REQUEST_ID
from trading_signal_pipeline.interfaces.api.v1.error_codes import ERR_HTTP, ERR_VALIDATION

app = FastAPI(title="Signal Ingestion API")


@app.get("/health")
def health():
    """Health check endpoint."""
    return {"status": "ok"}


@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    """
    Ensure every request has an X-Request-Id and propagate it into:
      - response header (X-Request-Id)
      - log context (request_id)
      - application events (correlation_id), when passed through use-cases
    """
    req_id = request.headers.get(HEADER_REQUEST_ID) or str(uuid.uuid4())
    set_request_id(req_id)
    try:
        response = await call_next(request)
        response.headers[HEADER_REQUEST_ID] = req_id
        return response
    finally:
        clear_request_id()


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(_request, exc: StarletteHTTPException):
    """Return a consistent error envelope for HTTP errors."""
    detail = exc.detail
    if isinstance(detail, dict) and "code" in detail and "message" in detail:
        code = str(detail.get("code"))
        message = str(detail.get("message"))
        details = detail.get("details")
    else:
        code = ERR_HTTP
        message = str(detail)
        details = None

    payload = ErrorResponse(error={"code": code, "message": message, "details": details})
    return JSONResponse(status_code=exc.status_code, content=payload.model_dump())


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_request, exc: RequestValidationError):
    """Return a consistent error envelope for request validation errors."""
    payload = ErrorResponse(
        error={
            "code": ERR_VALIDATION,
            "message": "Request validation failed",
            "details": exc.errors(),
        }
    )
    return JSONResponse(status_code=422, content=payload.model_dump())

app.include_router(webhook_router)
app.include_router(reporting_router)
