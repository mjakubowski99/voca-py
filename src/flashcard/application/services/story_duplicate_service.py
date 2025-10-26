from src.flashcard.application.dto.resolved_deck import ResolvedDeck
from src.flashcard.domain.models.story_collection import StoryCollection
from src.flashcard.application.services.flashcard_duplicate_service import FlashcardDuplicateService


class StoryDuplicateService:
    def __init__(self, duplicate_service: FlashcardDuplicateService):
        self.duplicate_service = duplicate_service

    async def remove_duplicates(
        self, deck: ResolvedDeck, stories: StoryCollection, words_count_to_save: int
    ) -> StoryCollection:
        """
        Removes duplicates from the story collection both within itself
        and against the existing flashcards in the deck.
        Only keeps up to `words_count_to_save` flashcards.
        """
        # 1️⃣ Remove duplicates using the duplicate service
        story_flashcards = await self.duplicate_service.remove_duplicates(deck.get_deck(), stories)

        # 2️⃣ Limit the number of flashcards to save
        story_flashcards = story_flashcards[:words_count_to_save]

        # 3️⃣ Update the story collection by removing duplicates
        stories.pull_stories_with_duplicates(story_flashcards)

        return stories
