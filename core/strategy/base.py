from abc import ABC, abstractmethod
import pandas as pd


class Strategy(ABC):
    """
    Abstract base class for trading strategies.

    A Strategy defines the logic for generating trading signals based on
    historical market data. Implementations must be deterministic and
    operate only on the provided input data (no external side effects).

    The output must include a 'signal' column indicating trading actions:
        1  -> BUY
       -1  -> SELL
        0  -> HOLD
    """

    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Generate trading signals from OHLCV market data.

        Parameters
        ----------
        data : pd.DataFrame
            Time-indexed DataFrame containing market data.
            Must include at least the 'Close' column.

        Returns
        -------
        pd.DataFrame
            A copy of the input DataFrame with an additional 'signal' column.

        Raises
        ------
        ValueError
            If required columns are missing from the input data.
        """
        pass