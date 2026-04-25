"""
Backtest run use-case.

This application service:
  - loads historical market data via MarketDataProvider
  - runs the domain Backtester and Strategy
  - computes metrics
  - persists the latest result
  - emits artifacts via ArtifactWriter ports
  - publishes a completion DomainEvent via EventPublisher
"""

from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from trading_signal_pipeline.domain.artifact import BacktestArtifact
from trading_signal_pipeline.domain.backtesting.backtester import Backtester
from trading_signal_pipeline.domain.events import DomainEvent
from trading_signal_pipeline.domain.strategy import Strategy
from trading_signal_pipeline.ports.artifact_writer import ArtifactWriter
from trading_signal_pipeline.ports.backtest_result_repository import BacktestResultRepository
from trading_signal_pipeline.ports.event_publisher import EventPublisher
from trading_signal_pipeline.ports.market_data_provider import MarketDataProvider
from trading_signal_pipeline.ports.metrics_calculator import MetricsCalculator
from trading_signal_pipeline.serialization.primitives import backtest_result_to_dict


class RunBacktestService:
    """
    Application use-case: load market data, run backtest, compute metrics,
    persist latest result, and emit an artifact via pluggable writers.
    """

    def __init__(
        self,
        data_provider: MarketDataProvider,
        backtester: Backtester,
        result_repo: BacktestResultRepository,
        publisher: EventPublisher,
        metrics: MetricsCalculator,
        writers: Optional[List[ArtifactWriter]] = None,
    ):
        """
        Args:
            data_provider: MarketDataProvider adapter.
            backtester: Domain Backtester.
            result_repo: BacktestResultRepository adapter.
            publisher: EventPublisher adapter.
            metrics: MetricsCalculator implementation.
            writers: Optional ArtifactWriter adapters.
        """
        self.data_provider = data_provider
        self.backtester = backtester
        self.result_repo = result_repo
        self.publisher = publisher
        self.metrics = metrics
        self.writers = writers or []

    def run(
        self,
        symbol: str,
        start: str,
        end: str,
        interval: str,
        strategy: Strategy,
    ) -> BacktestArtifact:
        """
        Run a backtest and emit an artifact.

        Args:
            symbol: Market symbol.
            start: Start date string (provider-dependent format).
            end: End date string (provider-dependent format).
            interval: Candle interval string (e.g. "1d").
            strategy: Domain Strategy.

        Returns:
            BacktestArtifact.
        """
        series = self.data_provider.load(symbol, start=start, end=end, interval=interval)
        result = self.backtester.run(symbol=symbol, series=series, strategy=strategy)

        metrics = self.metrics.compute_all(
            result.trades,
            result.equity_curve,
            initial_capital=self.backtester.initial_capital,
        )

        artifact = BacktestArtifact(
            result=result,
            metrics=metrics,
            meta={
                "symbol": symbol,
                "start": start,
                "end": end,
                "interval": interval,
                "strategy": strategy.__class__.__name__,
                "strategy_params": asdict(strategy) if hasattr(strategy, "__dataclass_fields__") else {},
                "generated_at": datetime.now(timezone.utc).isoformat(),
            },
        )

        self.result_repo.save_latest(result)
        for w in self.writers:
            w.write(artifact)

        self.publisher.publish(
            DomainEvent.now(
                name="backtest.completed",
                payload={
                    "meta": artifact.meta,
                    "metrics": artifact.metrics,
                    "result": backtest_result_to_dict(artifact.result),
                },
                correlation_id=f"backtest:{symbol}:{artifact.meta.get('generated_at')}",
            )
        )

        return artifact
