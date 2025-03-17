import motor.motor_asyncio
from pymongo import MongoClient
from gridfs import GridFS
from app.core.config import settings

# Async client for FastAPI
client = motor.motor_asyncio.AsyncIOMotorClient(settings.MONGODB_URL)
db = client[settings.DATABASE_NAME]

# Sync client for GridFS operations
sync_client = MongoClient(settings.MONGODB_URL)
sync_db = sync_client[settings.DATABASE_NAME]
fs = GridFS(sync_db)

# Collections
users_collection = db.users
posts_collection = db.posts
comments_collection = db.comments
reactions_collection = db.reactions