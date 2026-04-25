"""
Signal repository port.

This port abstracts persistence of ingested SignalEvent objects.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List

from trading_signal_pipeline.domain.signal import SignalEvent


class SignalRepository(ABC):
    """
    Inbound persistence port for ingested signals.
    """

    @abstractmethod
    def is_duplicate(self, signal: SignalEvent) -> bool:
        """
        Check if the signal was already ingested.

        Args:
            signal: SignalEvent.

        Returns:
            True if the event should be considered a duplicate.
        """
        raise NotImplementedError

    @abstractmethod
    def add(self, signal: SignalEvent) -> None:
        """
        Persist a signal event.

        Args:
            signal: SignalEvent to persist.
        """
        raise NotImplementedError

    @abstractmethod
    def list(self) -> List[SignalEvent]:
        """
        Return all ingested signals.

        Returns:
            Signals in insertion order.
        """
        raise NotImplementedError
