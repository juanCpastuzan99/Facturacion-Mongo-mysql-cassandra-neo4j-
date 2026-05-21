from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

from .invoice_detail import InvoiceDetail


@dataclass
class Invoice:
    """Entidad del dominio que representa una factura encabezado.

    Persistida en MySQL junto con sus detalles. Mantiene únicamente
    los identificadores de cliente/empleado que referencian Cassandra.
    """

    client_document: str
    employee_document: str
    payment_method: str
    details: List[InvoiceDetail] = field(default_factory=list)
    id: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    tax_rate: float = 0.19

    VALID_PAYMENTS = ("CASH", "CARD", "TRANSFER")

    def __post_init__(self) -> None:
        if self.payment_method not in self.VALID_PAYMENTS:
            raise ValueError(f"payment_method must be one of {self.VALID_PAYMENTS}")

    @property
    def subtotal(self) -> float:
        return round(sum(d.line_total for d in self.details), 2)

    @property
    def tax(self) -> float:
        return round(self.subtotal * self.tax_rate, 2)

    @property
    def total(self) -> float:
        return round(self.subtotal + self.tax, 2)

    def add_detail(self, detail: InvoiceDetail) -> None:
        self.details.append(detail)
