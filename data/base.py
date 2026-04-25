from abc import ABC, abstractmethod
import pandas as pd


class MarketDataLoader(ABC):
    """
    Interface for loading market OHLCV data.
    """

    @abstractmethod
    def load(
        self,
        symbol: str,
        start: str,
        end: str,
        interval: str,
    ) -> pd.DataFrame:
        """
        Load OHLCV data.

        Returns
        -------
        pd.DataFrame
            Data containing at least:
            Open, High, Low, Close, Volume
        """
        pass