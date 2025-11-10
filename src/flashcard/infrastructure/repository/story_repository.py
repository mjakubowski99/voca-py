from datetime import datetime, timezone
from sqlalchemy import select, func, insert, delete
from sqlalchemy.ext.asyncio import AsyncSession
from src.flashcard.application.repository.contracts import IStoryRepository
from src.flashcard.domain.models.story import Story, StoryFlashcard
from src.flashcard.domain.models.story_collection import StoryCollection
from src.flashcard.domain.value_objects import FlashcardId
from src.shared.value_objects.story_id import StoryId
from src.flashcard.infrastructure.repository.flashcard_repository import FlashcardRepository
from core.models import StoryFlashcards, Stories
from src.shared.value_objects.user_id import UserId


class StoryRepository(IStoryRepository):
    def __init__(self, flashcard_repo: FlashcardRepository, session: AsyncSession):
        self.flashcard_repo = flashcard_repo
        self.session = session

    async def find_random_story_id_by_flashcard_id(
        self, flashcard_id: FlashcardId
    ) -> StoryId | None:
        """
        Returns a random story_id that contains the given flashcard.
        """
        query = (
            select(StoryFlashcards.story_id)
            .where(StoryFlashcards.flashcard_id == flashcard_id.value)
            .order_by(func.random())
            .limit(1)
        )
        result = await self.session.execute(query)
        row = result.scalar_one_or_none()
        return StoryId(row) if row else None

    async def find(self, story_id: StoryId, user_id: UserId) -> Story | None:
        """
        Returns a Story with its flashcards mapped for the given user.
        """
        query = select(
            StoryFlashcards.flashcard_id,
            StoryFlashcards.story_id,
            StoryFlashcards.sentence_override,
        ).where(StoryFlashcards.story_id == story_id.value)

        result = await self.session.execute(query)
        rows = result.all()
        if not rows:
            return None

        flashcard_ids = [row.flashcard_id for row in rows]
        flashcards = await self.mapper.find_many_for_user(flashcard_ids, user_id)

        story_flashcards = []
        for row in rows:
            flashcard = next((f for f in flashcards if f.id.value == row.flashcard_id), None)
            story_flashcards.append(
                StoryFlashcard(
                    story_id=StoryId(row.story_id),
                    story_row_id=row.story_id,
                    sentence_override=row.sentence_override,
                    flashcard=flashcard,
                )
            )

        return Story(story_id, story_flashcards)

    async def save_many(self, stories: StoryCollection) -> None:
        """
        Inserts multiple stories and their story_flashcards.
        """
        now = datetime.now(timezone.utc).replace(tzinfo=None)

        # Insert stories
        insert_data = [{"created_at": now, "updated_at": now} for _ in stories.get()]
        stmt = insert(Stories).returning(Stories.id)
        result = await self.session.execute(stmt, insert_data)
        story_ids = [StoryId(row.id) for row in result.fetchall()]

        # Assign story_ids to story flashcards
        for story, story_id in zip(stories.get(), story_ids):
            for sf in story.flashcards:
                sf.story_id = story_id

        # Use mapper to prepare story flashcards
        stories = await self.flashcard_repo.create_many_from_story_flashcards(stories)

        # Insert story_flashcards
        flashcard_insert_data = [
            {
                "story_id": sf.story_id.value,
                "flashcard_id": sf.flashcard.id.value,
                "sentence_override": sf.sentence_override,
                "created_at": now,
                "updated_at": now,
            }
            for sf in stories.get_all_story_flashcards()
        ]
        await self.session.execute(insert(StoryFlashcards), flashcard_insert_data)
        await self.session.commit()

    async def bulk_delete(self, story_ids: list[StoryId]) -> None:
        """
        Deletes multiple stories by their IDs.
        """
        stmt = delete(Stories).where(Stories.id.in_([s.value for s in story_ids]))
        await self.session.execute(stmt)
        await self.session.commit()
