from abc import ABC, abstractmethod


class SessionFlashcardsBase(ABC):
    def has_flashcard_poll(self) -> bool:
        return not self.has_deck()

    @abstractmethod
    def has_deck(self) -> bool:
        """Should return True if the session is tied to a deck, False otherwise."""
        pass
