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

    def get_sentence_part_before_word(self) -> str:
        if self.word not in self.sentence:
            return self.sentence
        return self.sentence.split(self.word, 1)[0]

    def get_sentence_part_after_word(self) -> str:
        if self.word not in self.sentence:
            return ""
        return self.sentence.split(self.word, 1)[1]

    def is_answered(self) -> bool:
        return self.last_answer_correct if self.last_answer_correct is not None else False
