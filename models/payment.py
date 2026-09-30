from __future__ import annotations
from datetime import datetime
from typing import Dict, Any, Optional

from exceptions import InvalidPaymentError


class Payment:

    def __init__(
        self,
        payment_id: int,
        order_id: int,
        amount: float,
        method: str = "Cash",
        timestamp: Optional[str] = None,
    ) -> None:
        if amount <= 0:
            raise InvalidPaymentError("Payment amount must be greater than zero.")
        self.payment_id: int = payment_id
        self.order_id: int = order_id
        self.amount: float = round(amount, 2)
        self.method: str = method
        self.timestamp: str = timestamp or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "payment_id": self.payment_id,
            "order_id": self.order_id,
            "amount": self.amount,
            "method": self.method,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Payment":
        return cls(
            payment_id=data["payment_id"],
            order_id=data["order_id"],
            amount=data["amount"],
            method=data.get("method", "Cash"),
            timestamp=data.get("timestamp"),
        )

    def __str__(self) -> str:
        return f"Payment #{self.payment_id} - Order {self.order_id} - ${self.amount:.2f} ({self.method})"
