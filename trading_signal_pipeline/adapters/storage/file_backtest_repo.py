"""
Backtest result repository adapters.

JsonBacktestResultRepository stores only the latest BacktestResult as a JSON file.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from trading_signal_pipeline.domain.backtest_result import BacktestResult
from trading_signal_pipeline.ports.backtest_result_repository import BacktestResultRepository
from trading_signal_pipeline.serialization.primitives import backtest_result_from_dict, backtest_result_to_dict


class JsonBacktestResultRepository(BacktestResultRepository):
    """
    File-backed repository storing only the latest backtest result.
    """

    def __init__(self, path: str = "artifacts/latest_backtest.json"):
        """
        Args:
            path: JSON path used to store the latest result.
        """
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._cache: Optional[BacktestResult] = None

        if self.path.exists():
            d = json.loads(self.path.read_text(encoding="utf-8"))
            self._cache = backtest_result_from_dict(d)

    def get_latest(self) -> Optional[BacktestResult]:
        """See BacktestResultRepository."""
        return self._cache

    def save_latest(self, result: BacktestResult) -> None:
        """See BacktestResultRepository."""
        self._cache = result
        payload = backtest_result_to_dict(result)
        self.path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
