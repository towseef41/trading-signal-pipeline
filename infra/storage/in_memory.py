from infra.storage.base import SignalStore


class InMemorySignalStore(SignalStore):
    """
    In-memory implementation of SignalStore.
    """

    def __init__(self):
        self.signals = []
        self.seen = set()

    def _key(self, signal):
        return (signal.symbol, signal.side, signal.price)

    def is_duplicate(self, signal) -> bool:
        return self._key(signal) in self.seen

    def add(self, signal) -> None:
        key = self._key(signal)
        self.seen.add(key)
        self.signals.append(signal)