# Trading Signal Pipeline

An end-to-end trading system prototype that converts strategies into executable signals, runs backtests on historical data, ingests live signals via API, and generates performance reports.

---

## Overview

This project implements a simplified version of a real-world trading pipeline:

* **Strategy Layer** → Generates signals from market data
* **Backtesting Engine** → Simulates trades on historical data
* **Signal Ingestion API** → Accepts trading signals via webhook
* **Execution Layer (Mock)** → Simulates order execution
* **Reporting Layer** → Outputs performance metrics and summaries

---

## Features

* EMA Crossover Strategy (9/21)
* Backtesting on historical OHLCV data (Yahoo Finance)
* Performance metrics:

  * Total Return
  * Win Rate
  * Max Drawdown
  * Number of Trades
* FastAPI-based webhook receiver
* Input validation with Pydantic
* Duplicate signal handling (idempotency)
* Structured logging of signals
* Lightweight reporting (JSON/HTML)

---

## Architecture

The project follows DDD + Clean Architecture layering:

```
trading_signal_pipeline/domain/       → domain model (entities/value objects/policies)
trading_signal_pipeline/application/  → use-cases + app-level services (metrics/reporting)
trading_signal_pipeline/ports/        → interfaces (repositories, broker, writers, publishers)
trading_signal_pipeline/adapters/     → infra implementations (yfinance, file repos, writers, outbox)
trading_signal_pipeline/interfaces/   → interface layer (FastAPI)
```

Design principles:

* Single Responsibility Principle (SRP)
* Strategy pattern for extensibility
* Clear separation between pure logic and side effects

### Flows At A Glance

Backtest (CLI):

```
main.py (CLI)
  -> RunBacktestService
    -> MarketDataProvider (yfinance/binance/csv)
    -> Strategy (EMA crossover)
    -> Backtester + ExecutionModel (simulate fills/trades)
    -> MetricsEngine (total_return, win_rate, max_drawdown, num_trades)
    -> BacktestResultRepository (writes artifacts/latest_backtest.json)
    -> ArtifactWriter(s) (writes backtest_<...>.json + CSVs)
    -> EventPublisher (appends backtest.completed to artifacts/outbox.jsonl)
```

Signal ingestion (API):

```
POST /v1/signals (FastAPI)
  -> IngestSignalService
    -> SignalRepository (dedupe via Idempotency-Key, append artifacts/signals.jsonl)
    -> Broker (mock execution)
    -> EventPublisher (signal.ingested + signal.executed -> artifacts/outbox.jsonl)
```

Reporting (CLI/API):

```
GenerateReportService
  -> reads artifacts/latest_backtest.json (if present)
  -> reads artifacts/signals.jsonl (if present)
  -> MetricsEngine + ReportEngine (sections)
  -> returns JSON (stdout or GET /v1/report/)
```

### Detailed Architecture

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for:

- Package layout and dependency rules (ports/adapters)
- Backtest, ingestion, and reporting flows
- Extension points (strategies, writers, brokers, metrics, reports)

---

## Getting Started

### Prerequisites

- Python 3.12+ recommended
- (Optional) `virtualenv` / `venv`

### Quick Demo (Evaluator-Friendly)

This script runs a backtest, starts the API, demonstrates idempotency, and prints the report:

```bash
PIPELINE_API_KEY=devkey ./scripts/demo.sh
```

### 1. Clone the repository

```bash
git clone https://github.com/towseef41/trading-signal-pipeline.git
cd trading-signal-pipeline
```

### 2. Create a virtualenv (recommended)

```bash
python3 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## Run Backtest

Backtests load OHLCV candles via a pluggable market data provider, run the EMA(9/21)
crossover strategy, compute metrics, and write artifacts via pluggable writers.

Provider note:

- `yfinance` (Yahoo) is convenient for equities, but it is unreliable in many environments:
  - can hit upstream rate limits/blocks (HTTP 429/403) or return empty responses
  - may fail timezone metadata lookups (`YFTzMissingError: No timezone found`)
- Because of that, this project also supports `binance` (public klines endpoint, no API key) and `csv`
  so evaluators can run the backtest deterministically even when Yahoo is flaky.

```bash
python main.py backtest --symbol AAPL --start 2022-01-01 --end 2023-01-01 --interval 1d --output json csv
```

### Binance backtest (crypto)

You can also run the backtest against Binance spot markets (public endpoint, no API key):

```bash
python main.py backtest --provider binance --symbol BTCUSDT --start 2024-01-01 --end 2024-02-01 --interval 1d --output json
```

### Offline backtest (no network)

If you are running in an environment without network access (or yfinance is rate limited),
run the backtest against a local CSV:

```bash
python main.py backtest --provider csv --symbol AAPL --data-file sample_data/AAPL.csv --output json csv
```

### yfinance timezone fallback (optional)

In some environments Yahoo blocks timezone metadata calls, which can trigger a `YFTzMissingError`.
You can provide a fallback timezone:

```bash
python main.py backtest --symbol AAPL --start 2024-01-01 --end 2024-04-01 --interval 1d --yahoo-tz America/New_York --output json
```

Note: this may avoid timezone errors, but it does not bypass upstream rate limiting (HTTP 429).

This will:

* Fetch historical data
* Run EMA strategy
* Simulate trades
* Output performance metrics

### Backtest assumptions (explicit)

- Signals are generated using each candle's `close`.
- By default, backtest execution fills entries/exits at that same candle `close` (a common simplification).
- For stricter realism you can fill on the next bar `open` and/or apply slippage/fees:

```bash
python main.py backtest --provider binance --symbol BTCUSDT --start 2024-01-01 --end 2024-02-01 --interval 1d \
  --fill-model next_open --slippage-bps 5 --fee-bps 10 --output json
