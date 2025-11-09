from __future__ import annotations
from abc import ABC, abstractmethod

from src.flashcard.domain.value_objects import FlashcardId, SessionId
from src.shared.value_objects.user_id import UserId
from src.study.domain.enum import Rating
from src.study.domain.models.exercise.unscramble_word_exercise import UnscrambleWordExercise
from src.study.domain.models.exercise.word_match_exercise import WordMatchExercise
from src.study.domain.models.learning_session import LearningSession
from src.study.domain.value_objects import ExerciseId, LearningSessionId, LearningSessionStepId
from src.study.domain.value_objects import ExerciseEntryId


class IUnscrambleWordExerciseRepository(ABC):
    @abstractmethod
    async def find(self, exercise_id: ExerciseId) -> UnscrambleWordExercise:
        pass

    @abstractmethod
    async def find_by_entry_id(self, entry_id: ExerciseEntryId) -> UnscrambleWordExercise:
        pass

    @abstractmethod
    async def create(self, exercise: UnscrambleWordExercise) -> ExerciseId:
        pass

    @abstractmethod
    async def save(self, exercise: UnscrambleWordExercise) -> None:
        pass


class IWordMatchExerciseRepository(ABC):
    @abstractmethod
    def find(self, exercise_id: ExerciseId) -> WordMatchExercise:
        pass

    @abstractmethod
    def create(self, exercise: WordMatchExercise) -> ExerciseId:
        pass

    @abstractmethod
    def save(self, exercise: WordMatchExercise) -> None:
        pass


class ISessionRepository(ABC):
    @abstractmethod
    async def find(self, session_id: LearningSessionId) -> LearningSession:
        pass

    @abstractmethod
    async def create(self, session: LearningSession) -> LearningSession:
        pass

    @abstractmethod
    async def save_steps(self, session: LearningSession) -> LearningSession:
        pass

    @abstractmethod
    async def mark_all_user_sessions_finished(self, user_id: UserId) -> None:
        pass

    @abstractmethod
    async def update_flashcard_rating(
        self, step_id: LearningSessionStepId, rating: Rating
    ) -> FlashcardId:
        pass
