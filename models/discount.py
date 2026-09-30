from __future__ import annotations
from abc import ABC, abstractmethod

from exceptions import ValidationError


class Discount(ABC):
    @abstractmethod
    def apply(self, total: float) -> float:
        """Return the total after the discount has been applied."""

    @abstractmethod
    def describe(self) -> str:
        """A short, human-readable description of the discount."""


class NoDiscount(Discount):

    def apply(self, total: float) -> float:
        return total

    def describe(self) -> str:
        return "No discount"


class PercentageDiscount(Discount):
    """Reduces the total by a percentage."""

    def __init__(self, percent: float) -> None:
        if not (0 < percent <= 100):
            raise ValidationError("Percentage discount must be between 0 and 100.")
        self.percent: float = percent

    def apply(self, total: float) -> float:
        return round(total * (1 - self.percent / 100), 2)

    def describe(self) -> str:
        return f"{self.percent:.0f}% off"


class FixedAmountDiscount(Discount):
    """Reduces the total by a fixed dollar amount."""

    def __init__(self, amount: float) -> None:
        if amount <= 0:
            raise ValidationError("Fixed discount amount must be greater than zero.")
        self.amount: float = amount

    def apply(self, total: float) -> float:
        return max(0.0, round(total - self.amount, 2))

    def describe(self) -> str:
        return f"${self.amount:.2f} off"
