from fastapi.testclient import TestClient

from trading_signal_pipeline.interfaces.api.v1.app import app
from trading_signal_pipeline.interfaces.api.v1.dependencies import get_signal_store, get_broker, get_event_publisher
from trading_signal_pipeline.interfaces.api.v1.auth import require_api_key
from trading_signal_pipeline.domain.execution import ExecutionResult


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

class MockPublisher:
    def __init__(self):
        self.events = []

    def publish(self, event):
        self.events.append(event)


# ----------------------------
# Test Setup (IMPORTANT FIX)
# ----------------------------

def setup_function():
    """
    Reset dependencies before each test to ensure isolation.
    """
    mock_store = MockStore()
    mock_publisher = MockPublisher()

    app.dependency_overrides[get_signal_store] = lambda: mock_store
    app.dependency_overrides[get_broker] = lambda: MockBroker()
    app.dependency_overrides[get_event_publisher] = lambda: mock_publisher
    app.dependency_overrides[require_api_key] = lambda: None

    # Expose publisher for tests that need it.
    setup_function.mock_publisher = mock_publisher


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

    assert data["data"]["signal"]["symbol"] == "AAPL"
    assert data["data"]["signal"]["side"] == "BUY"
    assert data["data"]["signal"]["idempotency_key"]
    assert data["data"]["execution"]["status"] == "filled"
    assert response.headers.get("X-Request-Id")


def test_webhook_validation_error():
    payload = {
        "symbol": "AAPL",
        "side": "BUY",
        "qty": -10,  # invalid
        "price": 150
    }

    response = client.post("/v1/signals", json=payload, headers={"X-API-Key": "test"})

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"


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
    assert response2.json()["error"]["code"] == "duplicate_signal"
    assert response2.json()["error"]["message"] == "Duplicate signal"


def test_request_id_propagates_to_outbox_correlation_id():
    payload = {"symbol": "AAPL", "side": "BUY", "qty": 10, "price": 150}
    req_id = "req-test-123"
    response = client.post(
        "/v1/signals",
        json=payload,
        headers={"X-API-Key": "test", "X-Request-Id": req_id},
    )
    assert response.status_code == 200
    assert response.headers.get("X-Request-Id") == req_id

    publisher = setup_function.mock_publisher
    names = [e.name for e in publisher.events]
    assert "signal.ingested" in names
    assert "signal.executed" in names
    assert all(e.correlation_id == req_id for e in publisher.events)


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


def test_report_requires_auth():
    # Remove auth override for this test only.
    if require_api_key in app.dependency_overrides:
        del app.dependency_overrides[require_api_key]

    try:
        response = client.get("/v1/report/")
        assert response.status_code == 500
        body = response.json()
        assert body["error"]["code"] == "server_misconfigured"
    finally:
        app.dependency_overrides[require_api_key] = lambda: None


def test_report_response_envelope():
    response = client.get("/v1/report/", headers={"X-API-Key": "test"})
    assert response.status_code == 200
    body = response.json()
    assert "data" in body
    assert "performance" in body["data"]
    assert "trades_summary" in body["data"]
    assert "signals_summary" in body["data"]
