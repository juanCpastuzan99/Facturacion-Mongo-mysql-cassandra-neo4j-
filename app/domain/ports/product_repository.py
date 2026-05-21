from abc import ABC, abstractmethod
from typing import List, Optional

from ..entities.product import Product


class ProductRepository(ABC):
    """Puerto del dominio para productos."""

    @abstractmethod
    def save(self, product: Product) -> Product: ...

    @abstractmethod
    def find_by_sku(self, sku: str) -> Optional[Product]: ...

    @abstractmethod
    def find_all(self, category: Optional[str] = None) -> List[Product]: ...

    @abstractmethod
    def update_stock(self, sku: str, new_stock: int) -> None: ...

    @abstractmethod
    def delete(self, sku: str) -> None: ...
