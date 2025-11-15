from fastapi import APIRouter, Body, Depends
from core.auth import get_current_user
from punq import Container
from core.container import get_container
from src.shared.user.iuser import IUser
from src.user.application.command.create_report import CreateReportHandler
from src.user.infrastructure.http.report_requests import CreateReportRequest


router = APIRouter(tags=["Reports"])


@router.post("/api/v2/reports")
async def create_report(
    user: IUser = Depends(get_current_user),
    request: CreateReportRequest = Body(...),
    container: Container = Depends(get_container),
) -> dict:
    create_report_handler: CreateReportHandler = container.resolve(CreateReportHandler)

    from src.user.application.command.create_report import CreateReport

    command = CreateReport(
        type=request.type,
        description=request.description,
        email=request.email,
        user_id=user.get_id(),
        reportable_id=str(request.reportable_id) if request.reportable_id else None,
        reportable_type=request.reportable_type.value if request.reportable_type else None,
    )

    result = await create_report_handler.handle(command)

    return {"id": result.report_id}
