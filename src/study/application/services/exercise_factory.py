from random import shuffle
from src.shared.flashcard.contracts import IFlashcard, IFlashcardFacade
from src.study.application.dto.picking_context import PickingContext
from src.study.application.repository.contracts import (
    IUnscrambleWordExerciseRepository,
    IWordMatchExerciseRepository,
)
from src.study.domain.enum import ExerciseStatus
from src.study.domain.models.exercise.unscramble_word_exercise import UnscrambleWordExercise
from src.study.domain.models.exercise_entry.word_match_exercise_entry import WordMatchExerciseEntry
from src.study.domain.models.learning_session import LearningSession
from src.study.domain.models.exercise.word_match_exercise import WordMatchExercise
from src.study.domain.value_objects import ExerciseEntryId, ExerciseId
from src.study.domain.models.answer.word_match_answer import WordMatchAnswer


class ExerciseFactory:
    def __init__(
        self,
        flashcard_facade: IFlashcardFacade,
        unscramble_word_repository: IUnscrambleWordExerciseRepository,
        word_match_exercise_repository: IWordMatchExerciseRepository,
    ) -> None:
        self.flashcard_facade = flashcard_facade
        self.unscramble_word_repository = unscramble_word_repository
        self.word_match_exercise_repository = word_match_exercise_repository

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

    async def build_word_match(self, context: PickingContext) -> WordMatchExercise:
        flashcard_group = await self.flashcard_facade.pick_group(context)

        exclude_flashcard_ids = [
            flashcard.get_flashcard().get_flashcard_id()
            for flashcard in flashcard_group.get_flashcards()
        ]

        context.exclude_flashcard_ids.extend(exclude_flashcard_ids)

        flashcards = await self.flashcard_facade.pick_flashcards(context, 3)

        answer_options = [flashcard.get_back_word() for flashcard in flashcards]

        answer_options.extend(
            [
                flashcard.get_flashcard().get_back_word()
                for flashcard in flashcard_group.get_flashcards()
            ]
        )

        shuffle(answer_options)

        exercise = WordMatchExercise(
            story_id=flashcard_group.get_story_id(),
            exercise_id=ExerciseId.no_id(),
            user_id=context.user.get_id(),
            status=ExerciseStatus.NEW,
            exercise_entries=[
                WordMatchExerciseEntry(
                    id=ExerciseEntryId.no_id(),
                    exercise_id=ExerciseId.no_id(),
                    flashcard_id=flashcard.get_flashcard().get_flashcard_id(),
                    word=flashcard.get_flashcard().get_front_word(),
                    word_translation=flashcard.get_flashcard().get_back_word(),
                    sentence=flashcard.get_flashcard().get_front_context(),
                    order=flashcard.get_index(),
                    correct_answer=WordMatchAnswer(
                        answer_entry_id=ExerciseEntryId.no_id(),
                        word=flashcard.get_flashcard().get_back_word(),
                    ),
                    last_user_answer=None,
                    last_answer_correct=None,
                    score=0.0,
                    answers_count=0,
                    updated=False,
                )
                for flashcard in flashcard_group.get_flashcards()
            ],
            options=answer_options,
        )

        return await self.word_match_exercise_repository.create(exercise)
