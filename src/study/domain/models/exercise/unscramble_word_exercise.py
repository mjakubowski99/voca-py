# optimize imports
from __future__ import annotations
import random
from typing import List, Optional
from pydantic import model_validator

from src.shared.value_objects.flashcard_id import FlashcardId
from src.shared.value_objects.user_id import UserId
from src.shared.models import Emoji
from src.study.domain.enum import ExerciseStatus, ExerciseType
from src.study.domain.value_objects import ExerciseId, ExerciseEntryId
from src.study.domain.models.exercise.exercise import Exercise
from src.study.domain.models.exercise_entry.exercise_entry import ExerciseEntry
from src.study.domain.models.answer.unscramble_word_answer import UnscrambleWordAnswer


class UnscrambleWordExercise(Exercise):
    word: str
    flashcard_id: FlashcardId
    context_sentence: str
    word_translation: str
    context_sentence_translation: Optional[str] = None
    emoji: Optional[Emoji] = None
    scrambled_word: str

    @model_validator(mode="before")
    @classmethod
    def create_exercise_entry(cls, data: dict) -> dict:
        """Create the exercise entry before model initialization."""
        if isinstance(data, dict) and "answer_entry_id" in data:
            # Extract values needed for entry creation
            answer_entry_id = data.get("answer_entry_id")
            exercise_id = data.get("id")
            word_translation = data.get("word_translation")
            last_answer = data.get("last_answer")
            last_answer_correct = data.get("last_answer_correct")
            score = data.get("score", 0.0)
            answers_count = data.get("answers_count", 0)
            flashcard_id = data.get("flashcard_id")

            # Create the exercise entry
            entry = ExerciseEntry(
                id=answer_entry_id,
                exercise_id=exercise_id,
                flashcard_id=flashcard_id,
                correct_answer=UnscrambleWordAnswer(
                    answer_entry_id=answer_entry_id, unscrambled_word=word_translation
                ),
                last_user_answer=last_answer,
                last_answer_correct=last_answer_correct,
                order=0,
                score=score,
                answers_count=answers_count,
            )

            # Update data dict with the entry and type
            data["exercise_entries"] = [entry]
            data["type"] = ExerciseType.UNSCRAMBLE_WORDS

            # Remove temporary fields that aren't part of the model
            data.pop("answer_entry_id", None)
            data.pop("last_answer", None)
            data.pop("last_answer_correct", None)
            data.pop("score", None)
            data.pop("answers_count", None)

        return data

    @staticmethod
    def scramble(word: str) -> str:
        """Shuffle the characters of the given word."""
        chars = list(word)
        random.shuffle(chars)
        scrambled = "".join(chars)
        return scrambled

    @classmethod
    def new_exercise(
        cls,
        user_id: UserId,
        flashcard_id: FlashcardId,
        word: str,
        context_sentence: str,
        word_translation: str,
        context_sentence_translation: Optional[str],
        emoji: Optional[Emoji],
    ) -> "UnscrambleWordExercise":
        """Factory method for creating a new unscramble exercise."""
        scrambled_word = cls.scramble(word_translation)
        if scrambled_word == word:
            scrambled_word = cls.scramble(word_translation)

        return cls(
            id=ExerciseId.no_id(),
            user_id=user_id,
            flashcard_id=flashcard_id,
            status=ExerciseStatus.NEW,
            answer_entry_id=ExerciseEntryId.no_id(),
            word=word,
            context_sentence=context_sentence,
            word_translation=word_translation,
            context_sentence_translation=context_sentence_translation,
            emoji=emoji,
            scrambled_word=scrambled_word,
        )

    def get_word(self) -> str:
        return self.word

    def get_word_translation(self) -> str:
        return self.word_translation

    def get_context_sentence(self) -> str:
        return self.context_sentence

    def get_context_sentence_translation(self) -> Optional[str]:
        return self.context_sentence_translation

    def get_emoji(self) -> Optional[Emoji]:
        return self.emoji

    def get_scrambled_word(self) -> str:
        return self.scrambled_word

    def get_keyboard(self) -> List[str]:
        keyboard = list(self.word_translation)
        random.shuffle(keyboard)
        return keyboard

    def get_indexed_keyboard(self) -> List[dict]:
        return [{"c": c, "i": i} for i, c in enumerate(list(self.word_translation))]
