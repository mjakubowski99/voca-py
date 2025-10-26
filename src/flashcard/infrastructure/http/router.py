from fastapi import APIRouter, Depends
from core.auth import get_current_user
from src.flashcard.application.command.generate_flashcards import GenerateFlashcardsHandler
from src.shared.user.iuser import IUser
from core.container import container

router = APIRouter()


@router.post("/api/flashcards/generate")
async def generate_flashcards(
    user: IUser = Depends(get_current_user),
    generate_flashcards: GenerateFlashcardsHandler = Depends(
        lambda: container.resolve(GenerateFlashcardsHandler)
    ),
):
    pass
