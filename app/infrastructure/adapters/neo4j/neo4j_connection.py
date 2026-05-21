from neo4j import Driver, GraphDatabase

from ...config.settings import settings


class Neo4jConnection:
    """Singleton del driver Neo4j."""

    _driver: Driver | None = None

    @classmethod
    def driver(cls) -> Driver:
        if cls._driver is None:
            cls._driver = GraphDatabase.driver(
                settings.neo4j_uri,
                auth=(settings.neo4j_user, settings.neo4j_password),
            )
        return cls._driver

    @classmethod
    def shutdown(cls) -> None:
        if cls._driver:
            cls._driver.close()
        cls._driver = None
