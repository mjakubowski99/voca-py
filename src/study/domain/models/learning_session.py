from random import vonmisesvariate
from typing import List, Optional
from pydantic import BaseModel

from src.shared.value_objects.flashcard_deck_id import FlashcardDeckId
from src.shared.flashcard.contracts import IFlashcard
from src.shared.value_objects.user_id import UserId
from src.study.domain.enum import LearningActivityType, SessionStatus, SessionType
from src.study.domain.models.exercise.word_match_exercise import WordMatchExercise
from src.study.domain.models.exercise.unscramble_word_exercise import UnscrambleWordExercise
from src.study.domain.value_objects import LearningSessionId, LearningSessionStepId
from src.study.domain.models.learning_session_step import LearningSessionStep


class LearningSession(BaseModel):
    id: LearningSessionId
    status: SessionStatus
    user_id: UserId
    type: SessionType
    progress: int = 0
    limit: int
    deck_id: Optional[FlashcardDeckId]
    device: str
    new_steps: List[LearningSessionStep]

    model_config = {"arbitrary_types_allowed": True}

    @classmethod
    def new_session(
        cls,
        user_id: UserId,
        deck_id: Optional[FlashcardDeckId],
        session_type: SessionType,
        limit: int,
        device: str,
    ):
        return LearningSession(
            id=LearningSessionId.no_id(),
            user_id=user_id,
            deck_id=deck_id,
            status=SessionStatus.STARTED,
            progress=0,
            limit=limit,
            type=session_type,
            device=device,
            new_steps=[],
        )

    def is_finished(self) -> bool:
        return self.status == SessionStatus.FINISHED

    def check_if_finished(self):
        if self.progress >= self.limit:
            self.status = SessionStatus.FINISHED

    def add_flashcard(self, step_id: LearningSessionStepId, flashcard: IFlashcard):
        self.new_steps.append(
            LearningSessionStep(id=step_id, rating=None, flashcard_exercise=flashcard)
        )

    def add_unscramble_exercise(
        self, step_id: LearningSessionStepId, exercise: UnscrambleWordExercise
    ):
        self.new_steps.append(
            LearningSessionStep(id=step_id, rating=None, unscramble_word_exercise=exercise)
        )

    def add_word_match_exercise(self, step_id: LearningSessionStepId, exercise: WordMatchExercise):
        self.new_steps.append(
            LearningSessionStep(
                id=step_id, rating=None, flashcard_exercise=None, word_match_exercise=exercise
            )
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
        if self.status == SessionStatus.FINISHED:
            return False

        if self.progress >= self.limit:
            return False

        if len(self.new_steps) == 0:
            return True

        # pick last new step
        last_step = self.new_steps[-1]

        return last_step.rating is not None
