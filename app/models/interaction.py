from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime
from bson import ObjectId
from app.models.user import PyObjectId

class CommentBase(BaseModel):
    content: str

class CommentCreate(CommentBase):
    post_id: str

class CommentInDB(CommentBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    post_id: PyObjectId
    user_id: PyObjectId
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class Comment(CommentBase):
    id: str = Field(..., alias="_id")
    post_id: str
    user_id: str
    user: dict  # User information (username, profile picture)
    created_at: datetime
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class ReactionType(str, Enum):
    LIKE = "like"
    LOVE = "love"
    HAHA = "haha"
    WOW = "wow"
    SAD = "sad"
    ANGRY = "angry"

class ReactionBase(BaseModel):
    reaction_type: ReactionType

class ReactionCreate(ReactionBase):
    post_id: str

class ReactionInDB(ReactionBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    post_id: PyObjectId
    user_id: PyObjectId
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class Reaction(ReactionBase):
    id: str = Field(..., alias="_id")
    post_id: str
    user_id: str
    user: dict  # User information (username, profile picture)
    created_at: datetime
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}