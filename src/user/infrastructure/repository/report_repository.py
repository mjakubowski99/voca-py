from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import update, insert
from sqlalchemy.ext.asyncio import AsyncSession
from core.models import Reports
from src.user.application.repository.report_repository import IReportRepository
from src.shared.value_objects.user_id import UserId


class ReportRepository(IReportRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        type: str,
        description: str,
        email: Optional[str],
        user_id: Optional[UserId],
        reportable_id: Optional[str],
        reportable_type: Optional[str],
    ) -> int:
        """Create a new report and return its ID."""
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        stmt = (
            insert(Reports)
            .returning(Reports.id)
            .values(
                type=type,
                description=description,
                email=email,
                user_id=user_id.value if user_id else None,
                reportable_id=reportable_id,
                reportable_type=reportable_type,
                created_at=now,
                updated_at=now,
            )
        )
        result = await self.session.execute(stmt)
        report_id = result.scalar_one()
        await self.session.commit()
        return report_id

    async def detach_from_user(self, user_id: UserId) -> None:
        """Detach reports from a user by setting user_id to None."""
        stmt = update(Reports).where(Reports.user_id == user_id.value).values(user_id=None)
        await self.session.execute(stmt)
        await self.session.commit()
