from pydantic import BaseModel
from typing import Optional

from .models import StatusEnum

class TriggerReportOutPut(BaseModel):
    report_id: str

class ReportStatusOutPut(BaseModel):
    status: StatusEnum
    report_link: Optional[str]=None