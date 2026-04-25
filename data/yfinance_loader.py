import pandas as pd
import yfinance as yf

from data.base import MarketDataLoader


class YFinanceDataLoader(MarketDataLoader):
    """
    Loads OHLCV data using yfinance.
    """

    def load(
        self,
        symbol: str,
        start: str = "2022-01-01",
        end: str = "2023-01-01",
        interval: str = "1d",
    ) -> pd.DataFrame:
        df = yf.download(
            symbol,
            start=start,
            end=end,
            interval=interval,
        )

        if df.empty:
            raise ValueError(f"No data found for {symbol}")

        return df