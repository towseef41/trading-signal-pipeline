from abc import ABC, abstractmethod
import pandas as pd


class Strategy(ABC):
    """
    Abstract base class for trading strategies.

    Contract
    --------
    Input:
        DataFrame with at least 'Close' column

    Output:
        DataFrame with additional 'signal' column using SignalType values

    Notes
    -----
    - Must be deterministic
    - Must not introduce lookahead bias
    - Must not perform I/O operations
    """

    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        pass