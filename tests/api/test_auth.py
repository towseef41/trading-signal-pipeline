import pytest
from fastapi import HTTPException

from trading_signal_pipeline.interfaces.api.v1.auth import require_api_key


def test_require_api_key_500_when_server_misconfigured(monkeypatch):
    monkeypatch.delenv("PIPELINE_API_KEY", raising=False)
    with pytest.raises(HTTPException) as exc:
        require_api_key(x_api_key="anything")
    assert exc.value.status_code == 500


def test_require_api_key_401_when_missing_header(monkeypatch):
    monkeypatch.setenv("PIPELINE_API_KEY", "secret")
    with pytest.raises(HTTPException) as exc:
        require_api_key(x_api_key=None)
    assert exc.value.status_code == 401


def test_require_api_key_401_when_invalid(monkeypatch):
    monkeypatch.setenv("PIPELINE_API_KEY", "secret")
    with pytest.raises(HTTPException) as exc:
        require_api_key(x_api_key="wrong")
    assert exc.value.status_code == 401


def test_require_api_key_allows_valid(monkeypatch):
    monkeypatch.setenv("PIPELINE_API_KEY", "secret")
    # Should not raise.
    require_api_key(x_api_key="secret")
