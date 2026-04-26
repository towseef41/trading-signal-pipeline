"""
FastAPI application entrypoint.
"""

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from trading_signal_pipeline.interfaces.api.v1.ingestion import router as webhook_router
from trading_signal_pipeline.interfaces.api.v1.reporting import router as reporting_router
from trading_signal_pipeline.interfaces.api.v1.schemas import ErrorResponse

app = FastAPI(title="Signal Ingestion API")


@app.get("/health")
def health():
    """Health check endpoint."""
    return {"status": "ok"}


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(_request, exc: StarletteHTTPException):
    """Return a consistent error envelope for HTTP errors."""
    detail = exc.detail
    if isinstance(detail, dict) and "code" in detail and "message" in detail:
        code = str(detail.get("code"))
        message = str(detail.get("message"))
        details = detail.get("details")
    else:
        code = "http_error"
        message = str(detail)
        details = None

    payload = ErrorResponse(error={"code": code, "message": message, "details": details})
    return JSONResponse(status_code=exc.status_code, content=payload.model_dump())


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_request, exc: RequestValidationError):
    """Return a consistent error envelope for request validation errors."""
    payload = ErrorResponse(
        error={
            "code": "validation_error",
            "message": "Request validation failed",
            "details": exc.errors(),
        }
    )
    return JSONResponse(status_code=422, content=payload.model_dump())

app.include_router(webhook_router)
app.include_router(reporting_router)
