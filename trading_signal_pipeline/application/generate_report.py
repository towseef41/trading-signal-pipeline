"""
Reporting use-case.

This application service loads stored signals and the latest backtest result,
computes metrics, and composes a report via ReportSection plugins.
"""

from __future__ import annotations

from typing import Dict, Any, List

from trading_signal_pipeline.domain.trade import Trade
from trading_signal_pipeline.ports.backtest_result_repository import BacktestResultRepository
from trading_signal_pipeline.ports.signal_repository import SignalRepository
from trading_signal_pipeline.ports.metrics_calculator import MetricsCalculator
from trading_signal_pipeline.ports.report_composer import ReportComposer
from trading_signal_pipeline.serialization.primitives import signal_event_to_dict


class GenerateReportService:
    """
    Application service for producing a report from stored results + signals.
    """

    def __init__(
        self,
        signal_repo: SignalRepository,
        backtest_repo: BacktestResultRepository,
        metrics: MetricsCalculator,
        report: ReportComposer,
        initial_capital: float = 100000,
    ):
        """
        Args:
            signal_repo: Repository of ingested signals.
            backtest_repo: Repository containing the latest backtest result.
            metrics: MetricsCalculator implementation.
            report: ReportComposer implementation.
            initial_capital: Default initial capital for metrics when no result exists.
        """
        self.signal_repo = signal_repo
        self.backtest_repo = backtest_repo
        self.metrics = metrics
        self.report = report
        self.initial_capital = initial_capital

    def generate(self) -> Dict[str, Any]:
        """
        Generate a report.

        Returns:
            JSON-serializable dictionary containing report sections.
        """
        signals = [signal_event_to_dict(s) for s in self.signal_repo.list()]

        result = self.backtest_repo.get_latest()
        trades: List[Trade] = result.trades if result else []
        equity_curve = result.equity_curve if result else [self.initial_capital]

        metrics = self.metrics.compute_all(
            trades, equity_curve, initial_capital=self.initial_capital
        )
        return self.report.generate(metrics, trades, signals)
