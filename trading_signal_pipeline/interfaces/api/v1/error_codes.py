"""
API error codes.

These codes are returned in the standard error envelope:
  {"error": {"code": ..., "message": ..., "details": ...}}
"""

from __future__ import annotations


ERR_VALIDATION = "validation_error"
ERR_HTTP = "http_error"
ERR_DUPLICATE_SIGNAL = "duplicate_signal"
ERR_INVALID_API_KEY = "invalid_api_key"
ERR_SERVER_MISCONFIGURED = "server_misconfigured"

