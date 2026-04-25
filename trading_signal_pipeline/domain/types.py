"""
Small shared domain types.

Kept separate to avoid circular imports between domain modules.
"""

from __future__ import annotations

from typing import Literal


Side = Literal["BUY", "SELL"]
