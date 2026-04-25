from fastapi.testclient import TestClient

from api.v1.app import app
from api.v1.dependencies import get_signal_store, get_broker


# ----------------------------
# Mock Implementations
# ----------------------------

class MockStore:
    def __init__(self):
        self.data = []
        self.seen = set()

    def _key(self, signal):
        return (signal.symbol, signal.side, signal.price)

    def is_duplicate(self, signal):
        return self._key(signal) in self.seen

    def add(self, signal):
        key = self._key(signal)
        self.seen.add(key)
        self.data.append(signal)


class MockBroker:
    def execute(self, signal):
        return {
            "status": "mocked",
            "symbol": signal.symbol,
            "side": signal.side,
            "qty": signal.qty,
            "price": signal.price,
        }


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

    response = client.post("/v1/webhook", json=payload)

    assert response.status_code == 200
    data = response.json()

    assert data["message"] == "Signal processed"
    assert data["execution"]["status"] == "mocked"


def test_webhook_validation_error():
    payload = {
        "symbol": "AAPL",
        "side": "BUY",
        "qty": -10,  # invalid
        "price": 150
    }

    response = client.post("/v1/webhook", json=payload)

    assert response.status_code == 422


def test_duplicate_signal():
    payload = {
        "symbol": "AAPL",
        "side": "BUY",
        "qty": 10,
        "price": 150
    }

    # First request
    response1 = client.post("/v1/webhook", json=payload)
    assert response1.status_code == 200

    # Duplicate request (same store instance now)
    response2 = client.post("/v1/webhook", json=payload)
    assert response2.status_code == 400
    assert response2.json()["detail"] == "Duplicate signal"


def test_missing_fields():
    payload = {
        "symbol": "AAPL",
        "side": "BUY"
        # missing qty, price
    }

    response = client.post("/v1/webhook", json=payload)

    assert response.status_code == 422


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"