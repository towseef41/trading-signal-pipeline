from abc import ABC, abstractmethod


class SignalStore(ABC):
    """
    Abstract interface for signal storage.
    """

    @abstractmethod
    def is_duplicate(self, signal) -> bool:
        pass

    @abstractmethod
    def add(self, signal) -> None:
        pass