from __future__ import annotations
from typing import Dict, List, Optional

from models.menu_item import MenuItem
from models.table import Table, OCCUPIED
from models.customer import Customer
from models.order import Order, OPEN, PAID
from models.payment import Payment
from models.discount import Discount

from exceptions import (
    MenuItemNotFoundError,
    TableNotFoundError,
    CustomerNotFoundError,
    OrderNotFoundError,
    ValidationError,
)


class Restaurant:

    def __init__(self, name: str = "My Restaurant") -> None:
        self.name: str = name
        self.menu: Dict[int, MenuItem] = {}
        self.tables: Dict[int, Table] = {}
        self.customers: Dict[int, Customer] = {}
        self.orders: Dict[int, Order] = {}
        self.payments: List[Payment] = []

        self._next_menu_id: int = 1
        self._next_table_id: int = 1
        self._next_customer_id: int = 1
        self._next_order_id: int = 1
        self._next_payment_id: int = 1

    def add_menu_item(self, name: str, category: str, price: float) -> MenuItem:
        if not name.strip():
            raise ValidationError("Menu item name cannot be empty.")
        item = MenuItem(self._next_menu_id, name.strip(), category.strip(), price)
        self.menu[item.item_id] = item
        self._next_menu_id += 1
        return item

    def update_menu_item(self, item_id: int, name: str = None, category: str = None,
                          price: float = None, available: bool = None) -> MenuItem:
        item = self.get_menu_item(item_id)
        if name is not None:
            item.name = name.strip()
        if category is not None:
            item.category = category.strip()
        if price is not None:
            item.price = price
        if available is not None:
            item.available = available
        return item

    def delete_menu_item(self, item_id: int) -> None:
        if item_id not in self.menu:
            raise MenuItemNotFoundError(f"Menu item {item_id} does not exist.")
        del self.menu[item_id]

    def get_menu_item(self, item_id: int) -> MenuItem:
        if item_id not in self.menu:
            raise MenuItemNotFoundError(f"Menu item {item_id} does not exist.")
        return self.menu[item_id]

    def search_menu(self, keyword: str) -> List[MenuItem]:
        return [item for item in self.menu.values() if item.matches(keyword)]

    def filter_menu(self, category: Optional[str] = None, available: Optional[bool] = None) -> List[MenuItem]:
        results = list(self.menu.values())
        if category:
            results = [i for i in results if i.category.lower() == category.lower()]
        if available is not None:
            results = [i for i in results if i.available == available]
        return results


        
    def add_table(self, capacity: int) -> Table:
        table = Table(self._next_table_id, capacity)
        self.tables[table.table_id] = table
        self._next_table_id += 1
        return table

    def delete_table(self, table_id: int) -> None:
        if table_id not in self.tables:
            raise TableNotFoundError(f"Table {table_id} does not exist.")
        del self.tables[table_id]

    def get_table(self, table_id: int) -> Table:
        if table_id not in self.tables:
            raise TableNotFoundError(f"Table {table_id} does not exist.")
        return self.tables[table_id]

    def filter_tables(self, status: Optional[str] = None) -> List[Table]:
        if status is None:
            return list(self.tables.values())
        return [t for t in self.tables.values() if t.status == status]




    def add_customer(self, name: str, phone: str = "") -> Customer:
        if not name.strip():
            raise ValidationError("Customer name cannot be empty.")
        customer = Customer(self._next_customer_id, name.strip(), phone.strip())
        self.customers[customer.customer_id] = customer
        self._next_customer_id += 1
        return customer

    def update_customer(self, customer_id: int, name: str = None, phone: str = None) -> Customer:
        customer = self.get_customer(customer_id)
        if name is not None:
            customer.name = name.strip()
        if phone is not None:
            customer.phone = phone.strip()
        return customer

    def delete_customer(self, customer_id: int) -> None:
        if customer_id not in self.customers:
            raise CustomerNotFoundError(f"Customer {customer_id} does not exist.")
        del self.customers[customer_id]

    def get_customer(self, customer_id: int) -> Customer:
        if customer_id not in self.customers:
            raise CustomerNotFoundError(f"Customer {customer_id} does not exist.")
        return self.customers[customer_id]

    def search_customers(self, keyword: str) -> List[Customer]:
        return [c for c in self.customers.values() if c.matches(keyword)]




    def create_order(self, table_id: int, customer_id: Optional[int] = None) -> Order:
        table = self.get_table(table_id)
        if customer_id is not None:
            self.get_customer(customer_id)

        table.occupy()
        order = Order(self._next_order_id, table_id, customer_id)
        self.orders[order.order_id] = order
        self._next_order_id += 1
        return order

    def get_order(self, order_id: int) -> Order:
        if order_id not in self.orders:
            raise OrderNotFoundError(f"Order {order_id} does not exist.")
        return self.orders[order_id]

    def add_item_to_order(self, order_id: int, item_id: int, quantity: int) -> Order:
        order = self.get_order(order_id)
        menu_item = self.get_menu_item(item_id)
        order.add_item(menu_item, quantity)
        return order

    def remove_item_from_order(self, order_id: int, item_id: int) -> Order:
        order = self.get_order(order_id)
        order.remove_item(item_id)
        return order

    def apply_discount(self, order_id: int, discount: Discount) -> Order:
        order = self.get_order(order_id)
        order.discount = discount
        return order

    def checkout_order(self, order_id: int, method: str = "Cash") -> Payment:
        order = self.get_order(order_id)
        total = order.checkout()
        payment = Payment(self._next_payment_id, order_id, total, method)
        self.payments.append(payment)
        self._next_payment_id += 1
        self.get_table(order.table_id).free() 
        return payment

    def cancel_order(self, order_id: int) -> Order:
        order = self.get_order(order_id)
        order.cancel()
        self.get_table(order.table_id).free()
        return order

    def filter_orders(self, status: Optional[str] = None) -> List[Order]:
        if status is None:
            return list(self.orders.values())
        return [o for o in self.orders.values() if o.status == status]

    def search_orders(self, keyword: str) -> List[Order]:
        keyword = keyword.strip()
        results = []
        for order in self.orders.values():
            if keyword == str(order.order_id) or keyword == str(order.table_id):
                results.append(order)
        return results




    def dashboard_stats(self) -> Dict[str, object]:
        total_tables = len(self.tables)
        occupied = len(self.filter_tables(OCCUPIED))
        open_orders = len(self.filter_orders(OPEN))
        paid_orders = len(self.filter_orders(PAID))
        total_revenue = round(sum(p.amount for p in self.payments), 2)
        available_menu_items = len(self.filter_menu(available=True))

        return {
            "Total Tables": total_tables,
            "Occupied Tables": occupied,
            "Available Tables": total_tables - occupied,
            "Total Menu Items": len(self.menu),
            "Available Menu Items": available_menu_items,
            "Open Orders": open_orders,
            "Paid Orders": paid_orders,
            "Total Customers": len(self.customers),
            "Total Revenue": total_revenue,
        }

    def daily_sales_report(self, date: str) -> List[Payment]:
        """date format: 'YYYY-MM-DD'."""
        return [p for p in self.payments if p.timestamp.startswith(date)]
