from pydantic import BaseModel


class Emoji(BaseModel):
    emoji: str

    @classmethod
    def from_unicode(cls, emoji_unicode: str) -> "Emoji":
        """
        Construct from a raw Unicode emoji string.
        Example: Emoji.from_unicode("🐍")
        """
        if not emoji_unicode:
            return cls(emoji="")
        return cls(emoji=emoji_unicode)

    def to_unicode(self) -> str:
        """
        Returns the raw emoji Unicode string for database storage.
        Example: "🐍"
        """
        return self.emoji

    def __str__(self) -> str:
        return self.emoji

    def json_serialize(self) -> str:
        """
        Returns the raw emoji string (for serialization or JSON dumps).
        """
        return self.emoji
