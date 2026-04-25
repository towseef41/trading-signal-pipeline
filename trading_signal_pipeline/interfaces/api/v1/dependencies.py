"""
FastAPI dependency providers (composition root).

This is where ports are wired to concrete infra adapters.
"""

from functools import lru_cache

from fastapi import Depends

from trading_signal_pipeline.adapters.execution.broker import MockBroker
from trading_signal_pipeline.adapters.storage.file_signal_repo import JsonlSignalRepository
from trading_signal_pipeline.adapters.storage.file_backtest_repo import JsonBacktestResultRepository
from trading_signal_pipeline.adapters.outbox.file_publisher import FileOutboxPublisher
from trading_signal_pipeline.application.metrics.metrics import TotalReturn, WinRate, MaxDrawdown, NumTrades
from trading_signal_pipeline.application.metrics.registry import MetricsEngine
from trading_signal_pipeline.application.reporting.engine import ReportEngine
from trading_signal_pipeline.application.reporting.sections import PerformanceSection, TradesSection, SignalsSection
from trading_signal_pipeline.application.generate_report import GenerateReportService
from trading_signal_pipeline.application.ingest_signal import IngestSignalService
from trading_signal_pipeline.ports.signal_repository import SignalRepository
from trading_signal_pipeline.ports.backtest_result_repository import BacktestResultRepository
from trading_signal_pipeline.ports.broker import Broker
from trading_signal_pipeline.ports.event_publisher import EventPublisher
from trading_signal_pipeline.ports.metrics_calculator import MetricsCalculator
from trading_signal_pipeline.ports.report_composer import ReportComposer


@lru_cache
def get_signal_store() -> SignalRepository:
    """Provide a SignalRepository implementation."""
    return JsonlSignalRepository()


@lru_cache
def get_broker() -> Broker:
    """Provide a Broker implementation."""
    return MockBroker()


@lru_cache
def get_backtest_store() -> BacktestResultRepository:
    """Provide a BacktestResultRepository implementation."""
    return JsonBacktestResultRepository()


@lru_cache
def get_event_publisher() -> EventPublisher:
    """Provide an EventPublisher implementation."""
    return FileOutboxPublisher()


@lru_cache
def get_metrics_calculator() -> MetricsCalculator:
    """Provide the MetricsCalculator implementation used by use-cases."""
    return MetricsEngine([TotalReturn(), WinRate(), MaxDrawdown(), NumTrades()])


@lru_cache
def get_report_composer() -> ReportComposer:
    """Provide the ReportComposer implementation used by use-cases."""
    return ReportEngine([PerformanceSection(), TradesSection(), SignalsSection()])


def get_generate_report_service(
    signal_repo: SignalRepository = Depends(get_signal_store),
    backtest_repo: BacktestResultRepository = Depends(get_backtest_store),
    metrics: MetricsCalculator = Depends(get_metrics_calculator),
    report: ReportComposer = Depends(get_report_composer),
) -> GenerateReportService:
    """
    Provide GenerateReportService.
    """
    return GenerateReportService(signal_repo, backtest_repo, metrics=metrics, report=report, initial_capital=100000)


def get_ingest_signal_service(
    signal_repo: SignalRepository = Depends(get_signal_store),
    broker: Broker = Depends(get_broker),
    publisher: EventPublisher = Depends(get_event_publisher),
) -> IngestSignalService:
    """
    Provide IngestSignalService.
    """
    return IngestSignalService(repo=signal_repo, broker=broker, publisher=publisher)
