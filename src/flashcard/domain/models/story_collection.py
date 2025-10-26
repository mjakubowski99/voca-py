from typing import Generator, List

from src.flashcard.domain.models.flashcard import Flashcard
from src.flashcard.domain.models.story import Story
from src.flashcard.domain.models.story_flashcard import StoryFlashcard

from pydantic import BaseModel


class StoryCollection(BaseModel):
    stories: List[Story]
    pulled_flashcards: List[Flashcard] = []

    def get(self) -> List[Story]:
        return self.stories

    def unset(self, indexes: List[int]) -> None:
        for index in sorted(indexes, reverse=True):
            if 0 <= index < len(self.stories):
                self.stories.pop(index)

    def get_all_story_flashcards(self) -> Generator[StoryFlashcard, None, None]:
        for story in self.stories:
            for flashcard in story.get_story_flashcards():
                yield flashcard

    def get_all_flashcards_count(self) -> int:
        return len(list(self.get_all_story_flashcards()))

    def pull_stories_with_duplicates(
        self, stories_without_duplicates: List[StoryFlashcard]
    ) -> List[Flashcard]:
        stories_to_remove = []

        for index, story in enumerate(self.stories):
            new_story_flashcards = [
                sfc for sfc in stories_without_duplicates if index == sfc.get_index()
            ]

            if len(new_story_flashcards) != len(story.get_story_flashcards()):
                stories_to_remove.append(index)
                self.pulled_flashcards.extend([sfc.get_flashcard() for sfc in new_story_flashcards])
            else:
                story.set_story_flashcards(new_story_flashcards)

        self.unset(stories_to_remove)
        return self.pulled_flashcards

    def pull_stories_with_only_one_sentence(self) -> None:
        stories_to_remove = []

        for index, story in enumerate(self.stories):
            if len(story.get_story_flashcards()) == 1:
                stories_to_remove.append(index)
                self.pulled_flashcards.append(story.get_story_flashcards()[0].get_flashcard())

        self.unset(stories_to_remove)

    def get_pulled_flashcards(self) -> List[Flashcard]:
        return self.pulled_flashcards