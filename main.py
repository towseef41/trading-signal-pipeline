from __future__ import annotations

"""
CLI entrypoint.

Provides small commands to run a backtest and generate a report using the same
application services as the API.
"""

import argparse
import json

from trading_signal_pipeline.application.generate_report import GenerateReportService
from trading_signal_pipeline.application.run_backtest import RunBacktestService
from trading_signal_pipeline.application.metrics.metrics import TotalReturn, WinRate, MaxDrawdown, NumTrades
from trading_signal_pipeline.application.metrics.registry import MetricsEngine
from trading_signal_pipeline.application.reporting.engine import ReportEngine
from trading_signal_pipeline.application.reporting.sections import PerformanceSection, TradesSection, SignalsSection
from trading_signal_pipeline.domain.backtesting.backtester import Backtester
from trading_signal_pipeline.domain.backtesting.execution import LongOnlyExecution
from trading_signal_pipeline.domain.strategies.ema_crossover import EMACrossoverStrategy
from trading_signal_pipeline.adapters.market_data.csv_provider import CsvMarketDataProvider
from trading_signal_pipeline.adapters.market_data.binance_provider import BinanceMarketDataProvider
from trading_signal_pipeline.adapters.market_data.yfinance_provider import YFinanceMarketDataProvider
from trading_signal_pipeline.adapters.output.csv_writer import CsvArtifactWriter
from trading_signal_pipeline.adapters.output.json_writer import JsonArtifactWriter
from trading_signal_pipeline.adapters.outbox.file_publisher import FileOutboxPublisher
from trading_signal_pipeline.adapters.storage.file_backtest_repo import JsonBacktestResultRepository
from trading_signal_pipeline.adapters.storage.file_signal_repo import JsonlSignalRepository


def _cmd_backtest(args: argparse.Namespace) -> int:
    """Run a backtest command and print metrics to stdout."""
    if args.provider == "csv":
        if not args.data_file:
            raise SystemExit("--data-file is required when --provider=csv")
        provider = CsvMarketDataProvider(args.data_file)
    elif args.provider == "binance":
        provider = BinanceMarketDataProvider()
    else:
        provider = YFinanceMarketDataProvider(default_timezone=args.yahoo_tz)
    backtester = Backtester(
        execution=LongOnlyExecution(quantity=args.quantity),
        initial_capital=args.initial_capital,
    )
    result_repo = JsonBacktestResultRepository()

    writers = []
    if "json" in args.output:
        writers.append(JsonArtifactWriter())
    if "csv" in args.output:
        writers.append(CsvArtifactWriter())

    svc = RunBacktestService(
        data_provider=provider,
        backtester=backtester,
        result_repo=result_repo,
        publisher=FileOutboxPublisher(),
        metrics=MetricsEngine([TotalReturn(), WinRate(), MaxDrawdown(), NumTrades()]),
        writers=writers,
    )

    strategy = EMACrossoverStrategy(
        short_window=args.short_window,
        long_window=args.long_window,
    )

    artifact = svc.run(
        symbol=args.symbol,
        start=args.start,
        end=args.end,
        interval=args.interval,
        strategy=strategy,
    )

    print(json.dumps({"meta": artifact.meta, "metrics": artifact.metrics}, indent=2))
    return 0


def _cmd_report(args: argparse.Namespace) -> int:
    """Generate a report command and print JSON to stdout."""
    signal_repo = JsonlSignalRepository()
    backtest_repo = JsonBacktestResultRepository()
    metrics = MetricsEngine([TotalReturn(), WinRate(), MaxDrawdown(), NumTrades()])
    report = ReportEngine([PerformanceSection(), TradesSection(), SignalsSection()])
    svc = GenerateReportService(
        signal_repo,
        backtest_repo,
        metrics=metrics,
        report=report,
        initial_capital=args.initial_capital,
    )
    report = svc.generate()
    print(json.dumps(report, indent=2, default=str))
    return 0


def main(argv: list[str] | None = None) -> int:
    """
    CLI entrypoint.

    Args:
        argv: Optional argument vector (defaults to sys.argv).

    Returns:
        Process exit code.
    """
    p = argparse.ArgumentParser(prog="trading-signal-pipeline")
    sub = p.add_subparsers(dest="cmd", required=True)

    bt = sub.add_parser("backtest", help="Run EMA crossover backtest and emit artifacts")
    bt.add_argument("--symbol", default="AAPL")
    bt.add_argument("--start", default="2022-01-01")
    bt.add_argument("--end", default="2023-01-01")
    bt.add_argument("--interval", default="1d")
    bt.add_argument("--initial-capital", type=float, default=100000.0)
    bt.add_argument("--short-window", type=int, default=9)
    bt.add_argument("--long-window", type=int, default=21)
    bt.add_argument("--quantity", type=float, default=1.0)
    bt.add_argument(
        "--provider",
        choices=["yfinance", "binance", "csv"],
        default="yfinance",
        help="Market data provider to use for backtesting.",
    )
    bt.add_argument("--data-file", default=None, help="Path to a local OHLCV CSV file (offline backtests).")
    bt.add_argument("--yahoo-tz", default=None, help="Fallback timezone for yfinance (e.g. America/New_York).")
    bt.add_argument("--output", nargs="+", choices=["json", "csv"], default=["json"])
    bt.set_defaults(func=_cmd_backtest)

    rp = sub.add_parser("report", help="Generate a report from stored artifacts")
    rp.add_argument("--initial-capital", type=float, default=100000.0)
    rp.set_defaults(func=_cmd_report)

    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
