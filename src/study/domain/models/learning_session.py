from typing import List, Optional
from pydantic import BaseModel

from src.flashcard.domain.value_objects import FlashcardDeckId
from src.shared.flashcard.contracts import IFlashcard
from src.shared.value_objects.user_id import UserId
from src.study.domain.enum import LearningActivityType, Rating, SessionStatus, SessionType
from src.study.domain.models.exercise.word_match_exercise import WordMatchExercise
from src.study.domain.models.exercise.unscramble_word_exercise import UnscrambleWordExercise
from src.study.domain.value_objects import LearningSessionId, LearningSessionStepId
from src.study.domain.models.learning_session_step import LearningSessionStep


class LearningSession(BaseModel):
    id: LearningSessionId
    status: SessionStatus
    type: SessionType
    progress: int = 0
    limit: int
    new_steps: List[LearningSessionStep]

    model_config = {"arbitrary_types_allowed": True}

    @classmethod
    def new_session(
        user_id: UserId, deck_id: Optional[FlashcardDeckId], session_type: SessionType, limit: int
    ):
        return LearningSession(
            id=LearningSessionId.no_id(),
            user_id=user_id,
            deck_id=deck_id,
            status=SessionStatus.STARTED,
            progress=0,
            limit=limit,
            type=session_type,
        )

    def add_flashcard(self, step_id: LearningSessionStepId, flashcard: IFlashcard):
        self.new_steps.append(LearningSessionStep(id=step_id, rating=None, flashcard=flashcard))

    def add_unscramble_exercise(
        self, step_id: LearningSessionStepId, exercise: UnscrambleWordExercise
    ):
        self.new_steps.append(
            LearningSessionStep(id=step_id, rating=None, unscramble_word_exercise=exercise)
        )

    def add_word_match_exercise(self, step_id: LearningSessionStepId, exercise: WordMatchExercise):
        self.new_steps.append(
            LearningSessionStep(id=step_id, rating=None, word_match_exercise=exercise)
        )

    def pick_next_activity_type(self) -> LearningActivityType:
        import random

        match self.type:
            case SessionType.FLASHCARD:
                return LearningActivityType.FLASHCARDS
            case SessionType.UNSCRAMBLE_WORDS:
                return LearningActivityType.UNSCRAMBLE_WORDS
            case SessionType.MIXED:
                return random.choice(
                    [LearningActivityType.FLASHCARDS, LearningActivityType.UNSCRAMBLE_WORDS]
                )

    def needs_next(self):
        return True
