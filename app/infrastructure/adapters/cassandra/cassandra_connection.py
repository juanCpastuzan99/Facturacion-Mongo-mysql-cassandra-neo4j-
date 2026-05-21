"""Conexión a Cassandra.

Python 3.12 eliminó el módulo `asyncore` que cassandra-driver 3.29
intenta importar al inicializarse para escoger el reactor por defecto.
Antes de cargar `cassandra.cluster` registramos un stub mínimo y forzamos
el `AsyncioConnection` (compatible con 3.12) como clase de conexión.
"""

import sys
import types

if "asyncore" not in sys.modules:
    _stub = types.ModuleType("asyncore")
    _stub.dispatcher = type("dispatcher", (), {})
    _stub.loop = lambda *a, **k: None
    sys.modules["asyncore"] = _stub

from cassandra.auth import PlainTextAuthProvider  # noqa: E402
from cassandra.cluster import Cluster, Session  # noqa: E402
from cassandra.io.twistedreactor import TwistedConnection  # noqa: E402
from cassandra.policies import WhiteListRoundRobinPolicy  # noqa: E402

from ...config.settings import settings  # noqa: E402


class CassandraConnection:
    """Singleton de conexión al cluster Cassandra."""

    _session: Session | None = None
    _cluster: Cluster | None = None

    @classmethod
    def session(cls) -> Session:
        if cls._session is None:
            auth = None
            if settings.cassandra_user:
                auth = PlainTextAuthProvider(
                    username=settings.cassandra_user,
                    password=settings.cassandra_password,
                )
            hosts = list(settings.cassandra_hosts)
            cls._cluster = Cluster(
                contact_points=hosts,
                port=settings.cassandra_port,
                auth_provider=auth,
                # Sin protocol_version fijo: el driver lo negocia con el
                # servidor (Cassandra 4/5 = v5, ScyllaDB = v4).
                connection_class=TwistedConnection,
                # Evita que el driver descubra "peers" con IPs internas
                # (necesario cuando Scylla/Cassandra corre en WSL/Docker).
                load_balancing_policy=WhiteListRoundRobinPolicy(hosts),
                connect_timeout=20,
            )
            cls._session = cls._cluster.connect()
            cls._session.set_keyspace(settings.cassandra_keyspace)
        return cls._session

    @classmethod
    def shutdown(cls) -> None:
        if cls._session:
            cls._session.shutdown()
        if cls._cluster:
            cls._cluster.shutdown()
        cls._session = None
        cls._cluster = None
