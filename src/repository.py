from typing import Tuple, Union, List, Dict
from dateutil import parser
import datetime

from .models import ReportStatusTable, StatusEnum, StoreScheduleTable, StoreStatusTable, StoreTimeZoneTable

CURRENT_TIME = parser.parse("2023-01-25 18:13:22.47922")

async def check_if_some_report_generation_in_process()->Tuple[bool, Union[ReportStatusTable, None]]:
    running_processes = list(await ReportStatusTable.filter(status=StatusEnum.running))
    if len(running_processes) == 0:
        return (False, None)
    else:
        return (True, running_processes[0])
    
async def create_report_instance() -> ReportStatusTable:
    return await ReportStatusTable.create(status=StatusEnum.running)

async def get_report_status(report_id:str) -> Union[ReportStatusTable, None]:
    return await ReportStatusTable.filter(id=report_id).first()

async def complete_report_status(report_id: str, report_link: str) -> None:
    return await ReportStatusTable.filter(id=report_id).update(report_link=report_link, status=StatusEnum.success)

async def get_last_week_status() -> List[Dict]:
    return await StoreStatusTable.filter(
        timestamp_utc__gte=CURRENT_TIME - datetime.timedelta(days=7, hours=1)
    ).values(
        store_id = "store_id",
        timestamp_utc = "timestamp_utc",
        status = "status"
    )

async def get_all_store_timezones() -> List[Dict]:
    return await StoreTimeZoneTable.all().values()

async def get_all_schedules() -> List[Dict]:
    return await StoreScheduleTable.all().values()