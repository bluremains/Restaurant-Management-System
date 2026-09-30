# Restaurant Management System

## Project Name
Restaurant Management System — OOP Final Project

## Developed By
Yomn Osama Ibrahim

## Project Description
A desktop application for managing a small restaurant's day-to-day
operations: tables, menu, customers and orders. Built in Python using
Object-Oriented Programming, with a Tkinter GUI and JSON file
persistence (no database required).

## Main Features
- Manage tables (add/delete, see Available/Occupied status)
- Manage the menu (add/update/delete items, mark available/unavailable)
- Manage customers (add/update/delete)
- Create orders, add/remove items, apply discounts
- Checkout an order (creates a payment, frees the table)
- Cancel an open order (frees the table)
- Search menu items and customers by keyword
- Filter tables by status, menu items by category/availability, orders by status
- Live dashboard with real, non-hard-coded statistics
- Data is loaded on startup and saved automatically when the app closes

## Classes
`MenuItem` | A dish/drink: name, category, price (validated), availability |
`Table` | A physical table: capacity and Available/Occupied status |
`Customer` | A guest: name and phone number |
`Discount` (ABC) | Abstract contract for discount strategies |
`NoDiscount`, `PercentageDiscount`, `FixedAmountDiscount` | Concrete discount implementations |
`OrderItem` | One line of an order: a `MenuItem` + quantity |
`Order` | A customer's order: items, status, discount, total calculation |
`Payment` | A record of money received for a checked-out order |
`Restaurant` | Composition root: owns all collections, exposes CRUD/search/filter/business rules/dashboard |
`FileManager` | Reads and writes the JSON data file; the only class that touches disk |
`RestaurantService` | Converts between the `Restaurant` object graph and JSON-friendly dictionaries; calls `FileManager` |
`RestaurantApp` | The Tkinter GUI: dashboard, tabs, forms, tables, dialogs |

## OOP Concepts Used
- **Classes & Objects** — every real-world concept above is a class; the app creates and uses many objects of each.
- **Constructors** — every class defines `__init__`.
- **Encapsulation** — `MenuItem.price` and `Table.status` are only ever changed through validating methods/properties (`@property`, `occupy()`, `mark_available()`), never set directly from outside.
- **Properties** — `MenuItem.price` uses `@property`/`@price.setter` to reject invalid prices; `Table.is_available` and `Order.is_empty` are computed read-only properties.
- **Inheritance** — `NoDiscount`, `PercentageDiscount` and `FixedAmountDiscount` all inherit from the abstract `Discount` base class.
- **Polymorphism** — `Order.calculate_total()` calls `self.discount.apply(...)` without caring which concrete discount type is plugged in.
- **Abstraction** — `Discount` is an `ABC` with `@abstractmethod`s; it defines *what* a discount must do, hiding *how* each type calculates it.
- **Composition** — `Restaurant` **has** a menu, tables, customers, orders and payments; `Order` **has** `OrderItem`s, each of which **has** a `MenuItem`.
- **Type Hints** — used throughout every method signature and attribute.
- **Exception Handling** — a full custom exception hierarchy (see `exceptions.py`) is raised for every business-rule violation and caught in the GUI to show friendly messages instead of crashing.
- **Methods** — all business behavior (occupying a table, checking out an order, applying a discount) lives on the relevant class, not scattered in the GUI.

## Business Rules
- An occupied table cannot be assigned to a new order (`TableOccupiedError`).
- Order item quantity must be greater than zero (`InvalidQuantityError`).
- An empty order cannot be checked out (`EmptyOrderError`).
- Order total is always calculated automatically from its items and discount — never typed in by hand.
- A menu item price must be greater than zero (`ValidationError`).
- Only *available* menu items can be newly added to an order (`MenuItemUnavailableError`).

## File Storage
- Format: **JSON** (`data/restaurant_data.json`), created automatically on first save.
- `FileManager` (in `file_manager/file_manager.py`) is the only class that opens files; it handles missing files and corrupted JSON gracefully.
- `RestaurantService` (in `services/restaurant_service.py`) converts the full object graph (menu, tables, customers, orders, payments) to and from plain dictionaries.
- Data loads automatically when the app starts and saves automatically when the window is closed.

## GUI Framework
**Tkinter** (`ttk` widgets), part of the Python standard library — no installation required.

## How to Run
```bash
# Requires Python 3.9+
python main.py
```
To run the automated tests:
```bash
pip install pytest
python -m pytest tests/test_scenarios.py -v
```

## Test Scenarios
10 scenarios are documented in `tests/test_scenarios.txt` and automated
in `tests/test_scenarios.py` (3 successful, 3 invalid input, 2
business-rule violations, 2 edge cases). All 10 currently pass.

## Screenshots

<img width="1920" height="1020" alt="Screenshot 2026-09-30 194838" src="https://github.com/user-attachments/assets/f5630bde-2b48-44dd-9941-5469020c3b5f" />
<img width="1920" height="1020" alt="Screenshot 2026-09-30 194858" src="https://github.com/user-attachments/assets/f3a24a61-f42c-4f69-815d-bb8ecabba0cd" />
<img width="1920" height="1020" alt="Screenshot 2026-09-30 195714" src="https://github.com/user-attachments/assets/c8cb2d1c-11af-468c-b837-9c875da6993b" />
