from typing import List
from copy import deepcopy
from src.flashcard.domain.models.deck import Deck
from src.flashcard.domain.models.story_flashcard import StoryFlashcard
from src.flashcard.domain.models.story_collection import StoryCollection
from src.flashcard.application.repository.contracts import IFlashcardDuplicateRepository


class FlashcardDuplicateService:
    def __init__(self, duplicate_repository: IFlashcardDuplicateRepository):
        self.duplicate_repository = duplicate_repository

    async def remove_duplicates(self, deck: Deck, stories: StoryCollection) -> List[StoryFlashcard]:
        """
        Removes flashcards from the collection that are duplicates either within
        the collection itself or already existing in the deck.
        """
        # 1️⃣ Extract all front words (lowercased) from the story flashcards
        front_words = [
            sf.get_flashcard().front_word.lower() for sf in stories.get_all_story_flashcards()
        ]

        # 2️⃣ Keep only unique front words within this collection
        unique_words = list(dict.fromkeys(front_words))  # preserves order

        unique_flashcards: List[StoryFlashcard] = []
        for unique_word in unique_words:
            for sf in stories.get_all_story_flashcards():
                if sf.get_flashcard().front_word.lower() == unique_word:
                    unique_flashcards.append(deepcopy(sf))
                    break

        # 3️⃣ Remove flashcards already saved in the deck
        duplicated_words = await self.duplicate_repository.get_already_saved_front_words(
            deck.id, front_words
        )
        duplicated_words_lower = {word.lower() for word in duplicated_words}

        # 4️⃣ Filter out duplicates
        filtered_flashcards = [
            sf
            for sf in unique_flashcards
            if sf.get_flashcard().front_word.lower() not in duplicated_words_lower
        ]

        return filtered_flashcards
