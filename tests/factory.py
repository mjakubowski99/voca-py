import uuid
from core.container import container
from core.models import FlashcardDecks, Flashcards, Users
from src.flashcard.domain.enum import FlashcardOwnerType
from src.flashcard.domain.models.owner import Owner
from src.flashcard.domain.value_objects import OwnerId
from src.shared.enum import Language, LanguageLevel
from src.shared.util.hash import IHash


async def create_user_owner(session) -> Owner:
    user = await create_user(session)
    return Owner(id=OwnerId(value=user.id), flashcard_owner_type=FlashcardOwnerType.USER)


async def create_user(session, email="test@example.com", password="secret") -> Users:
    hasher = container.resolve(IHash)
    user = Users(
        id=uuid.uuid4(), email=email, name="Test User", password=hasher.make(password), picture=None
    )
    session.add(user)
    await session.flush()
    await session.refresh(user)
    await session.commit()
    return user


async def create_flashcard(
    session,
    deck: FlashcardDecks,
    owner: Owner,
    front_word: str = "Default front",
    back_word: str = "Default back",
    front_context: str = "Default context",
    back_context: str = "Default back context",
    front_lang: Language = Language.PL,
    back_lang: Language = Language.EN,
) -> Flashcards:
    """
    Factory to create a Flashcard for testing.
    """

    flashcard = Flashcards(
        flashcard_deck_id=deck.id,
        front_word=front_word,
        back_word=back_word,
        front_context=front_context,
        back_context=back_context,
        front_lang=front_lang.value,
        back_lang=back_lang.value,
        user_id=owner.id.value if owner.is_user() else None,
        admin_id=owner.id.value if owner.is_admin() else None,
    )
    session.add(flashcard)
    await session.flush()
    await session.refresh(flashcard)
    await session.commit()
    return flashcard


async def create_flashcard_deck(
    session,
    owner: Owner,
    name: str = "Default Deck",
    tag: str = "default_tag",
    default_language_level: LanguageLevel = LanguageLevel.B2,
) -> FlashcardDecks:
    """
    Factory to create a FlashcardDeck for testing.
    """

    deck = FlashcardDecks(
        name=name,
        tag=tag,
        user_id=owner.id.value if owner.is_user() else None,
        admin_id=owner.id.value if owner.is_admin() else None,
        default_language_level=default_language_level.value,
    )
    session.add(deck)
    await session.flush()
    await session.refresh(deck)
    await session.commit()
    return deck
