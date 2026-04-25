"""
Broker adapters.

This module contains a mock broker used for development/testing.
"""

from trading_signal_pipeline.domain.execution import ExecutionResult
from trading_signal_pipeline.domain.signal import SignalEvent
from trading_signal_pipeline.ports.broker import Broker


class MockBroker(Broker):
    """
    Simulates trade execution.
    """

    def execute(self, signal: SignalEvent) -> ExecutionResult:
        """
        Execute a signal and return a filled result.

        Args:
            signal: SignalEvent.

        Returns:
            ExecutionResult with status="filled".
        """
        return ExecutionResult(
            status="filled",
            symbol=signal.symbol,
            side=signal.side,
            qty=signal.qty,
            price=signal.price,
        )
