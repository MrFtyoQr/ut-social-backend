from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Response
from typing import Any, List, Optional
from app.services.post_service import (
    create_post, get_posts, get_post_by_id, delete_post
)
from app.services.user_service import get_user_by_id
from app.models.post import Post, PostCreate
from app.models.user import UserInDB
from app.api.deps import get_current_user
from app.db.mongodb import fs
from bson import ObjectId
from gridfs.errors import NoFile

router = APIRouter()

@router.post("/", response_model=Post, status_code=status.HTTP_201_CREATED)
async def create_new_post(
    content: str = Form(...),
    career: str = Form(...),
    files: List[UploadFile] = File(default_factory=list),  # ✅ Cambia None por `default_factory=list`
    current_user: UserInDB = Depends(get_current_user)
) -> Any:
    post_in = PostCreate(content=content, career=career)
    post = await create_post(post_in, str(current_user.id), files)
    
    # Enriquecer el post con datos del usuario
    post_dict = post.dict(by_alias=True)
    post_dict["user"] = {
        "id": str(current_user.id),
        "username": current_user.username,
        "profile_picture": current_user.profile_picture
    }
    
    return Post(**post_dict)

@router.get("/", response_model=List[Post])
async def read_posts(
    skip: int = 0,
    limit: int = 20,
    career: Optional[str] = None,
    current_user: UserInDB = Depends(get_current_user)
) -> Any:
    posts = await get_posts(skip, limit, career) or []  # ✅ Asegura que siempre devuelve una lista

    enriched_posts = []
    for post in posts:
        user = await get_user_by_id(str(post.user_id))
        if not user:
            continue  # ✅ Evita errores si el usuario no existe

        post_dict = post.dict(by_alias=True)
        post_dict["user"] = {
            "id": str(user.id),
            "username": user.username,
            "profile_picture": user.profile_picture
        }
        enriched_posts.append(Post(**post_dict))

    return enriched_posts

@router.get("/{post_id}", response_model=Post)
async def read_post(
    post_id: str,
    current_user: UserInDB = Depends(get_current_user)
) -> Any:
    post = await get_post_by_id(post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    # Enriquecer el post con datos del usuario
    user = await get_user_by_id(str(post.user_id))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    post_dict = post.dict(by_alias=True)
    post_dict["user"] = {
        "id": str(user.id),
        "username": user.username,
        "profile_picture": user.profile_picture
    }
    
    return Post(**post_dict)

@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_post(
    post_id: str,
    current_user: UserInDB = Depends(get_current_user)
) -> None:
    success = await delete_post(post_id, str(current_user.id))
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found or you don't have permission to delete it"
        )
    # ✅ No `return` necesario, FastAPI manejará 204 correctamente

@router.get("/file/{file_id}")
async def get_file(file_id: str) -> Any:
    try:
        file = fs.get(ObjectId(file_id))
        return Response(
            content=file.read(),
            media_type=file.content_type
        )
    except NoFile:  # ✅ Captura correctamente el error de archivo no encontrado
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
