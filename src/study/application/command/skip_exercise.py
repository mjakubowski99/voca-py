from src.shared.flashcard.contracts import IFlashcardFacade
from src.study.domain.value_objects import ExerciseId
from src.study.application.repository.contracts import (
    IUnscrambleWordExerciseRepository,
    IWordMatchExerciseRepository,
)


class SkipExercise:
    def __init__(
        self,
        unscramble_repository: IUnscrambleWordExerciseRepository,
        word_match_repository: IWordMatchExerciseRepository,
        flashcard_facade: IFlashcardFacade,
    ):
        self.unscramble_repository = unscramble_repository
        self.word_match_repository = word_match_repository
        self.flashcard_facade = flashcard_facade

    async def handle_unscramble(self, exercise_id: ExerciseId):
        exercise = await self.repository.find(exercise_id)
        exercise.skip_exercise()
        self.repository.save(exercise)

    async def handle_word_match(self, exercise_id: ExerciseId):
        exercise = await self.repository.find(exercise_id)
        exercise.skip_exercise()
        self.repository.save(exercise)
