from typing import List, Optional
from bson import ObjectId
from app.db.mongodb import comments_collection, reactions_collection
from app.models.interaction import CommentCreate, CommentInDB, ReactionCreate, ReactionInDB, ReactionType

# Comment services
async def create_comment(comment_in: CommentCreate, user_id: str) -> CommentInDB:
    comment_in_db = CommentInDB(
        **comment_in.dict(),
        user_id=ObjectId(user_id),
        post_id=ObjectId(comment_in.post_id)
    )
    
    result = await comments_collection.insert_one(comment_in_db.dict(by_alias=True))
    comment_in_db.id = result.inserted_id
    return comment_in_db

async def get_comments_by_post_id(post_id: str, skip: int = 0, limit: int = 50) -> List[CommentInDB]:
    cursor = comments_collection.find({"post_id": ObjectId(post_id)}).sort("created_at", 1).skip(skip).limit(limit)
    comments = await cursor.to_list(length=limit)
    return [CommentInDB(**comment) for comment in comments]

async def delete_comment(comment_id: str, user_id: str) -> bool:
    comment = await comments_collection.find_one({"_id": ObjectId(comment_id)})
    if not comment:
        return False
    
    if str(comment["user_id"]) != user_id:
        return False
    
    result = await comments_collection.delete_one({"_id": ObjectId(comment_id)})
    return result.deleted_count > 0

# Reaction services
async def create_or_update_reaction(reaction_in: ReactionCreate, user_id: str) -> ReactionInDB:
    # Check if user already reacted to this post
    existing_reaction = await reactions_collection.find_one({
        "post_id": ObjectId(reaction_in.post_id),
        "user_id": ObjectId(user_id)
    })
    
    if existing_reaction:
        # Update existing reaction
        await reactions_collection.update_one(
            {"_id": existing_reaction["_id"]},
            {"$set": {"reaction_type": reaction_in.reaction_type}}
        )
        existing_reaction["reaction_type"] = reaction_in.reaction_type
        return ReactionInDB(**existing_reaction)
    
    # Create new reaction
    reaction_in_db = ReactionInDB(
        **reaction_in.dict(),
        user_id=ObjectId(user_id),
        post_id=ObjectId(reaction_in.post_id)
    )
    
    result = await reactions_collection.insert_one(reaction_in_db.dict(by_alias=True))
    reaction_in_db.id = result.inserted_id
    return reaction_in_db

async def delete_reaction(post_id: str, user_id: str) -> bool:
    result = await reactions_collection.delete_one({
        "post_id": ObjectId(post_id),
        "user_id": ObjectId(user_id)
    })
    return result.deleted_count > 0

async def get_reactions_by_post_id(post_id: str) -> List[ReactionInDB]:
    cursor = reactions_collection.find({"post_id": ObjectId(post_id)})
    reactions = await cursor.to_list(length=100)
    return [ReactionInDB(**reaction) for reaction in reactions]

async def get_reaction_counts_by_post_id(post_id: str) -> dict:
    pipeline = [
        {"$match": {"post_id": ObjectId(post_id)}},
        {"$group": {"_id": "$reaction_type", "count": {"$sum": 1}}}
    ]
    
    cursor = reactions_collection.aggregate(pipeline)
    results = await cursor.to_list(length=10)
    
    counts = {reaction_type.value: 0 for reaction_type in ReactionType}
    for result in results:
        counts[result["_id"]] = result["count"]
    
    return counts