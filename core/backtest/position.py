from dataclasses import dataclass
from typing import Optional


@dataclass
class Position:
    is_open: bool = False
    entry_price: Optional[float] = None
    entry_time: Optional[object] = None