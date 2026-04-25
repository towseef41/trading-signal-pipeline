"""
Artifact writer adapters (JSON).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from trading_signal_pipeline.domain.artifact import BacktestArtifact
from trading_signal_pipeline.ports.artifact_writer import ArtifactWriter
from trading_signal_pipeline.serialization.primitives import backtest_result_to_dict


class JsonArtifactWriter(ArtifactWriter):
    """Write a BacktestArtifact to a single JSON file.

    The JSON payload contains:
      - meta: run metadata
      - metrics: computed metrics
      - result: serialized BacktestResult (equity_curve, trades, fills)
    """

    def __init__(self, output_dir: str = "artifacts"):
        """
        Args:
            output_dir: Directory where JSON artifacts will be written.
        """
        self.output_dir = Path(output_dir)

    def write(self, artifact: BacktestArtifact) -> None:
        """Write a backtest artifact to a single JSON file."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        symbol = str(artifact.meta.get("symbol", "UNKNOWN"))
        generated_at = str(artifact.meta.get("generated_at", "artifact"))
        safe_ts = generated_at.replace(":", "").replace(".", "")
        path = self.output_dir / f"backtest_{symbol}_{safe_ts}.json"

        payload: Dict[str, Any] = {
            "meta": artifact.meta,
            "metrics": artifact.metrics,
            "result": backtest_result_to_dict(artifact.result),
        }
        path.write_text(json.dumps(payload, indent=2, default=str) + "\n", encoding="utf-8")
