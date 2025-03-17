from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Response, status, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from typing import Any, List
from app.core.config import settings
from app.core.security import create_access_token
from app.services.user_service import (
    authenticate_user, create_user, get_user_by_id, update_profile_picture
)
from app.services.post_service import get_posts_by_user_id
from app.models.user import User, UserCreate, UserInDB
from app.models.post import Post
from app.api.deps import get_current_user
from app.db.mongodb import fs
import io
from gridfs.errors import NoFile

router = APIRouter()

@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register_user(user_in: UserCreate) -> Any:
    try:
        user = await create_user(user_in)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()) -> Any:
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=str(user.id), expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": str(user.id),
            "email": user.email,
            "username": user.username,
            "profile_picture": user.profile_picture
        }
    }

@router.get("/me", response_model=User)
async def get_current_user_info(current_user: UserInDB = Depends(get_current_user)) -> Any:
    return current_user

@router.get("/{user_id}", response_model=User)
async def get_user_info(user_id: str) -> Any:
    user = await get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return User(
        id=str(user.id),
        email=user.email,
        username=user.username,
        profile_picture=user.profile_picture
    )

@router.get("/{user_id}/posts", response_model=List[Post])
async def get_user_posts(
    user_id: str,
    skip: int = 0,
    limit: int = 20,
    current_user: UserInDB = Depends(get_current_user)
) -> Any:
    posts = await get_posts_by_user_id(user_id, skip, limit) or []

    # Enriquecer los posts con información del usuario
    enriched_posts = []
    for post in posts:
        user = await get_user_by_id(str(post.user_id))
        if not user:
            continue  # Evitar errores si el usuario no existe

        post_dict = post.dict(by_alias=True)
        post_dict["user"] = {
            "id": str(user.id),
            "username": user.username,
            "profile_picture": user.profile_picture
        }
        enriched_posts.append(Post(**post_dict))

    return enriched_posts

@router.post("/profile-picture")
async def upload_profile_picture(
    file: UploadFile = File(...),
    current_user: UserInDB = Depends(get_current_user)
) -> Any:
    # Validar tipo de archivo
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an image"
        )
    
    content = await file.read()
    file_id = fs.put(
        io.BytesIO(content),
        filename=file.filename,
        content_type=file.content_type
    )
    
    # Actualizar la foto de perfil del usuario
    success = await update_profile_picture(str(current_user.id), str(file_id))
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update profile picture"
        )
    
    return {"profile_picture_id": str(file_id)}

@router.get("/profile-picture/{file_id}")
async def get_profile_picture(file_id: str) -> Any:
    try:
        file = fs.get(ObjectId(file_id))
        return Response(
            content=file.read(),
            media_type=file.content_type
        )
    except NoFile:  # ✅ Captura correctamente el error cuando el archivo no existe
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
# ✅ Código refactorizado y reutilizado en múltiples rutas