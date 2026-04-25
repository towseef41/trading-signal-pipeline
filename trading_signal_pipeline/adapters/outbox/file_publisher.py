"""
Outbox publisher adapters.

FileOutboxPublisher appends DomainEvent objects to a JSONL file.
"""

from __future__ import annotations

import json
from pathlib import Path

from trading_signal_pipeline.domain.events import DomainEvent
from trading_signal_pipeline.ports.event_publisher import EventPublisher


class FileOutboxPublisher(EventPublisher):
    """
    Simple outbox: append events as JSON lines.
    """

    def __init__(self, path: str = "artifacts/outbox.jsonl"):
        """
        Args:
            path: JSONL file path to append events to.
        """
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def publish(self, event: DomainEvent) -> None:
        """Append the event to the outbox JSONL file."""
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(event.__dict__) + "\n")
