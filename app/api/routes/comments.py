from fastapi import APIRouter, Depends, HTTPException, status
from typing import Any, List
from app.services.interaction_service import (
    create_comment, get_comments_by_post_id, delete_comment
)
from app.services.user_service import get_user_by_id
from app.models.interaction import Comment, CommentCreate
from app.models.user import UserInDB
from app.api.deps import get_current_user

router = APIRouter()

@router.post("/", response_model=Comment, status_code=status.HTTP_201_CREATED)
async def create_new_comment(
    comment_in: CommentCreate,
    current_user: UserInDB = Depends(get_current_user)
) -> Any:
    comment = await create_comment(comment_in, str(current_user.id))
    
    # Enriquecer comentario con datos del usuario
    comment_dict = comment.dict(by_alias=True)
    comment_dict["user"] = {
        "id": str(current_user.id),
        "username": current_user.username,
        "profile_picture": current_user.profile_picture
    }
    
    return Comment(**comment_dict)

@router.get("/post/{post_id}", response_model=List[Comment])
async def read_comments(
    post_id: str,
    skip: int = 0,
    limit: int = 50,
    current_user: UserInDB = Depends(get_current_user)
) -> Any:
    comments = await get_comments_by_post_id(post_id, skip, limit) or []
    
    # Enriquecer comentarios con datos del usuario
    enriched_comments = []
    for comment in comments:
        user = await get_user_by_id(str(comment.user_id))
        if not user:
            continue
        comment_dict = comment.dict(by_alias=True)
        comment_dict["user"] = {
            "id": str(user.id),
            "username": user.username,
            "profile_picture": user.profile_picture
        }
        enriched_comments.append(Comment(**comment_dict))
    
    return enriched_comments

@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_comment(
    comment_id: str,
    current_user: UserInDB = Depends(get_current_user)
) -> None:
    success = await delete_comment(comment_id, str(current_user.id))
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found or you don't have permission to delete it"
        )
    # ✅ No retornar nada, FastAPI maneja `204 No Content` automáticamente
#