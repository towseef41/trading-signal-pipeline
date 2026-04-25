# core/models/signal.py

from enum import IntEnum


class SignalType(IntEnum):
    """
    Represents discrete trading signals.

    Values
    ------
    BUY  = 1
    SELL = -1
    HOLD = 0

    Notes
    -----
    This enum defines the contract between strategy and execution layers.
    All strategies must output signals using these values.
    """

    BUY = 1
    SELL = -1
    HOLD = 0