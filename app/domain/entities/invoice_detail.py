from dataclasses import dataclass
from typing import Optional


@dataclass
class InvoiceDetail:
    """Línea de detalle de factura. Persistida en MySQL en detalle_factura.

    Conserva el SKU (referencia a MongoDB) y una "foto" del producto
    en el momento de la venta para garantizar inmutabilidad histórica.
    """

    product_sku: str
    product_name: str
    quantity: int
    unit_price: float
    id: Optional[int] = None
    invoice_id: Optional[int] = None

    def __post_init__(self) -> None:
        if self.quantity <= 0:
            raise ValueError("quantity must be positive")
        if self.unit_price < 0:
            raise ValueError("unit_price cannot be negative")

    @property
    def line_total(self) -> float:
        return round(self.quantity * self.unit_price, 2)
