from abc import ABC, abstractmethod
from src.shared.value_objects.exercise_entry_id import ExerciseEntryId
from typing import List
from src.shared.enum import ExerciseType
from src.shared.value_objects.user_id import UserId
from src.shared.flashcard.contracts import ISessionFlashcardSummaries


class IFlashcardExercise(ABC):
    @abstractmethod
    def get_flashcard_id() -> int:
        pass

    @abstractmethod
    def get_exercise_entry_id() -> ExerciseEntryId:
        pass


class IFlashcardExerciseFacade(ABC):
    @abstractmethod
    async def build_exercise(
        self,
        summaries: ISessionFlashcardSummaries,
        user_id: UserId,
        exercise_type: ExerciseType,
    ) -> List[IFlashcardExercise]:
        """
        Build a list of flashcard exercises for the given session summaries, user, and exercise type.
        """
        pass
