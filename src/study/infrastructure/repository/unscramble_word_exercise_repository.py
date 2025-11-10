from sqlalchemy import select, insert, update
from sqlalchemy.exc import NoResultFound
from core.models import Exercises, ExerciseEntries, UnscrambleWordExercises

from src.shared.value_objects.flashcard_id import FlashcardId
from src.study.application.repository.contracts import (
    IUnscrambleWordExerciseRepository,
)
from src.study.domain.models.exercise.unscramble_word_exercise import UnscrambleWordExercise
from src.study.domain.models.answer.unscramble_word_answer import UnscrambleWordAnswer
from src.study.domain.enum import ExerciseStatus
from src.shared.models import Emoji
from src.study.domain.value_objects import ExerciseId
from src.study.domain.value_objects import ExerciseEntryId
from src.shared.value_objects.user_id import UserId
from sqlalchemy.ext.asyncio import AsyncSession


class UnscrambleWordExerciseRepository(IUnscrambleWordExerciseRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def find(self, exercise_id: ExerciseId) -> UnscrambleWordExercise:
        query = (
            select(
                Exercises.id,
                Exercises.user_id,
                Exercises.status,
                Exercises.exercise_type,
                Exercises.properties,
                UnscrambleWordExercises.word,
                UnscrambleWordExercises.scrambled_word,
                UnscrambleWordExercises.context_sentence,
                UnscrambleWordExercises.word_translation,
                UnscrambleWordExercises.context_sentence_translation,
                UnscrambleWordExercises.emoji,
                ExerciseEntries.id.label("exercise_entry_id"),
                ExerciseEntries.last_answer,
                ExerciseEntries.last_answer_correct,
                ExerciseEntries.score,
                ExerciseEntries.answers_count,
            )
            .join(UnscrambleWordExercises, Exercises.id == UnscrambleWordExercises.exercise_id)
            .join(ExerciseEntries, ExerciseEntries.exercise_id == Exercises.id)
            .where(Exercises.id == exercise_id.value)
        )

        result = await self.session.execute(query)
        row = result.first()

        if not row:
            raise NoResultFound(f"UnscrambleWordExercise with id {exercise_id.value} not found")

        return self._map_to_domain(row)

    async def find_by_entry_id(self, entry_id: ExerciseEntryId) -> UnscrambleWordExercise:
        query = (
            select(
                Exercises.id,
                Exercises.user_id,
                Exercises.status,
                Exercises.exercise_type,
                Exercises.properties,
                UnscrambleWordExercises.word,
                UnscrambleWordExercises.scrambled_word,
                UnscrambleWordExercises.context_sentence,
                UnscrambleWordExercises.word_translation,
                UnscrambleWordExercises.context_sentence_translation,
                UnscrambleWordExercises.emoji,
                ExerciseEntries.id.label("exercise_entry_id"),
                ExerciseEntries.last_answer,
                ExerciseEntries.last_answer_correct,
                ExerciseEntries.score,
                ExerciseEntries.answers_count,
            )
            .join(UnscrambleWordExercises, Exercises.id == UnscrambleWordExercises.exercise_id)
            .join(ExerciseEntries, ExerciseEntries.exercise_id == Exercises.id)
            .where(ExerciseEntries.id == entry_id.value)
        )

        result = await self.session.execute(query)
        row = result.first()

        if not row:
            raise NoResultFound(f"UnscrambleWordExercise with entry id {entry_id.value} not found")

        return self._map_to_domain(row)

    async def create(self, exercise: UnscrambleWordExercise) -> UnscrambleWordExercise:
        if not exercise.get_id().is_empty():
            raise ValueError("Cannot create exercise with already existing ID")

        insert_stmt = (
            insert(Exercises)
            .values(
                exercise_type=exercise.get_exercise_type().to_number(),
                user_id=exercise.get_user_id().value,
                status=exercise.get_status().value,
                properties={"flashcard_id": exercise.exercise_entries[0].flashcard_id.get_value()},
            )
            .returning(Exercises.id)
        )

        result = await self.session.execute(insert_stmt)
        new_id = result.scalar_one()

        await self.session.execute(
            insert(UnscrambleWordExercises).values(
                exercise_id=new_id,
                word=exercise.get_word(),
                context_sentence=exercise.get_context_sentence(),
                word_translation=exercise.get_word_translation(),
                context_sentence_translation=exercise.get_context_sentence_translation(),
                scrambled_word=exercise.get_scrambled_word(),
                emoji=exercise.get_emoji().to_unicode() if exercise.get_emoji() else None,
            )
        )
        exercise.id = ExerciseId(value=new_id)

        entry = exercise.get_exercise_entries()[0]
        result = await self.session.execute(
            insert(ExerciseEntries)
            .values(
                exercise_id=new_id,
                last_answer=entry.get_last_user_answer().to_string()
                if entry.get_last_user_answer()
                else None,
                last_answer_correct=entry.is_last_answer_correct(),
                score=entry.get_score(),
                answers_count=entry.get_answers_count(),
                correct_answer=entry.get_correct_answer().to_string(),
            )
            .returning(ExerciseEntries.id)
        )
        entry_id = result.scalar_one()
        exercise.exercise_entries[0].id = ExerciseEntryId(value=entry_id)

        await self.session.commit()

        return exercise

    async def save(self, exercise: UnscrambleWordExercise) -> None:
        await self.session.execute(
            update(Exercises)
            .where(Exercises.id == exercise.get_id().value)
            .values(
                exercise_type=exercise.get_exercise_type().to_number(),
                status=exercise.get_status().value,
            )
        )

        for entry in exercise.get_updated_entries():
            await self.session.execute(
                update(ExerciseEntries)
                .where(ExerciseEntries.id == entry.get_id().value)
                .values(
                    last_answer=entry.get_last_user_answer().to_string()
                    if entry.get_last_user_answer()
                    else None,
                    last_answer_correct=entry.is_last_answer_correct(),
                    score=entry.get_score(),
                    answers_count=entry.get_answers_count(),
                )
            )

        await self.session.commit()

    def _map_to_domain(self, row) -> UnscrambleWordExercise:
        entry_id = ExerciseEntryId(row.exercise_entry_id)

        return UnscrambleWordExercise(
            id=ExerciseId(value=row.id),
            user_id=UserId(value=row.user_id),
            flashcard_id=FlashcardId(value=row.properties["flashcard_id"]),
            status=ExerciseStatus(value=row.status),
            answer_entry_id=entry_id,
            word=row.word,
            context_sentence=row.context_sentence,
            word_translation=row.word_translation,
            context_sentence_translation=row.context_sentence_translation,
            emoji=Emoji.from_unicode(row.emoji) if row.emoji else None,
            scrambled_word=row.scrambled_word,
            last_answer=UnscrambleWordAnswer(
                answer_entry_id=entry_id, unscrambled_word=row.last_answer
            )
            if row.last_answer
            else None,
            last_answer_correct=row.last_answer_correct,
            score=float(row.score),
            answers_count=row.answers_count,
        )
