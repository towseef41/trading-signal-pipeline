"""
Report section plugin port.

Report sections are plugins that produce JSON-serializable section payloads.
They are modeled as ports so the report engine/use-cases depend only on the
interface, not concrete section implementations.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List

from trading_signal_pipeline.domain.trade import Trade


class ReportSection(ABC):
    """Interface for a report section."""

    @abstractmethod
    def name(self) -> str:
        """Section name used as the report dictionary key."""
        raise NotImplementedError

    @abstractmethod
    def generate(
        self,
        metrics: Dict[str, Any],
        trades: List[Trade],
        signals: List[Any],
    ) -> Dict[str, Any]:
        """
        Generate the section output.

        Args:
            metrics: Computed metric values.
            trades: Completed trades.
            signals: Ingested signals (already serialized as primitives).

        Returns:
            A JSON-serializable dictionary.
        """
        raise NotImplementedError

