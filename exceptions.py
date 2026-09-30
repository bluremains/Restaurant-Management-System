class RestaurantError(Exception):
    """Base class for every error raised by this application."""


class ValidationError(RestaurantError):
    """Raised when user-provided data fails a basic validation check."""


class TableNotFoundError(RestaurantError):
    """Raised when a table id does not exist."""


class TableOccupiedError(RestaurantError):
    """Raised when trying to assign an order to a table that is already occupied."""


class MenuItemNotFoundError(RestaurantError):
    """Raised when a menu item id does not exist."""


class MenuItemUnavailableError(RestaurantError):
    """Raised when trying to order a menu item that is marked unavailable."""


class InvalidQuantityError(RestaurantError):
    """Raised when an order-item quantity is not greater than zero."""


class EmptyOrderError(RestaurantError):
    """Raised when trying to check out an order that has no items."""


class OrderNotFoundError(RestaurantError):
    """Raised when an order id does not exist."""


class CustomerNotFoundError(RestaurantError):
    """Raised when a customer id does not exist."""


class InvalidPaymentError(RestaurantError):
    """Raised when a payment amount is not valid (e.g. zero or negative)."""
