import uuid
from sqlalchemy.ext.asyncio import async_sessionmaker
from src.entry.db import engine
import pytest
from src.entry.container import container

from src.entry.models import Users
from src.shared.util.hash import IHash
from tests.conftest import session

async def create_user(session, email="test@example.com", password="secret") -> Users:
    hasher = container.resolve(IHash)
    user = Users(
        id=uuid.uuid4(),
        email=email,
        name="Test User",
        password=hasher.make(password),
        picture=None
    )
    session.add(user)
    await session.flush()
    await session.refresh(user)
    await session.commit()
    return user