from functools import lru_cache

from infra.storage.base import SignalStore
from infra.storage.in_memory import InMemorySignalStore
from infra.execution.base import Broker
from infra.execution.broker import MockBroker


@lru_cache
def get_signal_store() -> SignalStore:
    return InMemorySignalStore()


@lru_cache
def get_broker() -> Broker:
    return MockBroker()