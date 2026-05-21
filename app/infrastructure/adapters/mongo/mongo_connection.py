from pymongo import MongoClient
from pymongo.database import Database

from ...config.settings import settings


class MongoConnection:
    """Singleton de conexión a MongoDB."""

    _client: MongoClient | None = None
    _db: Database | None = None

    @classmethod
    def db(cls) -> Database:
        if cls._db is None:
            cls._client = MongoClient(settings.mongo_uri, uuidRepresentation="standard")
            cls._db = cls._client[settings.mongo_db]
        return cls._db

    @classmethod
    def shutdown(cls) -> None:
        if cls._client:
            cls._client.close()
        cls._client = None
        cls._db = None
