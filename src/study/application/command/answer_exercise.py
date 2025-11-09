from src.shared.flashcard.contracts import IFlashcardFacade
from src.shared.user.iuser import IUser
from src.study.application.dto.rating_context import RatingContext
from src.study.application.repository.contracts import IUnscrambleWordExerciseRepository
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
        flashcard_facade: IFlashcardFacade,
    ):
        self.unscramble_repository = repository
        self.word_match_repository = word_match_repository
        self.flashcard_facade = flashcard_facade

    async def handle_unscramble(
        self, user: IUser, entry_id: ExerciseEntryId, unscrambled_word: str, hints_count: int
    ):
        exercise = await self.unscramble_repository.find_by_entry_id(entry_id)

        exercise.assess_answer(
            answer=UnscrambleWordAnswer(
                answer_entry_id=entry_id, unscrambled_word=unscrambled_word, hints_count=hints_count
            )
        )

        await self.unscramble_repository.save(exercise)

        await self._save_ratings(user, exercise)

    async def handle_word_match(
        self, user: IUser, exercise_id: ExerciseId, exercise_entry_id: ExerciseEntryId, answer: str
    ):
        exercise = await self.unscramble_repository.find(exercise_id)

        exercise.assess_answer(
            answer=WordMatchAnswer(answer_entry_id=exercise_entry_id, word=answer, hints_count=0)
        )

        await self._save_ratings(user, exercise)

    async def _save_ratings(self, user: IUser, exercise: Exercise):
        if exercise.is_completed():
            for entry in exercise.get_updated_entries():
                rating_context = RatingContext(
                    user=user,
                    flashcard_id=entry.flashcard_id,
                    rating=Rating.from_score(entry.score),
                )
                await self.flashcard_facade.new_rating(rating_context)
