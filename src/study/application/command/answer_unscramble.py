from src.shared.flashcard.contracts import IFlashcardFacade
from src.study.application.repository.contracts import IUnscrambleWordExerciseRepository
from src.study.domain.enum import Rating
from src.study.domain.models.answer.answer import Answer
from src.study.domain.models.answer.unscramble_word_answer import UnscrambleWordAnswer
from src.study.domain.value_objects import ExerciseEntryId


class AnswerUnscramble:
    def __init__(
        self, repository: IUnscrambleWordExerciseRepository, flashcard_facade: IFlashcardFacade
    ):
        self.repository = repository
        self.flashcard_facade = flashcard_facade

    async def handle(self, entry_id: ExerciseEntryId):
        exercise = await self.repository.find_by_entry_id(entry_id)

        exercise.assess_answer(
            answer=UnscrambleWordAnswer(
                answer_entry_id=entry_id, unscrambled_word="test", hints_count=0
            )
        )

        self.repository.save(exercise)

        for entry in exercise.updated_entries:
            self.flashcard_facade.new_rating(entry.flashcard_id, Rating.from_score(entry.score))
