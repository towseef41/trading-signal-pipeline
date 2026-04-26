"""
Default filesystem paths.

Centralizes default artifact filenames/locations so adapters and composition
roots don't duplicate hardcoded strings.
"""

from __future__ import annotations


DEFAULT_ARTIFACTS_DIR = "artifacts"

DEFAULT_LATEST_BACKTEST_PATH = f"{DEFAULT_ARTIFACTS_DIR}/latest_backtest.json"
DEFAULT_SIGNALS_PATH = f"{DEFAULT_ARTIFACTS_DIR}/signals.jsonl"
DEFAULT_OUTBOX_PATH = f"{DEFAULT_ARTIFACTS_DIR}/outbox.jsonl"

