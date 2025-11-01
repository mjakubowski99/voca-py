from typing import Optional, List
import random

from src.shared.flashcard.contracts import ISessionFlashcardSummaries, IAnswerOption
from src.shared.value_objects import StoryId
from src.flashcard.domain.models.session_flashcard_summary import SessionFlashcardSummary
from src.flashcard.domain.models.flashcard import Flashcard
from src.flashcard.domain.models.story import Story
from src.flashcard.domain.models.answer_option import AnswerOption


class SessionFlashcardSummaries(ISessionFlashcardSummaries):
    def __init__(
        self,
        story_id: Optional[StoryId],
        summaries: List[SessionFlashcardSummary],
        options: Optional[List[IAnswerOption]] = None,
    ):
        self._story_id = story_id
        self._summaries = summaries
        self._options = options or []

    @staticmethod
    def from_story(
        story: Story, base_story_flashcard: Flashcard, options: Optional[List[Flashcard]] = None
    ) -> "SessionFlashcardSummaries":
        options = options or []

        answer_options = [sf.get_flashcard().get_back_word() for sf in story.get_story_flashcards()]
        answer_options += [o.get_back_word() for o in options]
        answer_options.append(base_story_flashcard.get_back_word())
        # remove duplicates while preserving order
        answer_options = list(dict.fromkeys(answer_options))

        answer_options_objs = [AnswerOption(word) for word in answer_options]
        random.shuffle(answer_options_objs)

        summaries = []
        for i, story_flashcard in enumerate(story.get_story_flashcards()):
            summaries.append(
                SessionFlashcardSummary(
                    order=i,
                    flashcard=story_flashcard.get_flashcard(),
                    is_additional=False,
                    is_story_part=True,
                    story_sentence=story_flashcard.get_sentence_override(),
                )
            )

        return SessionFlashcardSummaries(story.get_id(), summaries, answer_options_objs)

    @staticmethod
    def from_flashcards(
        flashcards: List[Flashcard],
        base_flashcard: Flashcard,
        options: Optional[List[Flashcard]] = None,
    ) -> "SessionFlashcardSummaries":
        options = options or []

        answer_options = [o.get_back_word() for o in options]
        answer_options += [f.get_back_word() for f in flashcards]
        answer_options.append(base_flashcard.get_back_word())
        answer_options = list(dict.fromkeys(answer_options))

        answer_options_objs = [AnswerOption(word) for word in answer_options]
        random.shuffle(answer_options_objs)

        summaries = [
            SessionFlashcardSummary(
                order=i,
                flashcard=f,
                is_additional=False,
                is_story_part=False,
                story_sentence=None,
            )
            for i, f in enumerate(flashcards)
        ]

        return SessionFlashcardSummaries(None, summaries, answer_options_objs)

    def has_story(self) -> bool:
        return self._story_id is not None

    def get_story_id(self) -> Optional[StoryId]:
        return self._story_id

    def get_summaries(self) -> List[SessionFlashcardSummary]:
        return self._summaries

    def get_answer_options(self) -> List[IAnswerOption]:
        return self._options
