from fastapi import APIRouter, BackgroundTasks
from fastapi.exceptions import HTTPException

from .datatypes import TriggerReportOutPut, ReportStatusOutPut
from .repository import check_if_some_report_generation_in_process, create_report_instance, get_report_status
from .core import generate_report, start_report_generation

router = APIRouter()

@router.post("/trigger_report", response_model=TriggerReportOutPut)
async def trigger_report(backgroud_tasks: BackgroundTasks):
    running, report_instance = await check_if_some_report_generation_in_process()
    if running:
        return {"report_id": str(report_instance.id)}
    
    report_instance = await create_report_instance()
    backgroud_tasks.add_task(start_report_generation, str(report_instance.id))
    return {"report_id": str(report_instance.id)}


@router.get("/get_report", response_model=ReportStatusOutPut)
async def get_report(report_id: str):
    report_instance = await get_report_status(report_id=report_id)
    if report_instance is None:
        raise HTTPException(status_code=204, detail="No such report id found.")
    return ReportStatusOutPut(status=report_instance.status, report_link=report_instance.report_link)