"""
HTTP/API constants.

Centralizes header and environment variable names to avoid hardcoded strings
across the interface layer.
"""

from __future__ import annotations


ENV_PIPELINE_API_KEY = "PIPELINE_API_KEY"

HEADER_API_KEY = "X-API-Key"
HEADER_IDEMPOTENCY_KEY = "Idempotency-Key"
HEADER_REQUEST_ID = "X-Request-Id"

