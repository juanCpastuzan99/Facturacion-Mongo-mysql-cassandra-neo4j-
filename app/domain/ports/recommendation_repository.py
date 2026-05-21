from abc import ABC, abstractmethod
from typing import List

from ..entities.person import Person
from ..entities.product import Product


class RecommendationRepository(ABC):
    """Puerto del dominio para el motor de recomendaciones (Neo4j)."""

    @abstractmethod
    def upsert_person(self, person: Person) -> None: ...

    @abstractmethod
    def upsert_product(self, product: Product) -> None: ...

    @abstractmethod
    def register_purchase(self, client_document: str, product_sku: str, quantity: int) -> None: ...

    @abstractmethod
    def recommend_for_client(self, client_document: str, limit: int = 5) -> List[dict]:
        """Recomienda productos. Cada dict trae sku, name, score y reason."""
        ...

    @abstractmethod
    def reset_graph(self) -> None: ...
