from __future__ import annotations
from typing import Dict, Any
from exceptions import TableOccupiedError, ValidationError

AVAILABLE = "Available"
OCCUPIED = "Occupied"


class Table:
    def __init__(self, table_id: int, capacity: int, status: str = AVAILABLE) -> None:
        if capacity <= 0:
            raise ValidationError("Table capacity must be greater than zero.")
        self.table_id: int = table_id
        self.capacity: int = capacity
        self.status: str = status

    @property
    def is_available(self) -> bool:
        return self.status == AVAILABLE

    def occupy(self) -> None:
        if self.status == OCCUPIED:
            raise TableOccupiedError(f"Table {self.table_id} is already occupied.")
        self.status = OCCUPIED

    def free(self) -> None:
        self.status = AVAILABLE

    def to_dict(self) -> Dict[str, Any]:
        return {"table_id": self.table_id, "capacity": self.capacity, "status": self.status}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Table":
        return cls(table_id=data["table_id"], capacity=data["capacity"], status=data["status"])

    def __str__(self) -> str:
        return f"Table {self.table_id} (seats {self.capacity}) - {self.status}"
