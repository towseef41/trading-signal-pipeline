"""
Artifact writer port.

Writers emit BacktestArtifact objects to any output medium (files, DB, S3, etc.).
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from trading_signal_pipeline.domain.artifact import BacktestArtifact


class ArtifactWriter(ABC):
    """
    Outbound port for emitting artifacts (files, DB, S3, etc.).
    """

    @abstractmethod
    def write(self, artifact: BacktestArtifact) -> None:
        """
        Write a backtest artifact to an output.

        Args:
            artifact: BacktestArtifact to emit.
        """
        raise NotImplementedError
