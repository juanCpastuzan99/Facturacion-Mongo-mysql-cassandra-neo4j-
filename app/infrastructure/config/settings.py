import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    flask_secret: str = os.getenv("FLASK_SECRET", "change-me-in-prod")
    flask_debug: bool = os.getenv("FLASK_DEBUG", "True").lower() == "true"
    flask_host: str = os.getenv("FLASK_HOST", "127.0.0.1")
    flask_port: int = int(os.getenv("FLASK_PORT", "5000"))

    cassandra_hosts: tuple = tuple(os.getenv("CASSANDRA_HOSTS", "127.0.0.1").split(","))
    cassandra_port: int = int(os.getenv("CASSANDRA_PORT", "9042"))
    cassandra_keyspace: str = os.getenv("CASSANDRA_KEYSPACE", "billing")
    cassandra_user: str = os.getenv("CASSANDRA_USER", "")
    cassandra_password: str = os.getenv("CASSANDRA_PASSWORD", "")

    mongo_uri: str = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    mongo_db: str = os.getenv("MONGO_DB", "billing")

    mysql_host: str = os.getenv("MYSQL_HOST", "127.0.0.1")
    mysql_port: int = int(os.getenv("MYSQL_PORT", "3306"))
    mysql_user: str = os.getenv("MYSQL_USER", "root")
    mysql_password: str = os.getenv("MYSQL_PASSWORD", "")
    mysql_database: str = os.getenv("MYSQL_DATABASE", "billing")

    neo4j_uri: str = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    neo4j_user: str = os.getenv("NEO4J_USER", "neo4j")
    neo4j_password: str = os.getenv("NEO4J_PASSWORD", "neo4j12345")


settings = Settings()
