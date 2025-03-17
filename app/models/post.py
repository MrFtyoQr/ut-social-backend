from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from bson import ObjectId
from app.models.user import PyObjectId

class FileAttachment(BaseModel):
    file_id: str
    filename: str
    content_type: str
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class PostBase(BaseModel):
    content: str
    career: str  # Career/major this post is related to

class PostCreate(PostBase):
    pass

class PostInDB(PostBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: PyObjectId
    attachments: List[FileAttachment] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class Post(PostBase):
    id: str = Field(..., alias="_id")
    user_id: str
    user: dict  # User information (username, profile picture)
    attachments: List[FileAttachment] = []
    created_at: datetime
    comment_count: int = 0
    reaction_count: int = 0
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}