import random
from typing import List
from pydantic import BaseModel
from src.shared.enum import LanguageLevel
from src.shared.value_objects.language import Language

class InvalidPromptException(Exception):
    pass

class FlashcardPrompt(BaseModel):
    category: str
    language_level: LanguageLevel
    word_lang: Language
    translation_lang: Language
    words_count: int = 10
    initial_letters_to_avoid: List[str] = []

    prompt: str = '''
        You are an AI algorithm generating vocabulary for language learning.
        Based on the topic provided by the user, create a story consisting of ${{words_count}} sentences in ${{translation_lang_name}}.
        Divide the story into parts that must have 3-4 sentences each — each part is a separate mini-story,
        which within these sentences must form a coherent, logical whole (i.e., a short event with beginning, middle, and end).
        For each sentence, generate its translation into ${{word_lang_name}}.
        Then extract words for flashcards from the generated sentences. Selected words must:
        – appear in the sentence in their basic (uninflected) form,
        – directly relate to the topic,
        – not repeat in other stories.
        Example story: conversation with a cashier
            - Emma walked into the store and picked up a bottle of water.
            - She went to the counter where the cashier was waiting.
            - The cashier said, "That will be two dollars, please."
        Save the result in simple JSON code format:
        [{
        "word": "word_in_${{word_lang_code}}",
        "trans": "translation_in_${{translation_lang_code}}",
        "sentence": "sentence_in_${{word_lang_name}}",
        "sentence_trans": "sentence_in_${{translation_lang_name}}",
        "emoji": "😀",
        "story_id": 1
        },...]
        Field descriptions:
         - word: word in ${{word_lang_name}}
         - trans: its translation to ${{translation_lang_name}}
         - sentence: sentence in ${{word_lang_name}} containing the word
         - sentence_trans: sentence translation to ${{translation_lang_name}}
         - story_id: story number from which it originates (story_id).
        Generate a JSON format response containing ${{words_count}} records.
        Also consider the language level specification. Selected level: ${{level}}
        ${{letters_condition}}
        Apply:
            - creativity in creating examples
            - random generation seed: ${{seed}}
        User prompt: ${{category}}.
        Error condition: If for any reason you cannot generate records for the given situation, instead of records respond in format 
        {"error":"prompt"}
        Your response should contain only and exclusively data in JSON format and nothing else.
    '''

    def __init__(self, **data):
        super().__init__(**data)
        self.validate_languages()
        self.build_prompt()

    def validate_languages(self):
        # Replace this list with actual supported languages
        supported_languages = ["English", "Spanish", "French", "German"]
        if self.word_lang.get_value() not in supported_languages:
            raise InvalidPromptException(f"Unsupported word language: {self.word_lang.get_value()}")
        if self.translation_lang.get_value() not in supported_languages:
            raise InvalidPromptException(f"Unsupported translation language: {self.translation_lang.get_value()}")

    def build_prompt(self):
        self.set_random_seed()
        self.set_category()
        self.set_language_level()
        self.set_words_count()
        self.set_languages()
        self.set_initial_letters_to_avoid()
        self.remove_white_characters()

    def set_random_seed(self):
        self.prompt = self.prompt.replace("${{seed}}", str(random.randint(0, 1000)))

    def set_category(self):
        if "${{category}}" not in self.prompt:
            raise InvalidPromptException("Invalid prompt exception")
        self.prompt = self.prompt.replace("${{category}}", self.category)

    def set_language_level(self):
        if "${{level}}" not in self.prompt:
            raise InvalidPromptException("Invalid prompt exception. Language level not defined")
        self.prompt = self.prompt.replace("${{level}}", str(self.language_level))

    def set_words_count(self):
        if "${{words_count}}" not in self.prompt:
            raise InvalidPromptException("Invalid prompt exception")
        self.prompt = self.prompt.replace("${{words_count}}", str(self.words_count))

    def set_languages(self):
        replacements = {
            "${{word_lang_name}}": self.word_lang.get_value(),
            "${{translation_lang_name}}": self.translation_lang.get_value(),
            "${{word_lang_code}}": self.word_lang.get_value(),
            "${{translation_lang_code}}": self.translation_lang.get_value(),
        }
        for placeholder, value in replacements.items():
            if placeholder not in self.prompt:
                raise InvalidPromptException(f"Invalid prompt exception. Missing placeholder: {placeholder}")
            self.prompt = self.prompt.replace(placeholder, value)

    def set_initial_letters_to_avoid(self):
        if "${{letters_condition}}" not in self.prompt:
            raise InvalidPromptException("Invalid prompt exception")
        if not self.initial_letters_to_avoid:
            self.prompt = self.prompt.replace("${{letters_condition}}", "")
        else:
            condition = "Avoid words starting with letters: " + ",".join(self.initial_letters_to_avoid)
            self.prompt = self.prompt.replace("${{letters_condition}}", condition)

    def remove_white_characters(self):
        self.prompt = self.prompt.replace("\n", "").replace("\r", "")

    def get_prompt(self) -> str:
        return self.prompt

    def get_word_lang(self) -> Language:
        return self.word_lang

    def get_translation_lang(self) -> Language:
        return self.translation_lang
