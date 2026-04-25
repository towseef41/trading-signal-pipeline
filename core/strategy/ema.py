import pandas as pd

from core.strategy.base import Strategy
from core.models.signal import SignalType


class EMACrossoverStrategy(Strategy):
    """
    Exponential Moving Average (EMA) crossover strategy.

    Generates signals when short EMA crosses long EMA.

    BUY  → short EMA crosses above long EMA
    SELL → short EMA crosses below long EMA
    HOLD → otherwise
    """

    def __init__(self, short_window: int = 9, long_window: int = 21):
        self.short_window = short_window
        self.long_window = long_window

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Generate trading signals based on EMA crossover.

        Parameters
        ----------
        data : pd.DataFrame
            Must contain 'Close' column

        Returns
        -------
        pd.DataFrame
            Original data with:
            - ema_short
            - ema_long
            - signal (SignalType)
        """
        df = data.copy()

        if "Close" not in df.columns:
            raise ValueError("Input data must contain 'Close' column")

        # EMA calculations
        df["ema_short"] = df["Close"].ewm(span=self.short_window, adjust=False).mean()
        df["ema_long"] = df["Close"].ewm(span=self.long_window, adjust=False).mean()

        # Initialize signals
        df["signal"] = SignalType.HOLD

        # Prevent lookahead bias
        prev_short = df["ema_short"].shift(1)
        prev_long = df["ema_long"].shift(1)

        # Crossover logic
        buy = (prev_short <= prev_long) & (df["ema_short"] > df["ema_long"])
        sell = (prev_short >= prev_long) & (df["ema_short"] < df["ema_long"])

        df.loc[buy, "signal"] = SignalType.BUY
        df.loc[sell, "signal"] = SignalType.SELL

        return df