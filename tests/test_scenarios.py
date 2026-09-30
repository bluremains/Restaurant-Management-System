import sys
import os
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.restaurant import Restaurant
from models.discount import PercentageDiscount
from exceptions import (
    ValidationError,
    InvalidQuantityError,
    TableNotFoundError,
    TableOccupiedError,
    EmptyOrderError,
)


@pytest.fixture
def restaurant() -> Restaurant:
    r = Restaurant("Test")
    r.add_table(capacity=4)
    r.add_menu_item("Pizza", "Main", 9.99)
    r.add_menu_item("Lemonade", "Drink", 2.50)
    return r

def test_1_add_menu_item(restaurant: Restaurant) -> None:
    item = restaurant.add_menu_item("Caesar Salad", "ٍSalads", 6.50)
    assert item.name == "Caesar Salad"
    assert item.available is True
    assert restaurant.menu[item.item_id].price == 6.50


def test_2_full_order_flow(restaurant: Restaurant) -> None:
    order = restaurant.create_order(table_id=1)
    restaurant.add_item_to_order(order.order_id, item_id=1, quantity=2)
    restaurant.add_item_to_order(order.order_id, item_id=2, quantity=1)

    payment = restaurant.checkout_order(order.order_id, method="Cash")

    assert order.status == "Paid"
    assert payment.amount == pytest.approx(9.99 * 2 + 2.50)
    assert restaurant.get_table(1).status == "Available"


def test_3_search_customers(restaurant: Restaurant) -> None:
    restaurant.add_customer("Yomn", "011111111")
    results = restaurant.search_customers("Yomn")
    assert len(results) == 1
    assert results[0].name == "Yomn"

def test_4_negative_price_rejected(restaurant: Restaurant) -> None:
    with pytest.raises(ValidationError):
        restaurant.add_menu_item("Bad Item", "Main", -5)


def test_5_zero_quantity_rejected(restaurant: Restaurant) -> None:
    order = restaurant.create_order(table_id=1)
    with pytest.raises(InvalidQuantityError):
        restaurant.add_item_to_order(order.order_id, item_id=1, quantity=0)


def test_6_order_on_missing_table(restaurant: Restaurant) -> None:
    with pytest.raises(TableNotFoundError):
        restaurant.create_order(table_id=999)


def test_7_cannot_occupy_occupied_table(restaurant: Restaurant) -> None:
    restaurant.create_order(table_id=1)
    with pytest.raises(TableOccupiedError):
        restaurant.create_order(table_id=1)


def test_8_cannot_checkout_empty_order(restaurant: Restaurant) -> None:
    order = restaurant.create_order(table_id=1)
    with pytest.raises(EmptyOrderError):
        restaurant.checkout_order(order.order_id)
    assert order.status == "Open"


def test_9_adding_same_item_twice_merges_quantity(restaurant: Restaurant) -> None:
    order = restaurant.create_order(table_id=1)
    restaurant.add_item_to_order(order.order_id, item_id=1, quantity=2)
    restaurant.add_item_to_order(order.order_id, item_id=1, quantity=3)

    assert len(order.items) == 1
    assert order.items[0].quantity == 5


def test_10_full_discount_and_cancel_frees_table(restaurant: Restaurant) -> None:
    order = restaurant.create_order(table_id=1)
    restaurant.add_item_to_order(order.order_id, item_id=1, quantity=1)
    restaurant.apply_discount(order.order_id, PercentageDiscount(100))
    assert order.calculate_total() == 0

    restaurant.cancel_order(order.order_id)
    assert restaurant.get_table(1).status == "Available"
