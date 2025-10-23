import uuid
from src.entry.models import Users
from src.entry.container import container
from src.shared.util.hash import IHash

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
    await session.commit()
    await session.refresh(user)
    return user