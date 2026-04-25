"""
Report engine.

Composes a report by running multiple ReportSection implementations.
"""

from typing import List, Dict

from trading_signal_pipeline.ports.report_section import ReportSection
from trading_signal_pipeline.domain.trade import Trade
from trading_signal_pipeline.ports.report_composer import ReportComposer


class ReportEngine(ReportComposer):
    """
    Composes report from multiple sections.
    """

    def __init__(self, sections: List[ReportSection]):
        """
        Args:
            sections: Report sections to include.
        """
        self.sections = sections

    def generate(
        self,
        metrics: Dict,
        trades: List[Trade],
        signals: List,
    ) -> Dict:
        """
        Generate a report dictionary.

        Args:
            metrics: Computed metrics.
            trades: Completed trades.
            signals: Ingested signals (primitive dicts).

        Returns:
            Dict report.
        """
        report = {}

        for section in self.sections:
            report[section.name()] = section.generate(
                metrics, trades, signals
            )

        return report
