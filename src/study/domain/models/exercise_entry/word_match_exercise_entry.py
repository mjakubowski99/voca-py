from __future__ import annotations

# --- Domain imports ---
from src.study.domain.models.exercise_entry.exercise_entry import ExerciseEntry


class WordMatchExerciseEntry(ExerciseEntry):
    """Specialized ExerciseEntry for word-matching exercises."""

    word: str
    word_translation: str
    sentence: str

    def get_word(self) -> str:
        return self.word

    def get_word_translation(self) -> str:
        return self.word_translation

    def get_sentence(self) -> str:
        return self.sentence
