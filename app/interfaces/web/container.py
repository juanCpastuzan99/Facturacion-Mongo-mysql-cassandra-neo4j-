"""Contenedor de dependencias.

Mantiene el wiring entre puertos (dominio) y adaptadores (infraestructura)
y expone los servicios de aplicación listos para inyectar en las rutas.
"""

from ...application.services.invoice_service import InvoiceService
from ...application.services.person_service import PersonService
from ...application.services.product_service import ProductService
from ...application.services.recommendation_service import RecommendationService
from ...infrastructure.adapters.cassandra.cassandra_person_repository import (
    CassandraPersonRepository,
)
from ...infrastructure.adapters.mongo.mongo_product_repository import (
    MongoProductRepository,
)
from ...infrastructure.adapters.mysql.mysql_invoice_repository import (
    MySQLInvoiceRepository,
)
from ...infrastructure.adapters.neo4j.neo4j_recommendation_repository import (
    Neo4jRecommendationRepository,
)


class Container:
    _instance: "Container | None" = None

    def __init__(self) -> None:
        self.person_repo = CassandraPersonRepository()
        self.product_repo = MongoProductRepository()
        self.invoice_repo = MySQLInvoiceRepository()
        self.recommendation_repo = Neo4jRecommendationRepository()

        self.person_service = PersonService(self.person_repo, self.recommendation_repo)
        self.product_service = ProductService(self.product_repo, self.recommendation_repo)
        self.invoice_service = InvoiceService(
            self.invoice_repo, self.product_repo, self.person_repo, self.recommendation_repo
        )
        self.recommendation_service = RecommendationService(
            self.recommendation_repo, self.person_repo
        )

    @classmethod
    def instance(cls) -> "Container":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
