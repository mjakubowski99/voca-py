from core.generics import ResponseWrapper
from src.study.domain.models.learning_session import LearningSession
from src.study.infrastructure.http.response import LearningSessionResponse
from src.study.infrastructure.http.response import FlashcardResponse
from src.study.infrastructure.http.response import UnscrambleWordExerciseResponse
from src.study.domain.enum import ExerciseType


def learning_session_response_mapper(
    session: LearningSession,
) -> ResponseWrapper[LearningSessionResponse]:
    return ResponseWrapper[LearningSessionResponse](
        data=[
            LearningSessionResponse(
                id=session.id.get_value(),
                cards_per_session=session.limit,
                is_finished=session.is_finished(),
                progress=session.progress,
                is_exercise_mode=session.new_steps[-1].get_exercise_type() is not None
                if len(session.new_steps) > 0
                else False,
                score=0,
                next_flashcards=[
                    FlashcardResponse(
                        id=step.id.get_value(),
                        front_word=step.flashcard_exercise.get_front_word(),
                        front_lang=step.flashcard_exercise.get_front_lang().get_enum(),
                        back_word=step.flashcard_exercise.get_back_word(),
                        back_lang=step.flashcard_exercise.get_back_lang().get_enum(),
                        front_context=step.flashcard_exercise.get_front_context(),
                        back_context=step.flashcard_exercise.get_back_context(),
                        emoji=step.flashcard_exercise.get_emoji().emoji
                        if step.flashcard_exercise.get_emoji()
                        else None,
                        owner_type=step.flashcard_exercise.get_owner_type(),
                    )
                    for step in session.new_steps
                    if step.get_exercise_type() is None
                ],
                next_exercises=[
                    (
                        UnscrambleWordExerciseResponse(
                            id=step.unscramble_word_exercise.id.get_value(),
                            exercise_entry_id=step.unscramble_word_exercise.exercise_entries[
                                0
                            ].id.get_value(),
                            front_word=step.unscramble_word_exercise.word,
                            context_sentence=step.unscramble_word_exercise.context_sentence,
                            context_sentence_translation=step.unscramble_word_exercise.context_sentence_translation,
                            back_word=step.unscramble_word_exercise.word_translation,
                            emoji=step.unscramble_word_exercise.emoji.emoji
                            if step.unscramble_word_exercise.emoji
                            else None,
                            keyboard=step.unscramble_word_exercise.get_keyboard(),
                            indexed_keyboard=step.unscramble_word_exercise.get_indexed_keyboard(),
                        )
                        if step.get_exercise_type() is ExerciseType.UNSCRAMBLE_WORDS
                        else []
                    )
                    for step in session.new_steps
                    if step.get_exercise_type() is not None
                ],
            )
        ]
    )
