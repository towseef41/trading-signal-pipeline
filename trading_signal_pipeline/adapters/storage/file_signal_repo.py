"""
Signal repository adapters.

JsonlSignalRepository persists SignalEvent objects as JSON Lines.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import List

from trading_signal_pipeline.domain.signal import SignalEvent
from trading_signal_pipeline.ports.signal_repository import SignalRepository
from trading_signal_pipeline.serialization.primitives import signal_event_from_dict, signal_event_to_dict
from trading_signal_pipeline.config.paths import DEFAULT_SIGNALS_PATH


class JsonlSignalRepository(SignalRepository):
    """
    File-backed signal repository (JSON Lines) for simple persistence.
    """

    def __init__(self, path: str = DEFAULT_SIGNALS_PATH):
        """
        Args:
            path: JSONL path for persistence.
        """
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

        self._seen: set[str] = set()
        self._signals: list[SignalEvent] = []
        if self.path.exists():
            for line in self.path.read_text(encoding="utf-8").splitlines():
                if not line.strip():
                    continue
                d = json.loads(line)
                event = signal_event_from_dict(d)
                self._signals.append(event)
                self._seen.add(event.idempotency_key)

    def is_duplicate(self, signal: SignalEvent) -> bool:
        """See SignalRepository."""
        return signal.idempotency_key in self._seen

    def add(self, signal: SignalEvent) -> None:
        """See SignalRepository."""
        if signal.idempotency_key in self._seen:
            return
        self._seen.add(signal.idempotency_key)
        self._signals.append(signal)
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(signal_event_to_dict(signal)) + "\n")

    def list(self) -> List[SignalEvent]:
        """See SignalRepository."""
        return list(self._signals)
