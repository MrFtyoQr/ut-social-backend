from typing import Optional
from bson import ObjectId
from app.db.mongodb import users_collection
from app.models.user import UserCreate, UserInDB
from app.core.security import get_password_hash, verify_password

async def get_user_by_email(email: str) -> Optional[UserInDB]:
    user = await users_collection.find_one({"email": email})
    if user:
        return UserInDB(**user)
    return None

async def get_user_by_username(username: str) -> Optional[UserInDB]:
    user = await users_collection.find_one({"username": username})
    if user:
        return UserInDB(**user)
    return None

async def get_user_by_id(user_id: str) -> Optional[UserInDB]:
    user = await users_collection.find_one({"_id": ObjectId(user_id)})
    if user:
        return UserInDB(**user)
    return None

async def create_user(user_in: UserCreate) -> UserInDB:
    user = await get_user_by_email(user_in.email)
    if user:
        raise ValueError("Email already registered")
    
    username_exists = await get_user_by_username(user_in.username)
    if username_exists:
        raise ValueError("Username already taken")
    
    user_in_db = UserInDB(
        email=user_in.email,
        username=user_in.username,
        hashed_password=get_password_hash(user_in.password)
    )
    
    result = await users_collection.insert_one(user_in_db.dict(by_alias=True))
    user_in_db.id = str(result.inserted_id)  # ✅ Convertimos ObjectId a str
    
    return user_in_db  # ✅ Ahora FastAPI lo aceptará sin errores


async def authenticate_user(email: str, password: str) -> Optional[UserInDB]:
    user = await get_user_by_email(email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

async def update_profile_picture(user_id: str, profile_picture_id: str) -> bool:
    result = await users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"profile_picture": profile_picture_id}}
    )
    return result.modified_count > 0