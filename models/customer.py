from __future__ import annotations
from typing import Dict, Any, Optional


class Customer:

    def __init__(self, customer_id: int, name: str, phone: Optional[str] = None) -> None:
        self.customer_id: int = customer_id
        self.name: str = name
        self.phone: str = phone or ""

    def matches(self, keyword: str) -> bool:
        keyword = keyword.lower().strip()
        return keyword in self.name.lower() or keyword in self.phone.lower()

    def to_dict(self) -> Dict[str, Any]:
        return {"customer_id": self.customer_id, "name": self.name, "phone": self.phone}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Customer":
        return cls(customer_id=data["customer_id"], name=data["name"], phone=data.get("phone", ""))

    def __str__(self) -> str:
        return f"[{self.customer_id}] {self.name} ({self.phone})"
