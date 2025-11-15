from core.generics import ResponseWrapper
from src.flashcard.application.dto.rating_stats import RatingStats
from src.flashcard.infrastructure.http.response import RatingStat, RatingStatsResponse
from src.study.domain.models.exercise_entry.word_match_exercise_entry import WordMatchExerciseEntry
from src.study.domain.models.learning_session import LearningSession
from src.study.domain.models.learning_session_step import LearningSessionStep
from src.study.infrastructure.http.response import (
    LearningSessionResponse,
    FlashcardResponse,
    SessionDetailsResponse,
    UnscrambleWordExerciseResponse,
    WordMatchExerciseResponse,
    ExerciseWrapperResponse,
)
from src.study.domain.enum import ExerciseType
from typing import List, Callable, Optional


def _map_flashcard(step: LearningSessionStep) -> FlashcardResponse:
    exercise = step.flashcard_exercise
    return FlashcardResponse(
        id=step.id.get_value(),
        front_word=exercise.get_front_word(),
        front_lang=exercise.get_front_lang().get_enum(),
        back_word=exercise.get_back_word(),
        back_lang=exercise.get_back_lang().get_enum(),
        front_context=exercise.get_front_context(),
        back_context=exercise.get_back_context(),
        emoji=exercise.get_emoji().emoji if exercise.get_emoji() else None,
        owner_type=exercise.get_owner_type(),
    )


def _map_unscramble_exercise(step: LearningSessionStep) -> UnscrambleWordExerciseResponse:
    exercise = step.unscramble_word_exercise
    return UnscrambleWordExerciseResponse(
        id=exercise.id.get_value(),
        exercise_entry_id=exercise.exercise_entries[0].id.get_value(),
        front_word=exercise.word,
        context_sentence=exercise.context_sentence,
        context_sentence_translation=exercise.context_sentence_translation,
        back_word=exercise.word_translation,
        emoji=exercise.emoji.emoji if exercise.emoji else None,
        keyboard=exercise.get_keyboard(),
        indexed_keyboard=exercise.get_indexed_keyboard(),
    )


def _map_word_match_entry(
    entry: WordMatchExerciseEntry, exercise_id: int, is_story: bool, options: list
) -> WordMatchExerciseResponse:
    return WordMatchExerciseResponse(
        id=entry.id.get_value(),
        is_finished=entry.is_answered(),
        exercise_id=exercise_id,
        is_story=is_story,
        word=entry.word,
        word_translation=entry.word_translation,
        sentence_part_before_word=entry.get_sentence_part_before_word(),
        sentence_part_after_word=entry.get_sentence_part_after_word(),
        options=options,
        previous_entries=[],
    )


def _map_word_match_exercise(step: LearningSessionStep) -> WordMatchExerciseResponse:
    exercise = step.word_match_exercise
    current_entry = exercise.get_current_entry()
    exercise_id = exercise.id.get_value()
    is_story = exercise.is_story()
    options = exercise.options

    answered_entries = [
        _map_word_match_entry(entry, exercise_id, is_story, options)
        for entry in exercise.get_answered_entries()
    ]

    return WordMatchExerciseResponse(
        id=current_entry.id.get_value(),
        is_finished=current_entry.is_answered(),
        exercise_id=exercise_id,
        is_story=is_story,
        word=current_entry.word,
        word_translation=current_entry.word_translation,
        sentence_part_before_word=current_entry.get_sentence_part_before_word(),
        sentence_part_after_word=current_entry.get_sentence_part_after_word(),
        options=options,
        previous_entries=answered_entries,
    )


def _map_exercise(
    step: LearningSessionStep,
    links: Optional[List[str]] = None,
    get_links: Optional[Callable[[LearningSessionStep], List[str]]] = None,
) -> ExerciseWrapperResponse:
    exercise_type = step.get_exercise_type()

    # Get links - either from parameter, callable, or empty list
    if get_links is not None:
        exercise_links = get_links(step)
    elif links is not None:
        exercise_links = links
    else:
        exercise_links = []

    if exercise_type == ExerciseType.UNSCRAMBLE_WORDS:
        exercise_data = _map_unscramble_exercise(step)
    elif exercise_type == ExerciseType.WORD_MATCH:
        exercise_data = _map_word_match_exercise(step)
    else:
        raise ValueError(f"Unknown exercise type: {exercise_type}")

    return ExerciseWrapperResponse(
        exercise_type=exercise_type,
        links=exercise_links,
        data=exercise_data,
    )


def _is_exercise_mode(session: LearningSession) -> bool:
    if not session.new_steps:
        return False
    return session.new_steps[-1].get_exercise_type() is not None


def learning_session_response_mapper(
    session: LearningSession,
    links: Optional[List[str]] = None,
    get_links: Optional[Callable[[LearningSessionStep], List[str]]] = None,
) -> ResponseWrapper[LearningSessionResponse]:
    flashcard_steps = [step for step in session.new_steps if step.get_exercise_type() is None]

    exercise_steps = [step for step in session.new_steps if step.get_exercise_type() is not None]

    return ResponseWrapper[LearningSessionResponse](
        data=LearningSessionResponse(
            session=SessionDetailsResponse(
                id=session.id.get_value(),
                cards_per_session=session.limit,
                is_finished=session.is_finished(),
                progress=session.progress,
                is_exercise_mode=_is_exercise_mode(session),
                score=0,
                next_flashcards=[_map_flashcard(step) for step in flashcard_steps],
                next_exercises=[
                    _map_exercise(step, links=links, get_links=get_links) for step in exercise_steps
                ],
            )
        )
    )


def rating_stats_response_mapper(rating_stats: RatingStats) -> ResponseWrapper[RatingStatsResponse]:
    return ResponseWrapper[RatingStatsResponse](
        data=RatingStatsResponse(
            stats=[
                RatingStat(
                    rating=rating.rating,
                    rating_percentage=rating.rating_percentage,
                )
                for rating in rating_stats.stats
            ]
        )
    )
