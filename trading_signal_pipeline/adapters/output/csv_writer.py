"""
Artifact writer adapters (CSV).
"""

from __future__ import annotations

import csv
from pathlib import Path

from trading_signal_pipeline.domain.artifact import BacktestArtifact
from trading_signal_pipeline.ports.artifact_writer import ArtifactWriter
from trading_signal_pipeline.serialization.primitives import fill_to_dict, trade_to_dict


class CsvArtifactWriter(ArtifactWriter):
    """
    CSV writer splits output into tabular files.
    """

    def __init__(self, output_dir: str = "artifacts"):
        """
        Args:
            output_dir: Directory where CSV artifacts will be written.
        """
        self.output_dir = Path(output_dir)

    def write(self, artifact: BacktestArtifact) -> None:
        """
        Write metrics, equity curve, and trades to separate CSV files.
        """
        self.output_dir.mkdir(parents=True, exist_ok=True)
        symbol = str(artifact.meta.get("symbol", "UNKNOWN"))
        generated_at = str(artifact.meta.get("generated_at", "artifact"))
        safe_ts = generated_at.replace(":", "").replace(".", "")
        base = self.output_dir / f"backtest_{symbol}_{safe_ts}"

        # Metrics
        with (base.with_suffix(".metrics.csv")).open("w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["metric", "value"])
            for k, v in artifact.metrics.items():
                w.writerow([k, v])

        # Equity curve
        with (base.with_suffix(".equity.csv")).open("w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["idx", "equity"])
            for i, v in enumerate(artifact.result.equity_curve):
                w.writerow([i, v])

        # Trades
        with (base.with_suffix(".trades.csv")).open("w", newline="", encoding="utf-8") as f:
            fieldnames = [
                "symbol",
                "side",
                "entry_price",
                "exit_price",
                "quantity",
                "pnl",
                "entry_time",
                "exit_time",
            ]
            w = csv.DictWriter(f, fieldnames=fieldnames)
            w.writeheader()
            for t in artifact.result.trades:
                row = trade_to_dict(t)
                w.writerow(row)

        # Fills (entry/exit legs)
        with (base.with_suffix(".fills.csv")).open("w", newline="", encoding="utf-8") as f:
            fieldnames = ["symbol", "side", "price", "quantity", "time"]
            w = csv.DictWriter(f, fieldnames=fieldnames)
            w.writeheader()
            for fill in artifact.result.fills:
                w.writerow(fill_to_dict(fill))
