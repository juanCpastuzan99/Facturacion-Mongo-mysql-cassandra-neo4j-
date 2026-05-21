from typing import List

from ....domain.entities.person import Person
from ....domain.entities.product import Product
from ....domain.ports.recommendation_repository import RecommendationRepository
from .neo4j_connection import Neo4jConnection


class Neo4jRecommendationRepository(RecommendationRepository):
    """Adaptador Neo4j que construye un grafo Cliente-Producto-Contexto y
    recomienda combinando tres heurísticas:

      1) Filtrado colaborativo: lo que compraron clientes similares
         (mismo barrio, municipio, estrato y género).
      2) Similitud por categoría/tags: productos cercanos a los ya comprados.
      3) Popularidad geográfica: top productos del barrio del cliente.

    El score es la suma ponderada y se devuelve junto a la razón principal.
    """

    def __init__(self) -> None:
        self._driver = Neo4jConnection.driver()

    def upsert_person(self, person: Person) -> None:
        with self._driver.session() as s:
            s.run(
                """
                MERGE (p:Person {document: $document})
                SET p.role = $role,
                    p.first_name = $first_name,
                    p.last_name = $last_name,
                    p.gender = $gender,
                    p.stratum = $stratum
                MERGE (n:Neighborhood {name: $neighborhood})
                MERGE (m:Municipality {name: $municipality})
                MERGE (d:Department {name: $department})
                MERGE (g:Gender {code: $gender})
                MERGE (s:Stratum {level: $stratum})
                MERGE (p)-[:LIVES_IN]->(n)
                MERGE (n)-[:PART_OF]->(m)
                MERGE (m)-[:PART_OF]->(d)
                MERGE (p)-[:HAS_GENDER]->(g)
                MERGE (p)-[:HAS_STRATUM]->(s)
                """,
                document=person.document,
                role=person.role,
                first_name=person.first_name,
                last_name=person.last_name,
                gender=person.gender,
                stratum=person.stratum,
                neighborhood=person.neighborhood,
                municipality=person.municipality,
                department=person.department,
            )

    def upsert_product(self, product: Product) -> None:
        with self._driver.session() as s:
            s.run(
                """
                MERGE (p:Product {sku: $sku})
                SET p.name = $name,
                    p.price = $price,
                    p.brand = $brand
                MERGE (c:Category {name: $category})
                MERGE (p)-[:IN_CATEGORY]->(c)
                WITH p
                UNWIND $tags AS tag
                  MERGE (t:Tag {name: tag})
                  MERGE (p)-[:HAS_TAG]->(t)
                """,
                sku=product.sku,
                name=product.name,
                price=product.price,
                brand=product.brand,
                category=product.category,
                tags=product.tags,
            )

    def register_purchase(self, client_document: str, product_sku: str, quantity: int) -> None:
        with self._driver.session() as s:
            s.run(
                """
                MATCH (c:Person {document: $doc}), (p:Product {sku: $sku})
                MERGE (c)-[r:BOUGHT]->(p)
                ON CREATE SET r.quantity = $qty, r.times = 1
                ON MATCH  SET r.quantity = r.quantity + $qty, r.times = r.times + 1
                """,
                doc=client_document,
                sku=product_sku,
                qty=quantity,
            )

    def recommend_for_client(self, client_document: str, limit: int = 5) -> List[dict]:
        query = """
        CALL {
          // 1) Filtrado colaborativo: vecinos del mismo barrio,
          //    mismo género y estrato.
          MATCH (me:Person {document: $doc})-[:LIVES_IN]->(n:Neighborhood),
                (other:Person)-[:LIVES_IN]->(n),
                (other)-[ob:BOUGHT]->(rec:Product)
          WHERE other.document <> $doc
            AND other.gender   = me.gender
            AND other.stratum  = me.stratum
            AND NOT (me)-[:BOUGHT]->(rec)
          RETURN rec AS product,
                 3.0 * count(DISTINCT other) + 0.5 * sum(coalesce(ob.times, 0)) AS score,
                 'clientes similares en tu barrio' AS reason

          UNION

          // 2) Similitud por categoría/tags con mis compras.
          MATCH (me:Person {document: $doc})-[:BOUGHT]->(mine:Product)
                -[:IN_CATEGORY|HAS_TAG]->(ctx)
                <-[:IN_CATEGORY|HAS_TAG]-(rec:Product)
          WHERE rec <> mine AND NOT (me)-[:BOUGHT]->(rec)
          RETURN rec AS product,
                 2.0 * count(DISTINCT ctx) AS score,
                 'similar a productos que ya compraste' AS reason

          UNION

          // 3) Popularidad en el barrio.
          MATCH (me:Person {document: $doc})-[:LIVES_IN]->(n:Neighborhood),
                (anyone:Person)-[:LIVES_IN]->(n),
                (anyone)-[ob:BOUGHT]->(rec:Product)
          WHERE NOT (me)-[:BOUGHT]->(rec)
          RETURN rec AS product,
                 1.0 * sum(coalesce(ob.times, 0)) AS score,
                 'popular en tu barrio' AS reason
        }
        WITH product, sum(score) AS total_score, collect(reason) AS reasons
        WHERE product IS NOT NULL
        RETURN product.sku   AS sku,
               product.name  AS name,
               product.price AS price,
               total_score   AS score,
               reasons[0]    AS reason
        ORDER BY total_score DESC
        LIMIT $limit
        """
        with self._driver.session() as s:
            result = s.run(query, doc=client_document, limit=limit)
            return [
                {
                    "sku": r["sku"],
                    "name": r["name"],
                    "price": r["price"],
                    "score": round(float(r["score"]), 2),
                    "reason": r["reason"],
                }
                for r in result
                if r["sku"] is not None
            ]

    def reset_graph(self) -> None:
        with self._driver.session() as s:
            s.run("MATCH (n) DETACH DELETE n")
