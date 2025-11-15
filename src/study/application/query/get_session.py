from src.study.application.repository.contracts import ISessionRepository
from src.study.domain.models.learning_session import LearningSession
from src.study.domain.value_objects import LearningSessionId


class GetSession:
    def __init__(self, repository: ISessionRepository):
        self.repository = repository

    async def get(self, session_id: LearningSessionId) -> LearningSession:
        return await self.repository.find(session_id)
