from core.logging import logger
from src.shared.flashcard.contracts import IFlashcardFacade
from src.shared.user.iuser import IUser
from src.study.application.dto.rating_context import RatingContext
from src.study.application.repository.contracts import (
    ISessionRepository,
    IUnscrambleWordExerciseRepository,
)
from src.study.domain.enum import Rating
from src.study.domain.models.answer.unscramble_word_answer import UnscrambleWordAnswer
from src.study.domain.models.answer.word_match_answer import WordMatchAnswer
from src.study.domain.models.exercise.exercise import Exercise
from src.study.domain.value_objects import ExerciseEntryId, ExerciseId
from src.study.application.repository.contracts import IWordMatchExerciseRepository


class AnswerExercise:
    def __init__(
        self,
        repository: IUnscrambleWordExerciseRepository,
        word_match_repository: IWordMatchExerciseRepository,
        session_repository: ISessionRepository,
        flashcard_facade: IFlashcardFacade,
    ):
        self.unscramble_repository = repository
        self.word_match_repository = word_match_repository
        self.session_repository = session_repository
        self.flashcard_facade = flashcard_facade

    async def handle_unscramble(
        self, user: IUser, entry_id: ExerciseEntryId, unscrambled_word: str, hints_count: int
    ) -> None:
        exercise = await self.unscramble_repository.find_by_entry_id(entry_id)

        exercise.assess_answer(
            answer=UnscrambleWordAnswer(
                answer_entry_id=entry_id, unscrambled_word=unscrambled_word, hints_count=hints_count
            )
        )

        await self.unscramble_repository.save(exercise)

        await self._save_ratings(user, exercise)

    async def handle_word_match(self, user: IUser, exercise_entry_id: ExerciseEntryId, answer: str):
        exercise = await self.word_match_repository.find_by_entry_id(exercise_entry_id)

        exercise.assess_answer(
            answer=WordMatchAnswer(answer_entry_id=exercise_entry_id, word=answer)
        )

        await self.word_match_repository.save(exercise)

        await self._save_ratings(user, exercise, save_only_completed=True)

    async def _save_ratings(
        self, user: IUser, exercise: Exercise, save_only_completed: bool = False
    ):
        for entry in exercise.get_updated_entries():
            if save_only_completed and not entry.is_last_answer_correct():
                continue

            rating = Rating.from_score(entry.score)
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
