from datetime import datetime, timezone
from typing import Any, List, Dict
from sqlalchemy.future import select
from sqlalchemy import insert, update
from src.study.domain.models.exercise.word_match_exercise import WordMatchExercise
from src.study.domain.models.exercise_entry.word_match_exercise_entry import WordMatchExerciseEntry
from src.shared.value_objects.user_id import UserId
from src.shared.value_objects.flashcard_id import FlashcardId
from src.study.domain.value_objects import ExerciseId
from src.study.domain.value_objects import ExerciseEntryId
from src.study.domain.enum import ExerciseStatus
from src.study.domain.models.answer.word_match_answer import WordMatchAnswer
from core.models import Exercises, ExerciseEntries
from core.db import get_session
from src.study.application.repository.contracts import IWordMatchExerciseRepository


class WordMatchExerciseRepository(IWordMatchExerciseRepository):
    async def find(self, exercise_id: ExerciseId) -> WordMatchExercise:
        session = get_session()
        q = (
            select(Exercises, ExerciseEntries)
            .join(ExerciseEntries, ExerciseEntries.exercise_id == Exercises.id)
            .where(Exercises.id == exercise_id.value)
        )
        result = await session.execute(q)
        rows = result.fetchall()
        if not rows:
            raise Exception(f"No Word Match Exercise found for entry ID: {exercise_id.value}")

        properties = self._parse_properties(rows[0][0])
        entries = [self._map_entry(properties, row[1]) for row in rows]
        return self._map_exercise(properties, rows[0][0], entries)

    async def create(self, exercise: WordMatchExercise) -> WordMatchExercise:
        session = get_session()

        properties = self._props_from_exercise(exercise)
        stmt = insert(Exercises).values(
            exercise_type=exercise.type.to_number(),
            user_id=exercise.user_id.value,
            status=exercise.status.value,
            properties=properties,
        )
        result = await session.execute(stmt)

        exercise_id = result.inserted_primary_key[0]
        await self._insert_entries(session, exercise_id, exercise.exercise_entries)
        await session.commit()
        exercise.id = ExerciseId(exercise_id)
        return exercise

    async def save(self, exercise: WordMatchExercise) -> None:
        session = get_session()

        stmt = (
            update(Exercises)
            .where(Exercises.id == exercise.id.value)
            .values(
                exercise_type=exercise.type.to_number(),
                user_id=exercise.user_id.value,
                status=exercise.status.value,
                properties=self._props_from_exercise(exercise),
            )
        )
        await session.execute(stmt)
        await self._save_entries(session, exercise.get_updated_entries())
        await session.commit()

    async def _insert_entries(
        self, session, exercise_id: int, entries: List[WordMatchExerciseEntry]
    ) -> None:
        bulk = []
        for entry in entries:
            bulk.append(
                dict(
                    exercise_id=exercise_id,
                    correct_answer=entry.correct_answer.to_string(),
                    score=0.0,
                    answers_count=0,
                    last_answer=None,
                    last_answer_correct=None,
                    order=entry.order,
                )
            )
        if bulk:
            await session.execute(insert(ExerciseEntries), bulk)

    async def _save_entries(self, session, entries: List[WordMatchExerciseEntry]) -> None:
        for entry in entries:
            stmt = (
                update(ExerciseEntries)
                .where(ExerciseEntries.id == entry.id.value)
                .values(
                    correct_answer=entry.correct_answer.to_string(),
                    score=entry.score,
                    answers_count=entry.answers_count,
                    last_answer=entry.last_user_answer.to_string()
                    if entry.last_user_answer
                    else None,
                    last_answer_correct=entry.last_answer_correct,
                    order=entry.order,
                )
            )
            await session.execute(stmt)

    def _props_from_exercise(self, exercise: WordMatchExercise) -> Dict[str, Any]:
        return {
            "story_id": exercise.story_id.value if exercise.story_id else None,
            "sentences": [
                {
                    "flashcard_id": entry.flashcard_id.value,
                    "order": entry.order,
                    "sentence": entry.sentence,
                    "word": entry.word,
                    "translation": entry.word_translation,
                }
                for entry in exercise.exercise_entries
            ],
            "answer_options": exercise.options,
        }

    def _parse_properties(self, exercises_row) -> Dict[str, Any]:
        return exercises_row.properties

    def _map_entry(self, properties: Dict[str, Any], entry_row) -> WordMatchExerciseEntry:
        order = entry_row.order
        sentences = properties.get("sentences", [])
        word = sentences[order]["word"] if order < len(sentences) else ""
        translation = sentences[order]["translation"] if order < len(sentences) else ""
        sentence = sentences[order]["sentence"] if order < len(sentences) else ""

        entry_id = ExerciseEntryId(entry_row.id)
        return WordMatchExerciseEntry(
            word=word,
            word_translation=translation,
            sentence=sentence,
            id=entry_id,
            flashcard_id=FlashcardId(value=sentences[order]["flashcard_id"]),
            exercise_id=ExerciseId(value=entry_row.exercise_id),
            correct_answer=WordMatchAnswer(answer_entry_id=entry_id, word=entry_row.correct_answer),
            last_user_answer=WordMatchAnswer(answer_entry_id=entry_id, word=entry_row.last_answer)
            if entry_row.last_answer
            else None,
            last_answer_correct=entry_row.last_answer_correct,
            order=order,
            score=entry_row.score,
            answers_count=entry_row.answers_count,
        )

    def _map_exercise(
        self, properties: Dict[str, Any], exercises_row, entries: List[WordMatchExerciseEntry]
    ) -> WordMatchExercise:
        # story_id may be None
        sid_val = properties.get("story_id")
        story_id = None
        if sid_val is not None:
            from src.shared.value_objects.story_id import StoryId

            story_id = StoryId(sid_val)
        return WordMatchExercise(
            story_id=story_id,
            exercise_id=ExerciseId(value=exercises_row.id),
            user_id=UserId(value=exercises_row.user_id),
            status=ExerciseStatus(value=exercises_row.status),
            exercise_entries=entries,
            options=properties.get("answer_options", []),
        )
