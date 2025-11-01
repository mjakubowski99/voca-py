from abc import ABC, abstractmethod
from src.shared.value_objects.exercise_entry_id import ExerciseEntryId


class IFlashcardExercise(ABC):
    @abstractmethod
    def get_flashcard_id() -> int:
        pass

    @abstractmethod
    def get_exercise_entry_id() -> ExerciseEntryId:
        pass
