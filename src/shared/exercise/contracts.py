from abc import ABC, abstractmethod
from src.shared.value_objects.exercise_entry_id import ExerciseEntryId
from typing import List
from src.shared.enum import ExerciseType
from src.shared.value_objects.user_id import UserId
from src.shared.flashcard.contracts import ISessionFlashcardSummaries
from src.shared.value_objects.exercise_id import ExerciseId
from src.shared.models import Emoji
from typing import Optional


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
        pass


class IUnscrambleWordExerciseRead(ABC):
    @abstractmethod
    def get_id(self) -> ExerciseId:
        pass

    @abstractmethod
    def get_scrambled_word(self) -> str:
        pass

    @abstractmethod
    def get_front_word(self) -> str:
        pass

    @abstractmethod
    def get_context_sentence(self) -> str:
        pass

    @abstractmethod
    def get_context_sentence_translation(self) -> Optional[str]:
        pass

    @abstractmethod
    def get_emoji(self) -> Optional[Emoji]:
        pass

    @abstractmethod
    def get_keyboard(self) -> List[str]:
        pass

    @abstractmethod
    def get_exercise_entry_id(self) -> int:
        pass


class IWordMatchExerciseReadEntry(ABC):
    @abstractmethod
    def get_exercise_entry_id(self) -> ExerciseEntryId:
        pass

    @abstractmethod
    def is_answered(self) -> bool:
        pass

    @abstractmethod
    def get_word(self) -> str:
        pass

    @abstractmethod
    def get_word_translation(self) -> str:
        pass

    @abstractmethod
    def get_sentence(self) -> str:
        pass

    @abstractmethod
    def get_sentence_part_before_word(self) -> str:
        pass

    @abstractmethod
    def get_sentence_part_after_word(self) -> str:
        pass


class IWordMatchExerciseRead(ABC):
    @abstractmethod
    def get_exercise_id(self) -> ExerciseId:
        pass

    @abstractmethod
    def is_story(self) -> bool:
        pass

    @abstractmethod
    def get_entries(self) -> List[IWordMatchExerciseReadEntry]:
        pass

    @abstractmethod
    def get_answer_options(self) -> List[str]:
        pass


class IExerciseReadFacade(ABC):
    @abstractmethod
    def get_exercise_score_sum(self, exercise_entry_ids: List[ExerciseEntryId]) -> float:
        pass

    @abstractmethod
    def get_unscramble_word_exercise(self, id: ExerciseEntryId) -> IUnscrambleWordExerciseRead:
        pass

    @abstractmethod
    def get_word_match_exercise(self, id: ExerciseEntryId) -> IWordMatchExerciseRead:
        pass


class IExerciseSummary(ABC):
    @abstractmethod
    def get_id(self) -> ExerciseId:
        pass

    @abstractmethod
    def is_finished(self) -> bool:
        pass

    @abstractmethod
    def get_exercise_type(self) -> ExerciseType:
        pass


class IExerciseScore(ABC):
    @abstractmethod
    def get_exercise_entry_id(self) -> ExerciseEntryId:
        pass

    @abstractmethod
    def get_score(self) -> float:
        pass
