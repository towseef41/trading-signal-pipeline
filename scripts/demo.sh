#!/usr/bin/env bash
set -euo pipefail

# End-to-end demo script for evaluators:
# - Runs a backtest (Binance provider by default)
# - Starts the API server
# - Sends a webhook signal twice with the same Idempotency-Key (shows dedupe)
# - Fetches the report output
#
# Usage:
#   PIPELINE_API_KEY=devkey ./scripts/demo.sh
#
# Optional env vars:
#   PORT=8000
#   SYMBOL=BTCUSDT
#   START=2024-01-01
#   END=2024-02-01
#   INTERVAL=1d
#   PROVIDER=binance   # {binance,yfinance,csv}
#   OUTPUT="json csv"
#   CLEAN_ARTIFACTS=0  # set to 1 to wipe ./artifacts before running

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

PORT="${PORT:-8000}"
SYMBOL="${SYMBOL:-BTCUSDT}"
START="${START:-2024-01-01}"
END="${END:-2024-02-01}"
INTERVAL="${INTERVAL:-1d}"
PROVIDER="${PROVIDER:-binance}"
OUTPUT="${OUTPUT:-json csv}"
CLEAN_ARTIFACTS="${CLEAN_ARTIFACTS:-0}"

if [[ -z "${PIPELINE_API_KEY:-}" ]]; then
  echo "ERROR: PIPELINE_API_KEY must be set (e.g. PIPELINE_API_KEY=devkey ./scripts/demo.sh)" >&2
  exit 1
fi

PY="./venv/bin/python"
UVICORN="./venv/bin/uvicorn"
if [[ ! -x "$PY" ]]; then
  PY="python"
fi
if [[ ! -x "$UVICORN" ]]; then
  UVICORN="uvicorn"
fi

if [[ "$CLEAN_ARTIFACTS" == "1" ]]; then
  rm -f artifacts/* 2>/dev/null || true
fi

echo "== Backtest =="
$PY main.py backtest \
  --provider "$PROVIDER" \
  --symbol "$SYMBOL" \
  --start "$START" \
  --end "$END" \
  --interval "$INTERVAL" \
  --output $OUTPUT

echo
echo "== Start API (PORT=$PORT) =="
$UVICORN trading_signal_pipeline.interfaces.api.v1.app:app --port "$PORT" --log-level warning &
API_PID="$!"
cleanup() {
  kill "$API_PID" 2>/dev/null || true
  wait "$API_PID" 2>/dev/null || true
}
trap cleanup EXIT

for _ in {1..100}; do
  if curl -fsS "http://127.0.0.1:${PORT}/health" >/dev/null 2>&1; then
    break
  fi
  sleep 0.1
done

echo
echo "== Webhook (idempotency demo) =="
idem_key="demo-$(date +%s)"

code1="$(curl -sS -o /tmp/ingest1.json -w "%{http_code}" -X POST "http://127.0.0.1:${PORT}/v1/signals" \
  -H "X-API-Key: ${PIPELINE_API_KEY}" \
  -H "Idempotency-Key: ${idem_key}" \
  -H "Content-Type: application/json" \
  -d "{\"symbol\":\"${SYMBOL}\",\"side\":\"BUY\",\"qty\":1,\"price\":100.0}")"
echo "first request: HTTP $code1"
cat /tmp/ingest1.json || true
echo

code2="$(curl -sS -o /tmp/ingest2.json -w "%{http_code}" -X POST "http://127.0.0.1:${PORT}/v1/signals" \
  -H "X-API-Key: ${PIPELINE_API_KEY}" \
  -H "Idempotency-Key: ${idem_key}" \
  -H "Content-Type: application/json" \
  -d "{\"symbol\":\"${SYMBOL}\",\"side\":\"BUY\",\"qty\":1,\"price\":100.0}")"
echo "duplicate request (same Idempotency-Key): HTTP $code2"
cat /tmp/ingest2.json || true
echo

echo
echo "== Report =="
curl -sS "http://127.0.0.1:${PORT}/v1/report/" -H "X-API-Key: ${PIPELINE_API_KEY}"
echo

