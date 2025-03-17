from fastapi import APIRouter, Depends, HTTPException, status
from typing import Any, Dict, List
from app.services.interaction_service import (
    create_or_update_reaction, delete_reaction, 
    get_reactions_by_post_id, get_reaction_counts_by_post_id
)
from app.services.user_service import get_user_by_id
from app.models.interaction import Reaction, ReactionCreate
from app.models.user import UserInDB
from app.api.deps import get_current_user

router = APIRouter()

@router.post("/", response_model=Reaction, status_code=status.HTTP_201_CREATED)
async def create_new_reaction(
    reaction_in: ReactionCreate,
    current_user: UserInDB = Depends(get_current_user)
) -> Any:
    reaction = await create_or_update_reaction(reaction_in, str(current_user.id))
    
    # Enriquecer reacción con datos del usuario
    reaction_dict = reaction.dict(by_alias=True)
    reaction_dict["user"] = {
        "id": str(current_user.id),
        "username": current_user.username,
        "profile_picture": current_user.profile_picture
    }
    
    return Reaction(**reaction_dict)

@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_reaction(
    post_id: str,
    current_user: UserInDB = Depends(get_current_user)
) -> None:
    success = await delete_reaction(post_id, str(current_user.id))
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reaction not found"
        )
    # ✅ No retornar nada, FastAPI maneja `204 No Content` automáticamente

@router.get("/post/{post_id}", response_model=List[Reaction])
async def read_reactions(
    post_id: str,
    current_user: UserInDB = Depends(get_current_user)
) -> Any:
    reactions = await get_reactions_by_post_id(post_id) or []

    enriched_reactions = []
    for reaction in reactions:
        user = await get_user_by_id(str(reaction.user_id))
        if not user:
            continue
        reaction_dict = reaction.dict(by_alias=True)
        reaction_dict["user"] = {
            "id": str(user.id),
            "username": user.username,
            "profile_picture": user.profile_picture
        }
        enriched_reactions.append(Reaction(**reaction_dict))
    
    return enriched_reactions

@router.get("/post/{post_id}/counts", response_model=Dict[str, int])
async def read_reaction_counts(
    post_id: str,
    current_user: UserInDB = Depends(get_current_user)
) -> Any:
    counts = await get_reaction_counts_by_post_id(post_id)
    return counts
# ✅ ¡Listo! Ahora puedes obtener, crear y eliminar reacciones en tus publicaciones.