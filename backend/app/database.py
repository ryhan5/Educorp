import os
from motor.motor_asyncio import AsyncIOMotorClient

# Default to localhost if not specified
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = "educorp"

client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]

async def get_database():
    return db
