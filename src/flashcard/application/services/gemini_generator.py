import json
import logging
import re
from typing import Dict, List
from google.genai import Client

from src.flashcard.application.services.iflashcard_generator import IFlashcardGenerator
from src.flashcard.domain.models.deck import Deck
from src.flashcard.domain.models.owner import Owner
from src.shared.models import Emoji
from src.flashcard.domain.models.flashcard_prompt import FlashcardPrompt
from src.flashcard.domain.models.flashcard import Flashcard
from src.flashcard.domain.models.story import Story
from src.flashcard.domain.models.story_collection import StoryCollection
from src.flashcard.domain.models.story_flashcard import StoryFlashcard
from src.flashcard.domain.value_objects import FlashcardId
from src.shared.value_objects.story_id import StoryId

from config import settings


class AiResponseFailedException(Exception):
    pass


class AiResponseProcessingFailException(Exception):
    pass


class GeminiGenerator(IFlashcardGenerator):
    async def generate(self, owner: Owner, deck: Deck, prompt: FlashcardPrompt) -> StoryCollection:
        async with Client(api_key=settings.gemini_api_key).aio as client:
            try:
                response = await client.models.generate_content(
                    model="gemini-2.5-flash", contents=prompt.prompt
                )
            except Exception as e:
                logging.error("Gemini API request failed", exc_info=e)
                raise AiResponseFailedException(f"Gemini API request failed: {e}")

            if not hasattr(response, "text") or not response.text.strip():
                logging.error("Gemini API returned empty or invalid response")
                raise AiResponseFailedException("Gemini API returned empty or invalid response")

            text = response.text

        stories: Dict[int, List[StoryFlashcard]] = {}

        for row in self.parse_chat_response(text):
            story_index = row.get("story_id", 0)
            if story_index not in stories:
                stories[story_index] = []

            stories[story_index].append(
                StoryFlashcard(
                    story_id=StoryId.no_id(),
                    story_index=story_index,
                    sentence_override=None,
                    flashcard=Flashcard(
                        id=FlashcardId.no_id(),
                        front_word=str(row.get("word", "")),
                        front_lang=prompt.word_lang,
                        back_word=str(row.get("trans", "")),
                        back_lang=prompt.translation_lang,
                        front_context=str(row.get("sentence", "")),
                        back_context=str(row.get("sentence_trans", "")),
                        owner=owner,
                        deck=deck,
                        level=deck.default_language_level,
                        emoji=Emoji(emoji=row["emoji"]) if "emoji" in row else None,
                    ),
                )
            )

        result_stories = [
            Story(id=StoryId.no_id(), flashcards=flashcards) for flashcards in stories.values()
        ]

        return StoryCollection(stories=result_stories)

    @staticmethod
    def parse_chat_response(text: str) -> List[Dict]:
        match = re.search(r"```json(.*?)```", text, re.S)
        json_text = match.group(1).strip() if match else text.strip()

        try:
            rows = json.loads(json_text)
            if not isinstance(rows, list):
                logging.error("Gemini returned JSON, but not a list")
                raise AiResponseProcessingFailException()
            return rows
        except json.JSONDecodeError as e:
            logging.error("Failed to parse JSON from Gemini response", exc_info=e)
            raise AiResponseProcessingFailException()
