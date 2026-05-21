from typing import List, Optional

from ....domain.entities.product import Product
from ....domain.ports.product_repository import ProductRepository
from .mongo_connection import MongoConnection


class MongoProductRepository(ProductRepository):
    """Adaptador MongoDB para productos. Colección: products."""

    def __init__(self) -> None:
        self._collection = MongoConnection.db()["products"]
        self._collection.create_index("sku", unique=True)
        self._collection.create_index("category")
        self._collection.create_index("tags")

    def save(self, product: Product) -> Product:
        doc = self._to_doc(product)
        self._collection.update_one({"sku": product.sku}, {"$set": doc}, upsert=True)
        saved = self._collection.find_one({"sku": product.sku})
        return self._to_entity(saved)

    def find_by_sku(self, sku: str) -> Optional[Product]:
        doc = self._collection.find_one({"sku": sku})
        return self._to_entity(doc) if doc else None

    def find_all(self, category: Optional[str] = None) -> List[Product]:
        query = {"category": category} if category else {}
        return [self._to_entity(d) for d in self._collection.find(query).sort("name", 1)]

    def update_stock(self, sku: str, new_stock: int) -> None:
        self._collection.update_one({"sku": sku}, {"$set": {"stock": new_stock}})

    def delete(self, sku: str) -> None:
        self._collection.delete_one({"sku": sku})

    @staticmethod
    def _to_doc(product: Product) -> dict:
        return {
            "sku": product.sku,
            "name": product.name,
            "description": product.description,
            "category": product.category,
            "price": product.price,
            "stock": product.stock,
            "brand": product.brand,
            "tags": product.tags,
            "image_url": product.image_url,
        }

    @staticmethod
    def _to_entity(doc: dict) -> Product:
        return Product(
            id=str(doc.get("_id")),
            sku=doc["sku"],
            name=doc["name"],
            description=doc.get("description", ""),
            category=doc["category"],
            price=float(doc["price"]),
            stock=int(doc["stock"]),
            brand=doc.get("brand", ""),
            tags=doc.get("tags", []),
            image_url=doc.get("image_url"),
        )
