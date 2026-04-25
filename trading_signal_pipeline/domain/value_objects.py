"""
Domain value objects.

These types enforce basic invariants (non-empty symbols, positive prices/quantities)
and make intent explicit throughout the domain model.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Symbol:
    """Ticker/asset identifier (stored normalized as uppercase)."""

    value: str

    def __post_init__(self) -> None:
        """Normalize and validate the symbol."""
        v = (self.value or "").strip().upper()
        if not v:
            raise ValueError("Symbol must be non-empty")
        object.__setattr__(self, "value", v)

    def __str__(self) -> str:
        """Return the normalized symbol string."""
        return self.value


@dataclass(frozen=True)
class Price:
    """Positive price value object."""

    value: float

    def __post_init__(self) -> None:
        """Validate price is strictly positive."""
        if self.value <= 0:
            raise ValueError("Price must be > 0")

    def __float__(self) -> float:
        """Return the underlying float value."""
        return float(self.value)


@dataclass(frozen=True)
class Quantity:
    """Positive quantity value object."""

    value: float

    def __post_init__(self) -> None:
        """Validate quantity is strictly positive."""
        if self.value <= 0:
            raise ValueError("Quantity must be > 0")

    def __float__(self) -> float:
        """Return the underlying float value."""
        return float(self.value)


@dataclass(frozen=True)
class Volume:
    """Non-negative volume value object."""

    value: float

    def __post_init__(self) -> None:
        """Validate volume is non-negative."""
        if self.value < 0:
            raise ValueError("Volume must be >= 0")

    def __float__(self) -> float:
        """Return the underlying float value."""
        return float(self.value)
