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


def require_api_key(x_api_key: str | None = Header(default=None, alias="X-API-Key")) -> None:
    """
    Require a valid API key header.

    Args:
        x_api_key: Value of the X-API-Key header.

    Raises:
        HTTPException: 500 if the server is misconfigured (no key set),
            401 if the provided key is missing/invalid.
    """
    expected = os.environ.get("PIPELINE_API_KEY")
    if not expected:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "server_misconfigured", "message": "PIPELINE_API_KEY not set"},
        )

    if not x_api_key or not hmac.compare_digest(x_api_key, expected):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "invalid_api_key", "message": "Invalid API key"},
        )
