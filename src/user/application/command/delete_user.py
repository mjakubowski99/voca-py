from dataclasses import dataclass
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src.shared.flashcard.contracts import IFlashcardFacade
from src.shared.value_objects.user_id import UserId
from src.study.application.repository.contracts import ISessionRepository
from src.user.application.repository.contracts import IUserRepository
from src.user.application.repository.report_repository import IReportRepository
import logging

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class DeleteUser:
    user_id: UserId
    email: str  # For verification


class DeleteUserHandler:
    def __init__(
        self,
        session: AsyncSession,
        flashcard_facade: IFlashcardFacade,
        user_repository: IUserRepository,
        report_repository: IReportRepository,
        session_repository: ISessionRepository,
    ):
        self.session = session
        self.flashcard_facade = flashcard_facade
        self.user_repository = user_repository
        self.report_repository = report_repository
        self.session_repository = session_repository

    async def handle(self, command: DeleteUser) -> None:
        try:
            user = await self.user_repository.find_by_id(command.user_id)
            if user.get_email() != command.email:
                raise HTTPException(status_code=400, detail="Email does not match the user account")
        except ValueError:
            raise HTTPException(status_code=404, detail="User not found")

        try:
            await self.flashcard_facade.delete_user_data(command.user_id)

            await self.report_repository.detach_from_user(command.user_id)

            await self.session_repository.delete_all_for_user(command.user_id)

            await self.user_repository.delete(command.user_id)

            await self.session.commit()

        except Exception as exception:
            await self.session.rollback()
            raise exception
