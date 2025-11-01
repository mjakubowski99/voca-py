import json
from typing import List
from src.flashcard.application.exercise.iflashcard_exercise_factory import IFlashcardExerciseFactory
from src.shared.util.cache import ICache
from src.shared.value_objects.user_id import UserId
from src.flashcard.domain.models.flashcard import Flashcard
from src.flashcard.domain.models.next_session_flashcards import NextSessionFlashcards
from src.flashcard.application.repository.contracts import IStoryRepository
from src.flashcard.application.services.iflashcard_selector import IFlashcardSelector
from src.flashcard.domain.models.session_flashcard_summaries import SessionFlashcardSummaries


class WordMatchExerciseFactory(IFlashcardExerciseFactory):
    FLASHCARDS_COUNT_TO_ADD = 2

    def __init__(
        self,
        repository: IStoryRepository,
        selector: IFlashcardSelector,
        cache: ICache,
    ):
        self.repository = repository
        self.selector = selector
        self.cache = cache

    async def make(
        self,
        next_session_flashcards: NextSessionFlashcards,
        base_flashcard: Flashcard,
    ) -> SessionFlashcardSummaries:
        key = self.get_cache_key(next_session_flashcards.user_id)
        latest_stories = await self.retrieve_stories_from_cache(key)

        story_id = await self.repository.find_random_story_id_by_flashcard(base_flashcard.id)

        if story_id and story_id.value not in latest_stories:
            latest_stories.append(story_id.value)
            await self.cache.put(key, json.dumps(latest_stories), ttl=5 * 60)

            story = await self.repository.find(story_id, next_session_flashcards.user_id)

            exclude_ids = [
                flashcard.flashcard.id
                for flashcard in story.story_flashcards  # type: StoryFlashcard
            ]

            flashcards = await self.selector.select(
                next_session_flashcards,
                3,
                base_flashcard.front_lang.enum,
                base_flashcard.back_lang.enum,
                [base_flashcard.id] + exclude_ids,
            )

            return SessionFlashcardSummaries.from_story(story, base_flashcard, flashcards)

        # fallback selection
        flashcards = await self.selector.select(
            next_session_flashcards,
            self.FLASHCARDS_COUNT_TO_ADD + 3,
            base_flashcard.front_lang.enum,
            base_flashcard.back_lang.enum,
            [base_flashcard.id],
        )

        flashcards = [base_flashcard] + flashcards

        return SessionFlashcardSummaries.from_flashcards(
            flashcards[: self.FLASHCARDS_COUNT_TO_ADD + 1],
            base_flashcard,
            flashcards[self.FLASHCARDS_COUNT_TO_ADD + 1 :],
        )

    def get_cache_key(self, user_id: UserId) -> str:
        return f"latest-stories:{user_id.value}"

    async def retrieve_stories_from_cache(self, key: str) -> List[int]:
        cached = await self.cache.get(key)
        return json.loads(cached) if cached else []
