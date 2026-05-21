import mysql.connector
from mysql.connector.pooling import MySQLConnectionPool

from ...config.settings import settings


class MySQLConnection:
    """Pool de conexiones MySQL."""

    _pool: MySQLConnectionPool | None = None

    @classmethod
    def _get_pool(cls) -> MySQLConnectionPool:
        if cls._pool is None:
            cls._pool = MySQLConnectionPool(
                pool_name="billing_pool",
                pool_size=5,
                host=settings.mysql_host,
                port=settings.mysql_port,
                user=settings.mysql_user,
                password=settings.mysql_password,
                database=settings.mysql_database,
                autocommit=False,
            )
        return cls._pool

    @classmethod
    def get_connection(cls) -> mysql.connector.MySQLConnection:
        return cls._get_pool().get_connection()
