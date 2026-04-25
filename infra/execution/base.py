from abc import ABC, abstractmethod


class Broker(ABC):
    """
    Abstract broker interface.
    """

    @abstractmethod
    def execute(self, signal):
        pass