# Architecture

This project is intentionally structured as a small DDD + Clean Architecture / Hexagonal (Ports & Adapters) system.

The goal is that business logic is testable and framework-free, while I/O concerns (files, HTTP, yfinance) are isolated behind interfaces.

---

## High-Level Layout

```
trading_signal_pipeline/
  domain/          # Pure domain model (entities/value objects/policies)
  application/     # Use-cases (orchestration) + app-level services
    metrics/       # Metric plugins + engine
    reporting/     # Report sections + engine
  ports/           # Interfaces/ports (repos, broker, writers, publisher, data provider)
  adapters/        # Concrete implementations of ports (files, yfinance, outbox, mock broker)
  interfaces/      # HTTP interface layer (FastAPI)
main.py            # CLI composition root (wire ports -> adapters)
```

---

## Dependency Rule

Dependencies point inward:

```
interfaces/  -> application/ -> ports/ + domain/
adapters/    -> ports/ + domain/
domain/      -> (depends on nothing in this repo)
```

No module in `domain/` imports from `interfaces/` or `adapters/`.

---

## Core Domain Concepts

- Market data:
  - `domain/market.py` defines `Candle` and `MarketSeries`
- Strategy:
  - `domain/strategy.py` is the contract
  - `domain/strategies/ema_crossover.py` implements EMA(9/21) crossover
- Backtesting:
  - `domain/backtesting/backtester.py` runs a strategy against a `MarketSeries`
  - `domain/backtesting/execution.py` defines an `ExecutionModel` policy
  - `domain/backtesting/portfolio.py` and `domain/backtesting/position.py` hold state
  - Output is `domain/backtest_result.py` (`BacktestResult`)
- Signals / execution:
  - `domain/signal.py` contains `SignalType` and `SignalEvent` (webhook ingest)
  - `domain/execution.py` contains `ExecutionResult`
- Value objects:
  - `domain/value_objects.py` (`Symbol`, `Price`, `Quantity`, `Volume`) enforce basic invariants
- Execution realism (pluggable policies):
  - Fill model decides when/at-what-price to fill (same-bar close vs next-bar open)
  - Cost model applies slippage/fees (in basis points)

---

## Ports (Interfaces)

Ports are the contracts the application layer depends on:

- `ports/market_data_provider.py`: load OHLCV for backtests
- `ports/backtest_result_repository.py`: persist and retrieve latest backtest result
- `ports/signal_repository.py`: persist and dedupe ingested signals
- `ports/broker.py`: execute signals (mocked here)
- `ports/artifact_writer.py`: write backtest artifacts (JSON/CSV/etc.)
- `ports/event_publisher.py`: publish domain events (outbox/event-bus)

---

## Adapters (Implementations)

Concrete implementations of ports live in `adapters/`:

- Market data:
  - `adapters/market_data/yfinance_provider.py` implements `MarketDataProvider`
  - `adapters/market_data/binance_provider.py` implements `MarketDataProvider` (public klines API, no key)
  - `adapters/market_data/csv_provider.py` implements `MarketDataProvider` (offline/local CSV)
- Persistence:
  - `adapters/storage/file_backtest_repo.py` writes `artifacts/latest_backtest.json`
  - `adapters/storage/file_signal_repo.py` appends to `artifacts/signals.jsonl`
- Output writers:
  - `adapters/output/json_writer.py` writes a single JSON artifact
  - `adapters/output/csv_writer.py` writes metrics/equity/trades/fills as CSV
- Broker:
  - `adapters/execution/broker.py` is a `MockBroker` implementation
- Outbox/event publishing:
  - `adapters/outbox/file_publisher.py` appends to `artifacts/outbox.jsonl`

Serialization details are kept out of the domain and centralized in:

- `serialization/primitives.py` (domain objects <-> JSON-friendly primitives)

---

## Application Use-Cases

Use-cases are thin orchestrators that coordinate ports:

### RunBacktest

File: `application/run_backtest.py`

Flow:

```
MarketDataProvider.load(symbol, start, end, interval)
  -> Backtester.run(symbol, series, strategy)
  -> MetricsEngine.compute_all(trades, equity_curve)
  -> BacktestResultRepository.save_latest(result)
  -> ArtifactWriter.write(artifact) (0..N writers)
  -> EventPublisher.publish(backtest.completed)
```

Artifacts written (default):

- `artifacts/latest_backtest.json` (latest `BacktestResult`, used by reporting)
- `artifacts/backtest_<SYMBOL>_<TIMESTAMP>.json` (meta + metrics + result)
- `artifacts/backtest_<SYMBOL>_<TIMESTAMP>.metrics.csv`
- `artifacts/backtest_<SYMBOL>_<TIMESTAMP>.equity.csv`
- `artifacts/backtest_<SYMBOL>_<TIMESTAMP>.trades.csv`
- `artifacts/backtest_<SYMBOL>_<TIMESTAMP>.fills.csv` (entry/exit legs)
- `artifacts/outbox.jsonl` (includes `backtest.completed`)

### IngestSignal

File: `application/ingest_signal.py`

Flow:

```
create SignalEvent (with idempotency key + timestamp)
  -> SignalRepository.is_duplicate(event)
  -> SignalRepository.add(event)
  -> Broker.execute(event)
  -> EventPublisher.publish(signal.ingested)
  -> EventPublisher.publish(signal.executed)
```

Idempotency:

- The HTTP layer accepts an `Idempotency-Key` header.
- The `SignalRepository` tracks previously-seen keys and rejects duplicates to prevent re-processing.

### GenerateReport

File: `application/generate_report.py`

Flow:

```
signals = SignalRepository.list()
result  = BacktestResultRepository.get_latest()
metrics = MetricsEngine.compute_all(...)
report  = ReportEngine.generate(metrics, trades, signals)
```

Report output:

- CLI (`python main.py report`) prints JSON to stdout.
- API (`GET /v1/report/`) returns the same report as JSON.

---

## HTTP Interface (FastAPI)

The HTTP layer adapts request/response DTOs to use-cases and returns JSON.

Location:

- `interfaces/api/v1/app.py`
- `interfaces/api/v1/ingestion.py` (`POST /v1/signals`)
- `interfaces/api/v1/reporting.py` (`GET /v1/report/`)
- `interfaces/api/v1/dependencies.py` wires ports -> adapters
- `interfaces/api/v1/auth.py` enforces `X-API-Key` against env `PIPELINE_API_KEY`

The interface layer should contain:

- request validation (Pydantic)
- mapping primitives -> use-case calls
- mapping use-case outputs -> JSON responses

It should not contain business rules (those live in `domain/` + `application/`).

---

## Extension Points (Evaluator-Friendly)

Common ways to extend without touching the domain:

- Add a new strategy: implement `domain/strategy.py` and plug into `RunBacktestService`
- Add a new data source: implement `ports/market_data_provider.py`
- Add a new output: implement `ports/artifact_writer.py` (e.g., S3Writer, PostgresWriter)
- Add a real broker: implement `ports/broker.py`
- Add new metrics: implement `ports/metric.py` and register in the composition root
- Add new report sections: implement `ports/report_section.py` and register in the composition root
