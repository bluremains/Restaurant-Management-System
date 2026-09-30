from __future__ import annotations
from datetime import datetime
from typing import Dict, Any, List, Optional

from models.menu_item import MenuItem
from models.discount import Discount, NoDiscount
from exceptions import InvalidQuantityError, EmptyOrderError, MenuItemUnavailableError

OPEN = "Open"
PAID = "Paid"
CANCELLED = "Cancelled"


class OrderItem:

    def __init__(self, menu_item: MenuItem, quantity: int) -> None:
        if quantity <= 0:
            raise InvalidQuantityError("Quantity must be greater than zero.")
        self.menu_item: MenuItem = menu_item
        self.quantity: int = quantity

    @property
    def subtotal(self) -> float:
        return round(self.menu_item.price * self.quantity, 2)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item_id": self.menu_item.item_id,
            "name": self.menu_item.name,
            "unit_price": self.menu_item.price,
            "quantity": self.quantity,
        }

    def __str__(self) -> str:
        return f"{self.quantity} x {self.menu_item.name} = ${self.subtotal:.2f}"


class Order:
    """An order placed by a customer at a table."""

    def __init__(
        self,
        order_id: int,
        table_id: int,
        customer_id: Optional[int] = None,
        status: str = OPEN,
        created_at: Optional[str] = None,
        discount: Optional[Discount] = None,
    ) -> None:
        self.order_id: int = order_id
        self.table_id: int = table_id
        self.customer_id: Optional[int] = customer_id
        self.items: List[OrderItem] = []
        self.status: str = status
        self.created_at: str = created_at or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.discount: Discount = discount or NoDiscount()

    @property
    def is_empty(self) -> bool:
        return len(self.items) == 0

    def add_item(self, menu_item: MenuItem, quantity: int) -> None:
        if not menu_item.available:
            raise MenuItemUnavailableError(f"'{menu_item.name}' is currently unavailable.")
        for line in self.items:
            if line.menu_item.item_id == menu_item.item_id:
                line.quantity += quantity
                return
        self.items.append(OrderItem(menu_item, quantity))

    def remove_item(self, item_id: int) -> None:
        self.items = [line for line in self.items if line.menu_item.item_id != item_id]

    def calculate_subtotal(self) -> float:
        return round(sum(line.subtotal for line in self.items), 2)

    def calculate_total(self) -> float:
        return round(self.discount.apply(self.calculate_subtotal()), 2)

    def checkout(self) -> float:
        if self.is_empty:
            raise EmptyOrderError(f"Order {self.order_id} has no items and cannot be checked out.")
        self.status = PAID
        return self.calculate_total()

    def cancel(self) -> None:
        self.status = CANCELLED

    def to_dict(self) -> Dict[str, Any]:
        discount_data: Dict[str, Any] = {"type": self.discount.__class__.__name__}
        discount_data.update(getattr(self.discount, "__dict__", {}))
        return {
            "order_id": self.order_id,
            "table_id": self.table_id,
            "customer_id": self.customer_id,
            "status": self.status,
            "created_at": self.created_at,
            "items": [line.to_dict() for line in self.items],
            "discount": discount_data,
        }

    def __str__(self) -> str:
        return f"Order #{self.order_id} (Table {self.table_id}) - {self.status} - Total: ${self.calculate_total():.2f}"
