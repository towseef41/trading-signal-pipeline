"""
Broker execution port.

Application services call this port to execute a SignalEvent using a concrete
broker adapter (mock, paper trading, real broker).
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from trading_signal_pipeline.domain.execution import ExecutionResult
from trading_signal_pipeline.domain.signal import SignalEvent


class Broker(ABC):
    """
    Outbound port for order execution.
    """

    @abstractmethod
    def execute(self, signal: SignalEvent) -> ExecutionResult:
        """
        Execute a signal and return an execution result.

        Args:
            signal: SignalEvent to execute.

        Returns:
            ExecutionResult.
        """
        raise NotImplementedError
