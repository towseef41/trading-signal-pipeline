import csv
from datetime import datetime, timezone

from trading_signal_pipeline.adapters.output.csv_writer import CsvArtifactWriter
from trading_signal_pipeline.domain.artifact import BacktestArtifact
from trading_signal_pipeline.domain.backtest_result import BacktestResult
from trading_signal_pipeline.domain.fill import Fill
from trading_signal_pipeline.domain.trade import Trade
from trading_signal_pipeline.domain.value_objects import Price, Quantity, Symbol


def test_csv_writer_writes_fills_file(tmp_path):
    t0 = datetime(2024, 1, 1, tzinfo=timezone.utc)
    t1 = datetime(2024, 1, 2, tzinfo=timezone.utc)
    sym = Symbol("AAPL")

    trade = Trade(
        symbol=sym,
        side="SELL",
        entry_price=Price(100.0),
        exit_price=Price(105.0),
        quantity=Quantity(1.0),
        pnl=5.0,
        entry_time=t0,
        exit_time=t1,
    )
    fills = [
        Fill(symbol=sym, side="BUY", price=Price(100.0), quantity=Quantity(1.0), time=t0),
        Fill(symbol=sym, side="SELL", price=Price(105.0), quantity=Quantity(1.0), time=t1),
    ]
    result = BacktestResult(trades=[trade], equity_curve=[100000.0, 100005.0], fills=fills)
    artifact = BacktestArtifact(
        result=result,
        metrics={"total_return": 0.00005},
        meta={"symbol": "AAPL", "generated_at": "2024-01-01T00:00:00+00:00"},
    )

    writer = CsvArtifactWriter(output_dir=str(tmp_path))
    writer.write(artifact)

    fills_path = tmp_path / "backtest_AAPL_2024-01-01T000000+0000.fills.csv"
    assert fills_path.exists()

    with fills_path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 2
    assert rows[0]["side"] == "BUY"
    assert rows[1]["side"] == "SELL"

