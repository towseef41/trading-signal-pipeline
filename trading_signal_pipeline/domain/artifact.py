"""
Backtest artifact domain model.

BacktestArtifact is a richer export object that combines results, metrics, and meta.
It is emitted via ArtifactWriter ports to any output target (JSON, CSV, S3, etc.).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

from trading_signal_pipeline.domain.backtest_result import BacktestResult


@dataclass(frozen=True)
class BacktestArtifact:
    """Serializable artifact produced by the RunBacktest use-case."""

    result: BacktestResult
    metrics: Dict[str, float]
    meta: Dict[str, Any]
