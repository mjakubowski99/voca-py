from pydantic import BaseModel
from src.shared.enum import Language
from src.shared.value_objects.user_id import UserId
from src.flashcard.domain.value_objects import SessionId
from src.flashcard.application.repository.contracts import INextSessionFlashcardsRepository
from src.flashcard.application.services.iflashcard_selector import IFlashcardSelector
from src.flashcard.domain.services.session_flashcards_service import SessionFlashcardsService
from src.flashcard.application.exercise.flashcard_summary_factory import FlashcardSummaryFactory
from src.shared.exercise.contracts import IFlashcardExerciseFacade


class AddSessionFlashcards(BaseModel):
    session_id: SessionId
    user_id: UserId
    front: Language
    back: Language
    limit: int


class AddSessionFlashcardsHandler:
    def __init__(
        self,
        next_session_flashcards_repository: INextSessionFlashcardsRepository,
        selector: IFlashcardSelector,
        service: SessionFlashcardsService,
        facade: IFlashcardExerciseFacade,
        flashcard_summary_factory: FlashcardSummaryFactory,
    ):
        self.next_session_flashcards_repository = next_session_flashcards_repository
        self.selector = selector
        self.service = service
        self.facade = facade
        self.flashcard_summary_factory = flashcard_summary_factory

    async def handle(self, command: AddSessionFlashcards, display_limit: int = 1) -> None:
        next_session_flashcards = await self.next_session_flashcards_repository.find(
            command.session_id
        )

        if next_session_flashcards.unrated_count >= display_limit:
            return

        flashcards = await self.selector.select(
            next_session_flashcards,
            command.limit,
            command.front,
            command.back,
        )

        exercise_type = next_session_flashcards.resolve_exercise_by_rating(
            flashcards[0].last_user_rating
        )

        if exercise_type:
            summary_factory = self.flashcard_summary_factory.make(exercise_type)

            flashcard_summaries = await summary_factory.make(next_session_flashcards, flashcards[0])

            next_session_flashcards.add_flashcards_from_summaries(flashcard_summaries)

            exercise_entries = await self.facade.build_exercise(
                flashcard_summaries, command.user_id, exercise_type
            )

            next_session_flashcards.associate_exercise_entries(exercise_entries, exercise_type)
        else:
            next_session_flashcards = await self.service.add(next_session_flashcards, flashcards)

        await self.next_session_flashcards_repository.save(next_session_flashcards)
