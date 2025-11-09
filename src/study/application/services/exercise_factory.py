from src.shared.flashcard.contracts import IFlashcard, IFlashcardFacade
from src.study.application.dto.picking_context import PickingContext
from src.study.application.repository.contracts import IUnscrambleWordExerciseRepository
from src.study.domain.models.exercise.unscramble_word_exercise import UnscrambleWordExercise
from src.study.domain.models.learning_session import LearningSession


class ExerciseFactory:
    def __init__(
        self,
        flashcard_facade: IFlashcardFacade,
        unscramble_word_repository: IUnscrambleWordExerciseRepository,
    ) -> None:
        self.flashcard_facade = flashcard_facade
        self.unscramble_word_repository = unscramble_word_repository

    async def build_flashcard(self, context: PickingContext) -> IFlashcard:
        return await self.flashcard_facade.pick_flashcard(context)

    async def build_unscramble_words(self, context: PickingContext) -> UnscrambleWordExercise:
        flashcard = await self.flashcard_facade.pick_flashcard(context)

        exercise = UnscrambleWordExercise.new_exercise(
            user_id=context.user.get_id(),
            flashcard_id=flashcard.get_flashcard_id(),
            word=flashcard.get_front_word(),
            word_translation=flashcard.get_back_word(),
            context_sentence=flashcard.get_front_context(),
            context_sentence_translation=flashcard.get_back_context(),
            emoji=flashcard.get_emoji(),
        )

        return await self.unscramble_word_repository.create(exercise)
