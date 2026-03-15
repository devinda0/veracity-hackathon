from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.logger import get_logger

logger = get_logger(__name__)


async def init_mongodb(db: AsyncIOMotorDatabase) -> None:
    collections = ["users", "sessions", "chat_history", "audit_logs", "business_context"]
    existing_collections = set(await db.list_collection_names())

    for collection_name in collections:
        if collection_name not in existing_collections:
            await db.create_collection(collection_name)
            logger.info("mongodb_collection_created", collection=collection_name)

    await db.users.create_index("email", unique=True)
    await db.sessions.create_index([("user_id", 1), ("created_at", -1)])
    await db.chat_history.create_index([("session_id", 1), ("timestamp", -1)])
    await db.audit_logs.create_index([("user_id", 1), ("action", 1), ("created_at", -1)])
    await db.business_context.create_index([("session_id", 1), ("created_at", -1)])

    logger.info("mongodb_indexes_created")

