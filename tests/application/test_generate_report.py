from trading_signal_pipeline.application.generate_report import GenerateReportService
from trading_signal_pipeline.application.metrics.metrics import (
    MaxDrawdown,
    NumTrades,
    TotalReturn,
    WinRate,
)
from trading_signal_pipeline.application.metrics.registry import MetricsEngine
from trading_signal_pipeline.application.reporting.engine import ReportEngine
from trading_signal_pipeline.application.reporting.sections import PerformanceSection, SignalsSection, TradesSection


class EmptySignalRepo:
    def list(self):
        return []

    def is_duplicate(self, signal):
        return False

    def add(self, signal):
        raise AssertionError("not used")


class EmptyBacktestRepo:
    def get_latest(self):
        return None

    def save_latest(self, result):
        raise AssertionError("not used")


def test_generate_report_safe_with_no_backtest_and_no_signals():
    metrics = MetricsEngine([TotalReturn(), WinRate(), MaxDrawdown(), NumTrades()])
    report = ReportEngine([PerformanceSection(), TradesSection(), SignalsSection()])
    svc = GenerateReportService(
        signal_repo=EmptySignalRepo(),
        backtest_repo=EmptyBacktestRepo(),
        metrics=metrics,
        report=report,
        initial_capital=100000,
    )

    out = svc.generate()
    assert out["performance"]["num_trades"] == 0
    assert out["trades_summary"]["total_trades"] == 0
    assert out["signals_summary"]["total_signals"] == 0

