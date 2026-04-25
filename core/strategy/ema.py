import pandas as pd
from core.strategy.base import Strategy


class EMACrossoverStrategy(Strategy):
    """
    Exponential Moving Average (EMA) crossover strategy.

    This strategy generates trading signals based on the crossover of two EMAs:
    - A short-term EMA (fast-moving)
    - A long-term EMA (slow-moving)

    Signal generation logic:
    - BUY (1): When the short EMA crosses above the long EMA
    - SELL (-1): When the short EMA crosses below the long EMA
    - HOLD (0): Otherwise

    Notes
    -----
    - Signals are generated using previous values to avoid lookahead bias.
    - Only crossover points generate signals (not continuous trend following).
    """

    def __init__(self, short_window: int = 9, long_window: int = 21):
        """
        Initialize the EMA crossover strategy.

        Parameters
        ----------
        short_window : int, optional
            Window size for the short-term EMA (default is 9).
        long_window : int, optional
            Window size for the long-term EMA (default is 21).
        """
        self.short_window = short_window
        self.long_window = long_window

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Compute EMA crossover signals for the given market data.

        Parameters
        ----------
        data : pd.DataFrame
            Time-indexed OHLCV data containing at least the 'Close' column.

        Returns
        -------
        pd.DataFrame
            DataFrame with added columns:
            - 'ema_short': short-term EMA
            - 'ema_long': long-term EMA
            - 'signal': trading signal (1, -1, 0)

        Raises
        ------
        ValueError
            If the required 'Close' column is missing.

        Behavior
        --------
        - Signals are triggered only on crossover events.
        - Uses previous timestep values to prevent lookahead bias.
        """
        df = data.copy()

        if "Close" not in df.columns:
            raise ValueError("Input data must contain 'Close' column")

        df["ema_short"] = df["Close"].ewm(span=self.short_window, adjust=False).mean()
        df["ema_long"] = df["Close"].ewm(span=self.long_window, adjust=False).mean()

        df["signal"] = 0

        prev_short = df["ema_short"].shift(1)
        prev_long = df["ema_long"].shift(1)

        buy_signal = (prev_short <= prev_long) & (df["ema_short"] > df["ema_long"])
        sell_signal = (prev_short >= prev_long) & (df["ema_short"] < df["ema_long"])

        df.loc[buy_signal, "signal"] = 1
        df.loc[sell_signal, "signal"] = -1

        return df