```

### Backtest outputs

The default outputs are written under `./artifacts/` (this directory is created on demand).

- JSON artifact: `artifacts/backtest_<SYMBOL>_<TIMESTAMP>.json`
  - What it contains:
    - `meta`: run metadata (symbol, timestamps, provider, interval, params)
    - `metrics`: computed metrics (total_return, win_rate, max_drawdown, num_trades, etc.)
    - `result.equity_curve`: equity over time (one value per candle)
    - `result.trades`: completed round-trip trades (entry + exit + pnl)
    - `result.fills`: per-leg executions (BUY/SELL legs)
- CSV artifacts:
  - `artifacts/backtest_<SYMBOL>_<TIMESTAMP>.metrics.csv`
    - Two columns: `metric,value` (one row per metric)
  - `artifacts/backtest_<SYMBOL>_<TIMESTAMP>.equity.csv`
    - Two columns: `idx,equity` where `idx` is candle index in the series
  - `artifacts/backtest_<SYMBOL>_<TIMESTAMP>.trades.csv`
    - One row per completed trade (round-trip): `symbol,side,entry_price,exit_price,quantity,pnl,entry_time,exit_time`
  - `artifacts/backtest_<SYMBOL>_<TIMESTAMP>.fills.csv` (BUY/SELL legs)
    - One row per fill (entry/exit leg): `symbol,side,price,quantity,time`
- Latest backtest snapshot used by reporting:
  - `artifacts/latest_backtest.json`
    - Same schema as `result` in the JSON artifact (no `meta`/`metrics`), used by the reporting engine.
- Outbox events (JSON Lines):
  - `artifacts/outbox.jsonl`
    - Append-only JSONL event log written by the ingestion pipeline (one JSON object per line).

Note: artifacts are typically ignored by git (see `.gitignore`).

---

## Run API Server

Set an API key for the server (required for protected endpoints):

```bash
export PIPELINE_API_KEY="change-me"
```

```bash
uvicorn trading_signal_pipeline.interfaces.api.v1.app:app --reload
```

API docs:

- Swagger UI: `http://127.0.0.1:8000/docs`
- Health: `GET http://127.0.0.1:8000/health`

Auth:

- Protected endpoints require `X-API-Key: <PIPELINE_API_KEY>`
- Unprotected endpoint: `GET /health`
- Observability: you may send `X-Request-Id` (optional). If omitted, the server generates one and echoes it back.

---

## Example Webhook Request

Endpoint: `POST http://127.0.0.1:8000/v1/signals`

Authentication:

- Set `PIPELINE_API_KEY` on the server.
- Send `X-API-Key: <your key>` with each request.

```json
{
  "symbol": "AAPL",
  "side": "BUY",
  "qty": 10,
  "price": 150.25
}
```

Example `curl`:

```bash
curl -sS -X POST "http://127.0.0.1:8000/v1/signals" \
  -H "X-API-Key: $PIPELINE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"symbol":"AAPL","side":"BUY","qty":10,"price":150.25}'
```

Response shape (success):

```json
{
  "data": {
    "signal": {
      "symbol": "AAPL",
      "side": "BUY",
      "qty": 10.0,
      "price": 150.25,
      "received_at": "2026-01-01T00:00:00+00:00",
      "idempotency_key": "..."
    },
    "execution": {
      "status": "filled",
      "symbol": "AAPL",
      "side": "BUY",
      "qty": 10.0,
      "price": 150.25
    }
  }
}
```

Response headers:

- `X-Request-Id`: request identifier (useful for tracing and matching outbox events)

Behavior:

- Malformed payloads are rejected with `422` (FastAPI/Pydantic validation).
- Duplicate signals are rejected with `400` (`error.code="duplicate_signal"`).
- Accepted signals are persisted to `artifacts/signals.jsonl` with a timestamp.

Response shape (error envelope):

```json
{
  "error": {
    "code": "validation_error",
    "message": "Request validation failed",
    "details": []
  }
}
```

### Test idempotency (duplicate signal handling)

The ingestion endpoint supports an `Idempotency-Key` header. Send the same request twice with the
same `Idempotency-Key`:

