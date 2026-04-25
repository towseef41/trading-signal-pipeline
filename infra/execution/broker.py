from infra.execution.base import Broker


class MockBroker(Broker):
    """
    Simulates trade execution.
    """

    def execute(self, signal):
        return {
            "status": "filled",
            "symbol": signal.symbol,
            "side": signal.side,
            "qty": signal.qty,
            "price": signal.price,
        }