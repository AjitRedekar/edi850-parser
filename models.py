from dataclasses import dataclass, field
from decimal import Decimal
from datetime import date


@dataclass(slots=True)
class OrderLine:
    line_no: int | None = None
    qty: int | None = None
    uom: str | None = None
    price: Decimal | None = None
    item: str | None = None
    description: str | None = None

    def extended_value(self) -> Decimal:
        """Calculate the extended value of the order line."""
        return self.qty * self.price | None


@dataclass(slots=True)
class Address:
    name: str | None = None
    address: str | None = None
    city: str | None = None
    state: str | None = None
    zip: str | None = None


@dataclass(slots=True)
class Order:
    po_number: str | None = None
    po_date: date | None = None
    ship_to: Address = field(default_factory=Address)
    lines: list[OrderLine] = field(default_factory=OrderLine)
    guid: str | None = None
