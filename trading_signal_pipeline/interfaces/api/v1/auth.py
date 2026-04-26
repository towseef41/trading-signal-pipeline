"""
API authentication dependencies.

For this project we use a simple API key header check:
  - Client sends: X-API-Key: <key>
  - Server verifies against env var: PIPELINE_API_KEY

This keeps auth concerns in the interface layer (not in domain/application).
"""

from __future__ import annotations

import hmac
import os

from fastapi import Header, HTTPException, status

from trading_signal_pipeline.interfaces.api.v1.constants import ENV_PIPELINE_API_KEY, HEADER_API_KEY
from trading_signal_pipeline.interfaces.api.v1.error_codes import ERR_INVALID_API_KEY, ERR_SERVER_MISCONFIGURED


def require_api_key(x_api_key: str | None = Header(default=None, alias=HEADER_API_KEY)) -> None:
    """
    Require a valid API key header.

    Args:
        x_api_key: Value of the X-API-Key header.

    Raises:
        HTTPException: 500 if the server is misconfigured (no key set),
            401 if the provided key is missing/invalid.
    """
    expected = os.environ.get(ENV_PIPELINE_API_KEY)
    if not expected:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": ERR_SERVER_MISCONFIGURED, "message": f"{ENV_PIPELINE_API_KEY} not set"},
        )

    if not x_api_key or not hmac.compare_digest(x_api_key, expected):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": ERR_INVALID_API_KEY, "message": "Invalid API key"},
        )
