from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Product:
    """Entidad del dominio que representa un producto del catálogo.

    Persistida en MongoDB para aprovechar la flexibilidad del esquema
    (tags y atributos varían según categoría).
    """

    sku: str
    name: str
    description: str
    category: str
    price: float
    stock: int
    brand: str
    tags: List[str] = field(default_factory=list)
    image_url: Optional[str] = None
    id: Optional[str] = None

    def __post_init__(self) -> None:
        if self.price < 0:
            raise ValueError("price cannot be negative")
        if self.stock < 0:
            raise ValueError("stock cannot be negative")

    def discount_stock(self, quantity: int) -> None:
        if quantity <= 0:
            raise ValueError("quantity must be positive")
        if quantity > self.stock:
            raise ValueError(f"insufficient stock for {self.sku}")
        self.stock -= quantity