```bash
curl -sS -X POST "http://127.0.0.1:8000/v1/signals" \
  -H "X-API-Key: $PIPELINE_API_KEY" \
  -H "X-Request-Id: req-123" \
  -H "Idempotency-Key: demo-1" \
  -H "Content-Type: application/json" \
  -d '{"symbol":"BTCUSDT","side":"BUY","qty":1,"price":100.0}'

# Same key again -> rejected as duplicate
curl -sS -X POST "http://127.0.0.1:8000/v1/signals" \
  -H "X-API-Key: $PIPELINE_API_KEY" \
  -H "X-Request-Id: req-123" \
  -H "Idempotency-Key: demo-1" \
  -H "Content-Type: application/json" \
  -d '{"symbol":"BTCUSDT","side":"BUY","qty":1,"price":100.0}'
```

---

## Reporting

Reporting reads:

- `artifacts/latest_backtest.json` (if present)
- `artifacts/signals.jsonl` (if present)

### CLI report

```bash
python main.py report
```

Outputs a JSON summary (safe to run even before any backtest or webhook ingestion).

### API report

Endpoint: `GET http://127.0.0.1:8000/v1/report/`

```bash
curl -sS "http://127.0.0.1:8000/v1/report/" \
  -H "X-API-Key: $PIPELINE_API_KEY" | python -m json.tool
```

Response shape:

```json
{
  "data": {
    "performance": { "total_return": 0.0, "win_rate": 0.0, "max_drawdown": 0.0, "num_trades": 0 },
    "trades_summary": { "total_trades": 0, "last_trade": null },
    "signals_summary": { "total_signals": 0, "last_signal": null }
  }
}
```

---

## Testing

```bash
pytest
```

If you are using a virtualenv, prefer:

```bash
python -m pytest -q
```

## CI

GitHub Actions runs:

- `pytest` (unit tests)
- `ruff` (light lint: undefined names / syntax errors)
- `mypy` (non-strict type check)

---

## Troubleshooting

- If commands fail with missing packages (e.g. `fastapi`, `yfinance`), make sure your virtualenv is activated (`source venv/bin/activate`) and dependencies are installed.
- If you run `report` without having run a backtest or ingested signals, the report returns zeros/empty summaries instead of erroring.

---

## Docker (Production-Like Run)

### Build and run (Docker)

```bash
docker build -t trading-signal-pipeline .
docker run --rm -p 8000:8000 \
  -e PIPELINE_API_KEY="change-me" \
  -v "$(pwd)/artifacts:/app/artifacts" \
  trading-signal-pipeline
```

Then open:

- `http://127.0.0.1:8000/docs`
- `http://127.0.0.1:8000/health`

### Run with docker-compose

```bash
docker compose up --build
```

### Run CLI commands inside the container

Backtest:

```bash
docker run --rm -v "$(pwd)/artifacts:/app/artifacts" trading-signal-pipeline \
  python main.py backtest --symbol AAPL --output json csv
```

Report:

```bash
docker run --rm -v "$(pwd)/artifacts:/app/artifacts" trading-signal-pipeline \
  python main.py report
```

Notes:

- `./artifacts` is mounted so backtest outputs, signals, and the outbox persist across runs.
- If you do not mount `./artifacts`, container runs will still work but outputs will be ephemeral.

---

## Extensibility

This project is intentionally designed around ports (interfaces) and pluggable components, so these are straightforward to add without rewriting core logic:

* Multiple strategies: implement `trading_signal_pipeline/domain/strategy.py` and plug into `RunBacktestService`
* Additional data providers (e.g., Binance): implement `trading_signal_pipeline/ports/market_data_provider.py`
* Database persistence (e.g., PostgreSQL): implement `trading_signal_pipeline/ports/signal_repository.py` and `trading_signal_pipeline/ports/backtest_result_repository.py`
* Real broker integration: implement `trading_signal_pipeline/ports/broker.py`
* Additional outputs (S3, DB, etc.): implement `trading_signal_pipeline/ports/artifact_writer.py`
* More metrics (Sharpe, Sortino, etc.): implement `trading_signal_pipeline/ports/metric.py` and register in the composition root
* Additional report formats/sections: implement `trading_signal_pipeline/ports/report_section.py` and register in the composition root

---

## Production Considerations (Intentional Gaps)

This is an assessment-focused prototype. The codebase is structured so the following can be added
as adapters/config without rewriting core domain logic:

- Persistence: replace file-backed repos (`*.json`/`*.jsonl`) with DB-backed repositories (e.g., Postgres) and add migrations/retention.
- Auth/security: rotateable API keys or OAuth/JWT, TLS termination, rate limiting, replay protection, audit logs.
- Observability: JSON structured logs, request/correlation IDs, metrics (Prometheus), tracing (OpenTelemetry).
- Execution realism: fill on next-bar open, slippage/fees, partial fills, position sizing, risk limits.
- Reliability: background job queue for execution/outbox publishing, retries/backoff, dead-letter handling.

These are called out explicitly to show a production mindset while keeping the assessment implementation lightweight.

---

## 👤 Author

Towseef Altaf
