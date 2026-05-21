from typing import List, Optional

from ...domain.entities.product import Product
from ...domain.ports.product_repository import ProductRepository
from ...domain.ports.recommendation_repository import RecommendationRepository


class ProductService:
    def __init__(
        self,
        product_repo: ProductRepository,
        recommendation_repo: RecommendationRepository,
    ) -> None:
        self._products = product_repo
        self._graph = recommendation_repo

    def create(self, product: Product) -> Product:
        if self._products.find_by_sku(product.sku):
            raise ValueError(f"Product with sku {product.sku} already exists")
        saved = self._products.save(product)
        self._graph.upsert_product(saved)
        return saved

    def update(self, product: Product) -> Product:
        if not self._products.find_by_sku(product.sku):
            raise ValueError(f"Product with sku {product.sku} not found")
        self._products.save(product)
        self._graph.upsert_product(product)
        return product

    def get(self, sku: str) -> Optional[Product]:
        return self._products.find_by_sku(sku)

    def list(self, category: Optional[str] = None) -> List[Product]:
        return self._products.find_all(category=category)

    def delete(self, sku: str) -> None:
        self._products.delete(sku)
