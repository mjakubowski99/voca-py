from src.shared.flashcard.contracts import IFlashcardFacade
from src.shared.user.iuser import IUser
from src.shared.value_objects.flashcard_id import FlashcardId
from src.study.domain.models.exercise.exercise import Exercise
from src.study.domain.value_objects import ExerciseEntryId, ExerciseId
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

        await self._save_unknown_ratings(user, exercise)

    async def handle_word_match(self, user: IUser, exercise_id: ExerciseId):
        exercise = await self.word_match_repository.find(exercise_id)

        exercise.skip_exercise()

        await self.word_match_repository.save(exercise)

        await self._save_unknown_ratings(user, exercise)

    async def _save_unknown_ratings(self, user: IUser, exercise: Exercise):
        for entry in exercise.exercise_entries:
            if entry.answers_count > 0:
                continue

            rating = Rating.UNKNOWN
            rating_context = RatingContext(
                user=user, flashcard_id=entry.flashcard_id, rating=rating
            )
            await self._save_rating_by_entry_id(user, entry.id, rating)
            await self.flashcard_facade.new_rating(rating_context)

    async def _save_rating_by_entry_id(
        self, user: IUser, entry_id: ExerciseEntryId, rating: Rating
    ):
        await self.session_repository.update_flashcard_rating_by_entry_id(
            entry_id=entry_id,
            rating=rating,
        )
