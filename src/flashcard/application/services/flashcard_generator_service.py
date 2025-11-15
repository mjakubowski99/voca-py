from src.shared.value_objects.language import Language
from src.flashcard.application.dto.resolved_deck import ResolvedDeck
from src.flashcard.domain.models.flashcard_prompt import FlashcardPrompt
from src.flashcard.application.repository.contracts import IFlashcardDeckRepository
from src.flashcard.application.repository.contracts import IFlashcardRepository
from src.flashcard.application.repository.contracts import IStoryRepository
from src.flashcard.application.repository.contracts import IFlashcardDuplicateRepository
from src.flashcard.application.services.story_duplicate_service import StoryDuplicateService
from src.flashcard.application.services.iflashcard_generator import IFlashcardGenerator


class FlashcardGeneratorService:
    def __init__(
        self,
        deck_repository: IFlashcardDeckRepository,
        flashcard_repository: IFlashcardRepository,
        story_repository: IStoryRepository,
        generator: IFlashcardGenerator,
        duplicate_repository: IFlashcardDuplicateRepository,
        story_duplicate_service: StoryDuplicateService,
    ):
        self.deck_repository = deck_repository
        self.flashcard_repository = flashcard_repository
        self.story_repository = story_repository
        self.generator = generator
        self.duplicate_repository = duplicate_repository
        self.story_duplicate_service = story_duplicate_service

    async def generate(
        self,
        deck: ResolvedDeck,
        front: Language,
        back: Language,
        deck_name: str,
        words_count: int,
        words_count_to_save: int,
    ) -> int:
        """
        Generate flashcards with AI and handle duplicates.
        """
        try:
            # 1️⃣ Avoid letters that already exist in deck
            initial_letters_to_avoid = (
                await self.duplicate_repository.get_random_front_word_initial_letters(
                    deck.get_deck().id, 5
                )
            )

            default_language_level = deck.get_deck().default_language_level

            prompt = FlashcardPrompt(
                category=deck_name,
                language_level=default_language_level,
                word_lang=front,
                translation_lang=back,
                words_count=words_count,
                initial_letters_to_avoid=initial_letters_to_avoid,
            )

            # 2️⃣ Generate stories using AI generator
            stories = await self.generator.generate(deck.get_deck().owner, deck.get_deck(), prompt)

            # 3️⃣ Remove duplicates if needed
            if words_count > words_count_to_save:
                stories = await self.story_duplicate_service.remove_duplicates(
                    deck, stories, words_count_to_save
                )
                stories.pull_stories_with_only_one_sentence()

                pulled_flashcards = stories.get_pulled_flashcards()
                if pulled_flashcards:
                    await self.flashcard_repository.create_many(pulled_flashcards)

            # 4️⃣ Save all stories
            if stories.get():
                await self.story_repository.save_many(stories)

            # 5️⃣ Return total flashcard count
            return stories.get_all_flashcards_count()

        except Exception:
            # Rollback deck if it’s newly created
            if not deck.is_existing_deck:
                await self.deck_repository.remove(deck.get_deck())
            raise
