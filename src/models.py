from tortoise.models import Model
from tortoise import fields
from dateutil import tz
from typing import Any, Optional, Union, Type
import datetime
from enum import Enum

class DaysEnum(int, Enum):
    sunday = 6
    monday = 0
    tuesday = 1
    wednesday = 2
    thursday = 3
    friday = 4
    saturday = 5

class StatusEnum(str, Enum):
    success = "Completed"
    running = "Running"

utc = tz.gettz("utc")

def to_utc_datetime(value: datetime.datetime)->datetime.datetime:
    if value.tzinfo is None:
        return value
    else:
        value = value.astimezone(utc)
        value = value.replace(tzinfo=None)
        return value
    
class UTCDateTimeField(fields.DatetimeField):    
    class _db_postgres:
        SQL_TYPE = "TIMESTAMP"
        
    def __init__(self, auto_now: bool = False, auto_now_add: bool = False, **kwargs: Any) -> None:
        super().__init__(auto_now, auto_now_add, **kwargs)
        
    def to_db_value(self, value: Optional[datetime.datetime], instance: "Union[Type[Model], Model]") -> Optional[datetime.datetime]:
        if value is None:
            return super().to_db_value(value, instance)
        else:
            return to_utc_datetime(value=value)
        
    def to_python_value(self, value: Any) -> Optional[datetime.datetime]:
        if value is None:
            return super().to_python_value(value)
        else:
            return to_utc_datetime(value=value)

class StoreStatusTable(Model):
    id = fields.BigIntField(pk=True)
    store_id = fields.BigIntField(null=False)
    timestamp_utc = UTCDateTimeField(null=False, index=True)
    status = fields.BooleanField(null=False)

class StoreScheduleTable(Model):
    id = fields.BigIntField(pk=True)
    store_id = fields.BigIntField(null=False)
    day = fields.IntEnumField(enum_type=DaysEnum, null=False)
    start_time_local = fields.TextField(null=False)
    end_time_local = fields.TextField(null=False)


class StoreTimeZoneTable(Model):
    id = fields.BigIntField(pk=True)
    store_id = fields.BigIntField(null=False)
    timezone_str = fields.CharField(max_length=50)

class ReportStatusTable(Model):
    id = fields.UUIDField(pk=True)
    status = fields.CharEnumField(StatusEnum, max_length=20, index=True, null=False)
    report_link = fields.TextField(null=True)