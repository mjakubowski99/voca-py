from src.study.application.command.create_session import CreateSession
from src.study.application.query.get_session import GetSession
from src.study.application.command.add_next_session_step import AddNextSessionStep
from src.study.application.command.rate_flashcard import RateFlashcard


async def create_session(create_session: CreateSession, add_step: AddNextSessionStep):
    session = await create_session.handle()

    session = await add_step.handle()

    return session


async def get_session(get_session: GetSession, add_step: AddNextSessionStep):
    session = await create_session.handle()

    session = await add_step.handle()

    return session


async def rate_flashcard(
    rate_flashcard: RateFlashcard, get_session: GetSession, add_step: AddNextSessionStep
):
    await rate_flashcard.rate(session_id, rating)

    session = await get_session.get()

    session = await add_step.handle()

    return session


async def answer_unscramble_words_exercise():
    pass


async def answer_word_match_exercise():
    pass


async def skip_unscramble_words_exercise():
    pass


async def skip_word_match_exercise():
    pass
