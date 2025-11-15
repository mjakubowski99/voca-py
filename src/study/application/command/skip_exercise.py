from src.shared.flashcard.contracts import IFlashcardFacade
from src.shared.user.iuser import IUser
from src.shared.value_objects.flashcard_id import FlashcardId
from src.study.domain.value_objects import ExerciseId
from src.study.application.repository.contracts import (
    ISessionRepository,
    IUnscrambleWordExerciseRepository,
    IWordMatchExerciseRepository,
)
from src.study.application.dto.rating_context import RatingContext
from src.study.domain.enum import Rating


class SkipExercise:
    def __init__(
        self,
        unscramble_repository: IUnscrambleWordExerciseRepository,
        word_match_repository: IWordMatchExerciseRepository,
        session_repository: ISessionRepository,
        flashcard_facade: IFlashcardFacade,
    ):
        self.unscramble_repository = unscramble_repository
        self.word_match_repository = word_match_repository
        self.flashcard_facade = flashcard_facade
        self.session_repository = session_repository

    async def handle_unscramble(self, user: IUser, exercise_id: ExerciseId):
        exercise = await self.unscramble_repository.find(exercise_id)

        exercise.skip_exercise()

        await self.unscramble_repository.save(exercise)

        await self.session_repository.update_flashcard_rating_by_entry_id(
            entry_id=exercise.exercise_entries[0].id,
            rating=Rating.UNKNOWN,
        )

        await self.__save_rating_for_skipped_step(user, exercise.exercise_entries[0].flashcard_id)

    async def handle_word_match(self, user: IUser, exercise_id: ExerciseId):
        exercise = await self.word_match_repository.find(exercise_id)

        exercise.skip_exercise()

        await self.word_match_repository.save(exercise)

        for entry in exercise.word_match_entries:
            if entry.is_answered():
                continue

            await self.__save_rating_for_skipped_step(user, entry.flashcard_id)

    async def __save_rating_for_skipped_step(self, user: IUser, flashcard_id: FlashcardId):
        await self.flashcard_facade.new_rating(
            RatingContext(user=user, flashcard_id=flashcard_id, rating=Rating.UNKNOWN)
        )
