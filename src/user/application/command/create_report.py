from dataclasses import dataclass
from typing import Optional
from src.shared.value_objects.user_id import UserId
from src.user.application.repository.report_repository import IReportRepository


@dataclass(frozen=True)
class CreateReport:
    type: str
    description: str
    email: Optional[str]
    user_id: Optional[UserId]
    reportable_id: Optional[str]
    reportable_type: Optional[str]


@dataclass(frozen=True)
class CreateReportResult:
    report_id: int


class CreateReportHandler:
    def __init__(self, report_repository: IReportRepository):
        self.report_repository = report_repository

    async def handle(self, command: CreateReport) -> CreateReportResult:
        report_id = await self.report_repository.create(
            type=command.type,
            description=command.description,
            email=command.email,
            user_id=command.user_id,
            reportable_id=command.reportable_id,
            reportable_type=command.reportable_type,
        )

        return CreateReportResult(report_id=report_id)
