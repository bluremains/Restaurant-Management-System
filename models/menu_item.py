from __future__ import annotations
from typing import Dict, Any

from exceptions import ValidationError


class MenuItem:
    """A single item that can be ordered (e.g. 'Margherita Pizza')."""

    def __init__(self, item_id: int, name: str, category: str, price: float, available: bool = True) -> None:
        self.item_id: int = item_id
        self.name: str = name
        self.category: str = category
        self.__price: float = 0.0     
        self.price = price
        self.available: bool = available

    @property
    def price(self) -> float:
        return self.__price

    @price.setter
    def price(self, value: float) -> None:
        if value <= 0:
            raise ValidationError("Menu item price must be greater than zero.")
        self.__price = round(float(value), 2)

    def mark_available(self) -> None:
        self.available = True

    def mark_unavailable(self) -> None:
        self.available = False

    def matches(self, keyword: str) -> bool:
        """Used for search-by-name/category."""
        keyword = keyword.lower().strip()
        return keyword in self.name.lower() or keyword in self.category.lower()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item_id": self.item_id,
            "name": self.name,
            "category": self.category,
            "price": self.price,
            "available": self.available,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MenuItem":
        return cls(
            item_id=data["item_id"],
            name=data["name"],
            category=data["category"],
            price=data["price"],
            available=data.get("available", True),
        )

    def __str__(self) -> str:
        status = "Available" if self.available else "Unavailable"
        return f"[{self.item_id}] {self.name} ({self.category}) - ${self.price:.2f} - {status}"
