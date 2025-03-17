from typing import List, Optional
from bson import ObjectId
from fastapi import UploadFile
import io
from app.db.mongodb import posts_collection, fs, sync_db
from app.models.post import PostCreate, PostInDB, FileAttachment

async def create_post(post_in: PostCreate, user_id: str, files: List[UploadFile] = None) -> PostInDB:
    attachments = []
    
    if files:
        for file in files:
            content = await file.read()
            file_id = fs.put(
                io.BytesIO(content),
                filename=file.filename,
                content_type=file.content_type
            )
            
            attachments.append(
                FileAttachment(
                    file_id=str(file_id),
                    filename=file.filename,
                    content_type=file.content_type
                )
            )
    
    post_in_db = PostInDB(
        **post_in.dict(),
        user_id=ObjectId(user_id),
        attachments=attachments
    )
    
    result = await posts_collection.insert_one(post_in_db.dict(by_alias=True))
    post_in_db.id = result.inserted_id
    return post_in_db

async def get_posts(skip: int = 0, limit: int = 20, career: Optional[str] = None) -> List[PostInDB]:
    query = {}
    if career:
        query["career"] = career
    
    cursor = posts_collection.find(query).sort("created_at", -1).skip(skip).limit(limit)
    posts = await cursor.to_list(length=limit)
    return [PostInDB(**post) for post in posts]

async def get_post_by_id(post_id: str) -> Optional[PostInDB]:
    post = await posts_collection.find_one({"_id": ObjectId(post_id)})
    if post:
        return PostInDB(**post)
    return None

async def get_posts_by_user_id(user_id: str, skip: int = 0, limit: int = 20) -> List[PostInDB]:
    cursor = posts_collection.find({"user_id": ObjectId(user_id)}).sort("created_at", -1).skip(skip).limit(limit)
    posts = await cursor.to_list(length=limit)
    return [PostInDB(**post) for post in posts]

async def delete_post(post_id: str, user_id: str) -> bool:
    post = await get_post_by_id(post_id)
    if not post:
        return False
    
    if str(post.user_id) != user_id:
        return False
    
    # Delete file attachments from GridFS
    for attachment in post.attachments:
        fs.delete(ObjectId(attachment.file_id))
    
    result = await posts_collection.delete_one({"_id": ObjectId(post_id)})
    return result.deleted_count > 0