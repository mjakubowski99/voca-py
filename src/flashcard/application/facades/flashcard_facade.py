from typing import List
from src.flashcard.application.dto.context import Context
from src.flashcard.application.dto.flashcard_group import FlashcardGroup, FlashcardGroupItem
from src.flashcard.application.repository.contracts import (
    IFlashcardDeckRepository,
    IFlashcardRepository,
    IStoryRepository,
)
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
from src.shared.flashcard.contracts import IFlashcardGroup
from src.shared.user.iuser import IUser
from src.shared.value_objects.user_id import UserId


class FlashcardFacade(IFlashcardFacade):
    def __init__(
        self,
        selector: IFlashcardSelector,
        algorithm: IRepetitionAlgorithm,
        poll_manager: FlashcardPollManager,
        repository: IFlashcardRepository,
        story_repository: IStoryRepository,
        deck_repository: IFlashcardDeckRepository,
    ):
        self.selector = selector
        self.poll_manager = poll_manager
        self.algorithm = algorithm
        self.flashcard_repository = repository
        self.story_repository = story_repository
        self.deck_repository = deck_repository

    async def get_flashcard(self, id: FlashcardId) -> IFlashcard:
        return (await self.flashcard_repository.find_many([id]))[0]

    async def pick_flashcard(self, context: IPickingContext) -> IFlashcard:
        return (await self.pick_flashcards(context, 1))[0]

    async def pick_flashcards(self, context: IPickingContext, limit: int) -> List[IFlashcard]:
        if context.get_current_count() == 0:
            await self.poll_manager.refresh(
                user_id=context.get_user().get_id(),
                front=context.get_user().get_user_language(),
                back=context.get_user().get_learning_language(),
            )

        algo_context = Context(
            user_id=context.get_user().get_id(),
            max_flashcards_count=context.get_max_flashcards_count(),
            current_session_flashcards_count=context.get_current_count(),
            has_flashcard_poll=context.get_flashcard_deck_id() is not None,
            has_deck=context.get_flashcard_deck_id() is not None,
        )

        return await self.selector.select(
            algo_context,
            limit,
            context.get_user().get_user_language().get_enum(),
            context.get_user().get_learning_language().get_enum(),
            [],
        )

    async def pick_group(self, context: IPickingContext) -> IFlashcardGroup:
        flashcard = await self.pick_flashcard(context)

        story_id = await self.story_repository.find_random_story_id_by_flashcard_id(
            flashcard.get_flashcard_id()
        )

        if story_id is None:
            flashcards = await self.pick_flashcards(context, 3)
            return FlashcardGroup(
                story_id=None,
                flashcards=[
                    FlashcardGroupItem(
                        index=index,
                        flashcard=flashcard,
                    )
                    for index, flashcard in enumerate(flashcards)
                ],
            )
        else:
            return await self.story_repository.find(story_id, context.get_user().get_id())

    async def new_rating(self, rating_context: IRatingContext):
        await self.algorithm.handle(
            FlashcardId(value=rating_context.get_flashcard_id().get_value()),
            rating_context.get_user().get_id(),
            rating_context.get_rating(),
        )

    async def delete_user_data(self, user_id: UserId):
        await self.deck_repository.delete_all_for_user(user_id)

    async def post_language_update(self, user: IUser):
        """Clear flashcard poll after language preferences update."""
        await self.poll_manager.clear(user.get_id())
