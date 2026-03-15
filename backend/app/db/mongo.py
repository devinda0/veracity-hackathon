from contextlib import asynccontextmanager
from typing import AsyncIterator

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import OperationFailure, ServerSelectionTimeoutError

from app.core.logger import get_logger

logger = get_logger(__name__)


class MongoDBClient:
    _instance: AsyncIOMotorClient | None = None
    _db: AsyncIOMotorDatabase | None = None

    @classmethod
    async def connect(cls, mongo_uri: str, database_name: str) -> AsyncIOMotorDatabase:
        if cls._instance is None:
            cls._instance = AsyncIOMotorClient(
                mongo_uri,
                maxPoolSize=10,
                minPoolSize=2,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000,
                socketTimeoutMS=5000,
                uuidRepresentation="standard",
            )
            cls._db = cls._instance[database_name]

            try:
                await cls._instance.admin.command("ping")
                await cls._verify_replica_set()
                logger.info("mongodb_connected", database=database_name)
            except ServerSelectionTimeoutError as exc:
                logger.error("mongodb_connection_timeout", error=str(exc))
                await cls.disconnect()
                raise
            except Exception:
                await cls.disconnect()
                raise

        if cls._db is None:
            cls._db = cls._instance[database_name]
        return cls._db

    @classmethod
    async def _verify_replica_set(cls) -> None:
        if cls._instance is None:
            return

        try:
            status = await cls._instance.admin.command("replSetGetStatus")
            logger.info(
                "mongodb_replica_set_verified",
                set=status.get("set"),
                members=len(status.get("members", [])),
            )
        except OperationFailure as exc:
            logger.warning(
                "mongodb_replica_set_check_failed",
                code=getattr(exc, "code", None),
                error=str(exc),
            )
        except Exception as exc:
            logger.warning("mongodb_replica_set_check_failed", error=str(exc))

    @classmethod
    async def disconnect(cls) -> None:
        if cls._instance is not None:
            cls._instance.close()
            logger.info("mongodb_disconnected")

        cls._instance = None
        cls._db = None

    @classmethod
    def get_db(cls) -> AsyncIOMotorDatabase:
        if cls._db is None:
            raise RuntimeError("MongoDB not initialized. Call connect() first.")
        return cls._db


async def get_mongo_db() -> AsyncIOMotorDatabase:
    return MongoDBClient.get_db()


@asynccontextmanager
async def mongo_database_context() -> AsyncIterator[AsyncIOMotorDatabase]:
    yield MongoDBClient.get_db()

