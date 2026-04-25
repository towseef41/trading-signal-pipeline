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

The project follows a clean separation of concerns:

```
core/        → Strategy, Backtest Engine, Metrics
infra/       → Data loading, storage, logging
interface/   → API endpoints and reporting
```

Design principles:

* Single Responsibility Principle (SRP)
* Strategy pattern for extensibility
* Clear separation between pure logic and side effects

---

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/your-username/trading-signal-pipeline.git
cd trading-signal-pipeline
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

---

## Run Backtest

```bash
python main.py backtest
```

This will:

* Fetch historical data
* Run EMA strategy
* Simulate trades
* Output performance metrics

---

## Run API Server

```bash
uvicorn interface.api:app --reload
```

---

## Example Webhook Request

```json
{
  "symbol": "AAPL",
  "side": "BUY",
  "qty": 10,
  "price": 150.25
}
```

---

## Reporting

```bash
python main.py report
```

Outputs:

* Backtest results
* Signal logs summary

---

## Testing

```bash
pytest
```

---

## Future Improvements

* Support multiple strategies
* Add database persistence (PostgreSQL)
* Real broker integration
* Strategy configuration via YAML
* Advanced metrics (Sharpe ratio, etc.)

---

## Notes

This project is designed as a clean, extensible prototype — balancing simplicity with production-oriented design principles.

---

## 👤 Author

Towseef Altaf
