from typing import Optional
from src.shared.value_objects.exercise_entry_id import ExerciseEntryId
from shared.enum import ExerciseType
from flashcard.domain.value_objects import FlashcardId


class NextSessionFlashcard:
    def __init__(self, flashcard_id: FlashcardId):
        self._id: FlashcardId = flashcard_id
        self._exercise_entry_id: Optional[ExerciseEntryId] = None
        self._type: Optional[ExerciseType] = None

    # Getters
    def get_flashcard_id(self) -> FlashcardId:
        return self._id

    def get_exercise_type(self) -> Optional[ExerciseType]:
        return self._type

    def get_exercise_entry_id(self) -> Optional[ExerciseEntryId]:
        return self._exercise_entry_id

    def has_exercise(self) -> bool:
        return self._exercise_entry_id is not None

    # Setter
    def set_exercise(self, entry_id: ExerciseEntryId, exercise_type: ExerciseType) -> None:
        self._exercise_entry_id = entry_id
        self._type = exercise_type
