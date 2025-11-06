from src.flashcard.application.dto.context import Context
from src.flashcard.application.repository.contracts import IFlashcardRepository
from src.flashcard.application.services.flashcard_poll_manager import FlashcardPollManager
from src.flashcard.application.services.irepetition_algorithm import IRepetitionAlgorithm
from src.flashcard.domain.value_objects import FlashcardId
from src.shared.flashcard.contracts import (
    IFlashcard,
    IFlashcardFacade,
    IPickingContext,
    IRatingContext,
)
from src.flashcard.application.services.iflashcard_selector import IFlashcardSelector
from src.flashcard.domain.enum import Rating


class FlashcardFacade(IFlashcardFacade):
    def __init__(
        self,
        selector: IFlashcardSelector,
        algorithm: IRepetitionAlgorithm,
        poll_manager: FlashcardPollManager,
        repository: IFlashcardRepository,
    ):
        self.selector = selector
        self.poll_manager = poll_manager
        self.algorithm = algorithm
        self.flashcard_repository = repository

    async def get_flashcard(self, id: FlashcardId) -> IFlashcard:
        return await self.flashcard_repository.find_many([id])[0]

    async def pick_flashcard(self, context: IPickingContext) -> IFlashcard:
        # means session was newly created
        if context.get_current_count() == 0:
            await self.poll_manager.refresh(context.get_user().get_id())

        algo_context = Context(
            user_id=context.get_user_id(),
            max_flashcards_count=context.get_max_flashcards_count(),
            current_session_flashcards_count=context.get_current_count(),
            has_flashcard_poll=context.get_flashcard_deck_id() is not None,
            has_deck=context.get_flashcard_deck_id() is not None,
        )

        return self.selector.select(
            algo_context,
            1,
            context.get_user().get_user_language(),
            context.get_user().get_learning_language(),
            [],
        )

    async def new_rating(self, context: IRatingContext):
        await self.algorithm.handle(
            context.get_flashcard_id(), context.get_user().get_id(), context.get_rating()
        )
