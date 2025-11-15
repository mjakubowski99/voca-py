from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional


class ReportableType(Enum):
    FLASHCARD = "flashcard"


class CreateReportRequest(BaseModel):
    email: str = Field(..., description="Email of the reporter", example="email@email.com")
    type: str = Field(..., description="Type of report", example="inappropriate_content")
    description: str = Field(
        ...,
        description="Description of the report",
        example="This flashcard has inappropriate content",
    )
    reportable_id: Optional[int] = Field(None, description="ID of the reported item", example=1)
    reportable_type: Optional[ReportableType] = Field(
        None, description="Type of the reported item", example="flashcard"
    )
