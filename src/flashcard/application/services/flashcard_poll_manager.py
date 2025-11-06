from src.shared.value_objects.user_id import UserId
from src.shared.value_objects.language import Language
from src.flashcard.domain.models.flashcard_poll import FlashcardPoll
from src.flashcard.application.repository.contracts import IFlashcardPollRepository
from src.flashcard.application.services.flashcard_poll_resolver import FlashcardPollResolver
from src.flashcard.application.services.iflashcard_selector import IFlashcardSelector


class FlashcardPollManager:
    def __init__(
        self,
        selector: IFlashcardSelector,
        repository: IFlashcardPollRepository,
        resolver: FlashcardPollResolver,
    ):
        self.selector = selector
        self.resolver = resolver
        self.repository = repository

    LEITNER_MAX_LEVEL: int = 30_000

    async def refresh(self, user_id: UserId, front: Language, back: Language) -> FlashcardPoll:
        poll = await self.resolver.resolve(user_id)

        if not poll.poll_is_full():
            flashcards = await self.selector.select_to_poll(
                user_id,
                poll.count_to_fill_poll(),
                front.get_enum(),
                back.get_enum(),
            )
            flashcard_ids = [f.get_id() for f in flashcards]
            poll.push(flashcard_ids)

        elif poll.are_flashcards_to_purge():
            limit = poll.get_count_to_purge()
            flashcards = await self.selector.select_to_poll(
                user_id,
                limit,
                front.get_enum(),
                back.get_enum(),
            )
            flashcard_ids = [f.get_id() for f in flashcards]
            poll.replace_with_new(flashcard_ids)

        await self.repository.save(poll)

        await self.repository.reset_leitner_level_if_max_level_exceeded(
            user_id, self.LEITNER_MAX_LEVEL
        )

        return poll

    async def clear(self, user_id: UserId) -> None:
        """Remove all flashcards for a given user."""
        await self.repository.delete_all_by_user_id(user_id)
