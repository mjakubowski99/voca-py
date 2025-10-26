from pydantic import BaseModel
import json


class Emoji(BaseModel):
    emoji: str

    @classmethod
    def from_unicode(cls, emoji_unicode: str) -> "Emoji":
        try:
            decoded = json.loads(emoji_unicode)
        except json.JSONDecodeError:
            decoded = ""
        return cls(emoji=decoded)

    def to_unicode(self) -> str:
        return json.dumps(self.emoji)

    def __str__(self) -> str:
        return self.emoji

    def json_serialize(self) -> str:
        return self.emoji
