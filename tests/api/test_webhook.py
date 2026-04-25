from fastapi.testclient import TestClient

from trading_signal_pipeline.interfaces.api.v1.app import app
from trading_signal_pipeline.interfaces.api.v1.dependencies import get_signal_store, get_broker, get_event_publisher
from trading_signal_pipeline.interfaces.api.v1.auth import require_api_key
from trading_signal_pipeline.domain.execution import ExecutionResult
from trading_signal_pipeline.adapters.outbox.noop_publisher import NoOpEventPublisher


# ----------------------------
# Mock Implementations
# ----------------------------

class MockStore:
    def __init__(self):
        self.data = []
        self.seen = set()

    def is_duplicate(self, signal):
        return signal.idempotency_key in self.seen

    def add(self, signal):
        self.seen.add(signal.idempotency_key)
        self.data.append(signal)

    def list(self):
        return list(self.data)


class MockBroker:
    def execute(self, signal):
        return ExecutionResult(
            status="filled",
            symbol=signal.symbol,
            side=signal.side,
            qty=signal.qty,
            price=signal.price,
        )


# ----------------------------
# Test Setup (IMPORTANT FIX)
# ----------------------------

def setup_function():
    """
    Reset dependencies before each test to ensure isolation.
    """
    mock_store = MockStore()

    app.dependency_overrides[get_signal_store] = lambda: mock_store
    app.dependency_overrides[get_broker] = lambda: MockBroker()
    app.dependency_overrides[get_event_publisher] = lambda: NoOpEventPublisher()
    app.dependency_overrides[require_api_key] = lambda: None


client = TestClient(app)


# ----------------------------
# Tests
# ----------------------------

def test_webhook_success():
    payload = {
        "symbol": "AAPL",
        "side": "BUY",
        "qty": 10,
        "price": 150
    }

    response = client.post("/v1/signals", json=payload, headers={"X-API-Key": "test"})

    assert response.status_code == 200
    data = response.json()

    assert data["message"] == "Signal processed"
    assert data["execution"]["status"] == "filled"


def test_webhook_validation_error():
    payload = {
        "symbol": "AAPL",
        "side": "BUY",
        "qty": -10,  # invalid
        "price": 150
    }

    response = client.post("/v1/signals", json=payload, headers={"X-API-Key": "test"})

    assert response.status_code == 422


def test_duplicate_signal():
    payload = {
        "symbol": "AAPL",
        "side": "BUY",
        "qty": 10,
        "price": 150
    }

    # First request
    response1 = client.post("/v1/signals", json=payload, headers={"X-API-Key": "test"})
    assert response1.status_code == 200

    # Duplicate request (same store instance now)
    response2 = client.post("/v1/signals", json=payload, headers={"X-API-Key": "test"})
    assert response2.status_code == 400
    assert response2.json()["detail"] == "Duplicate signal"


def test_missing_fields():
    payload = {
        "symbol": "AAPL",
        "side": "BUY"
        # missing qty, price
    }

    response = client.post("/v1/signals", json=payload, headers={"X-API-Key": "test"})

    assert response.status_code == 422


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
