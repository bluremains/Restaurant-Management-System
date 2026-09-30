from __future__ import annotations
from typing import Any, Dict

from file_manager.file_manager import FileManager
from models.restaurant import Restaurant
from models.menu_item import MenuItem
from models.table import Table
from models.customer import Customer
from models.order import Order, OrderItem
from models.payment import Payment
from models.discount import Discount, NoDiscount, PercentageDiscount, FixedAmountDiscount


class RestaurantService:
    """Loads a Restaurant from disk on startup and saves it back on demand."""

    def __init__(self, file_path: str = "data/restaurant_data.json") -> None:
        self.file_manager = FileManager(file_path)

    def load(self) -> Restaurant:
        data = self.file_manager.load()
        if not data:
            return Restaurant()
        return self._from_dict(data)

    def save(self, restaurant: Restaurant) -> None:
        self.file_manager.save(self._to_dict(restaurant))

    @staticmethod
    def _discount_from_dict(data: Dict[str, Any]) -> Discount:
        kind = data.get("type", "NoDiscount")
        if kind == "PercentageDiscount":
            return PercentageDiscount(data["percent"])
        if kind == "FixedAmountDiscount":
            return FixedAmountDiscount(data["amount"])
        return NoDiscount()

    def _to_dict(self, restaurant: Restaurant) -> Dict[str, Any]:
        return {
            "name": restaurant.name,
            "next_ids": {
                "menu": restaurant._next_menu_id,
                "table": restaurant._next_table_id,
                "customer": restaurant._next_customer_id,
                "order": restaurant._next_order_id,
                "payment": restaurant._next_payment_id,
            },
            "menu": [item.to_dict() for item in restaurant.menu.values()],
            "tables": [table.to_dict() for table in restaurant.tables.values()],
            "customers": [c.to_dict() for c in restaurant.customers.values()],
            "orders": [order.to_dict() for order in restaurant.orders.values()],
            "payments": [p.to_dict() for p in restaurant.payments],
        }

    def _from_dict(self, data: Dict[str, Any]) -> Restaurant:
        restaurant = Restaurant(name=data.get("name", "My Restaurant"))

        for item_data in data.get("menu", []):
            item = MenuItem.from_dict(item_data)
            restaurant.menu[item.item_id] = item

        for table_data in data.get("tables", []):
            table = Table.from_dict(table_data)
            restaurant.tables[table.table_id] = table

        for cust_data in data.get("customers", []):
            customer = Customer.from_dict(cust_data)
            restaurant.customers[customer.customer_id] = customer

        for order_data in data.get("orders", []):
            order = Order(
                order_id=order_data["order_id"],
                table_id=order_data["table_id"],
                customer_id=order_data.get("customer_id"),
                status=order_data.get("status", "Open"),
                created_at=order_data.get("created_at"),
                discount=self._discount_from_dict(order_data.get("discount", {})),
            )
            for line_data in order_data.get("items", []):
                menu_item = restaurant.menu.get(line_data["item_id"])
                if menu_item is not None:
                    order.items.append(OrderItem(menu_item, line_data["quantity"]))
            restaurant.orders[order.order_id] = order

        for pay_data in data.get("payments", []):
            restaurant.payments.append(Payment.from_dict(pay_data))

        next_ids = data.get("next_ids", {})
        restaurant._next_menu_id = next_ids.get("menu", len(restaurant.menu) + 1)
        restaurant._next_table_id = next_ids.get("table", len(restaurant.tables) + 1)
        restaurant._next_customer_id = next_ids.get("customer", len(restaurant.customers) + 1)
        restaurant._next_order_id = next_ids.get("order", len(restaurant.orders) + 1)
        restaurant._next_payment_id = next_ids.get("payment", len(restaurant.payments) + 1)

        return restaurant
