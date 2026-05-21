"""Ejecuta todos los scripts de seed contra los 4 SGBDs.

Uso:
    python -m dbs.seed_all
o:
    python dbs/seed_all.py

Lee la configuración del .env (settings.py). Requiere que los servicios
de Cassandra, MongoDB, MySQL y Neo4j estén accesibles.
"""

from __future__ import annotations

import json
import re
import sys
import types
from pathlib import Path

# Stub para Python 3.12 (asyncore fue removido)
if "asyncore" not in sys.modules:
    _stub = types.ModuleType("asyncore")
    _stub.dispatcher = type("dispatcher", (), {})
    _stub.loop = lambda *a, **k: None
    sys.modules["asyncore"] = _stub

from cassandra.auth import PlainTextAuthProvider  # noqa: E402
from cassandra.cluster import Cluster  # noqa: E402
from cassandra.io.twistedreactor import TwistedConnection  # noqa: E402
from cassandra.policies import WhiteListRoundRobinPolicy  # noqa: E402
from neo4j import GraphDatabase  # noqa: E402
from pymongo import MongoClient  # noqa: E402

import mysql.connector  # noqa: E402

sys.path.append(str(Path(__file__).resolve().parents[1]))
from app.infrastructure.config.settings import settings  # noqa: E402


HERE = Path(__file__).parent


# ---------- Cassandra ----------------------------------------------------
def _execute_cql_statements(session, cql_text: str) -> None:
    cleaned = re.sub(r"//.*", "", cql_text)
    for stmt in (s.strip() for s in cleaned.split(";")):
        if stmt:
            session.execute(stmt)


def seed_cassandra() -> None:
    print(">>Cassandra: cargando 01_cassandra.cql")
    auth = (
        PlainTextAuthProvider(settings.cassandra_user, settings.cassandra_password)
        if settings.cassandra_user
        else None
    )
    hosts = list(settings.cassandra_hosts)
    cluster = Cluster(
        contact_points=hosts,
        port=settings.cassandra_port,
        auth_provider=auth,
        # Sin protocol_version: el driver negocia (Cassandra v5, Scylla v4).
        connection_class=TwistedConnection,
        load_balancing_policy=WhiteListRoundRobinPolicy(hosts),
        connect_timeout=20,
    )
    session = cluster.connect()
    cql = (HERE / "01_cassandra.cql").read_text(encoding="utf-8")
    _execute_cql_statements(session, cql)
    cluster.shutdown()
    print("  [OK]Cassandra OK")


# ---------- MongoDB ------------------------------------------------------
def seed_mongo() -> None:
    print(">>MongoDB: cargando productos")
    client = MongoClient(settings.mongo_uri)
    db = client[settings.mongo_db]
    db.products.drop()
    db.products.create_index("sku", unique=True)
    db.products.create_index("category")
    db.products.create_index("tags")
    products = json.loads((HERE / "products_seed.json").read_text(encoding="utf-8"))
    db.products.insert_many(products)
    print(f"  [OK]MongoDB OK ({db.products.count_documents({})} productos)")
    client.close()


# ---------- MySQL --------------------------------------------------------
def seed_mysql() -> None:
    print(">>MySQL: ejecutando 03_mysql.sql")
    conn = mysql.connector.connect(
        host=settings.mysql_host,
        port=settings.mysql_port,
        user=settings.mysql_user,
        password=settings.mysql_password,
        autocommit=True,
    )
    cur = conn.cursor()
    sql = (HERE / "03_mysql.sql").read_text(encoding="utf-8")
    for statement in _split_sql(sql):
        cur.execute(statement)
        while cur.nextset():
            pass
    cur.close()
    conn.close()
    print("  [OK]MySQL OK")


def _split_sql(text: str) -> list[str]:
    cleaned = re.sub(r"--.*", "", text)
    return [s.strip() for s in cleaned.split(";") if s.strip()]


# ---------- Neo4j --------------------------------------------------------
def seed_neo4j() -> None:
    print(">>Neo4j: ejecutando 04_neo4j.cypher")
    driver = GraphDatabase.driver(
        settings.neo4j_uri, auth=(settings.neo4j_user, settings.neo4j_password)
    )
    text = (HERE / "04_neo4j.cypher").read_text(encoding="utf-8")
    statements = _split_cypher(text)
    with driver.session() as s:
        for stmt in statements:
            s.run(stmt)
    driver.close()
    print("  [OK]Neo4j OK")


def _split_cypher(text: str) -> list[str]:
    cleaned = re.sub(r"//.*", "", text)
    return [s.strip() for s in cleaned.split(";") if s.strip()]


# ---------- Entry --------------------------------------------------------
if __name__ == "__main__":
    steps = [seed_cassandra, seed_mongo, seed_mysql, seed_neo4j]
    for step in steps:
        try:
            step()
        except Exception as exc:
            print(f"  [FAIL]{step.__name__} falló: {exc}", file=sys.stderr)
    print("\nListo. Visita http://localhost:8000 despues de levantar Flask.")
