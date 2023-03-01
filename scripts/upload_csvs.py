import pandas as pd
from tortoise import Tortoise
from dateutil import parser

from src.models import StoreStatusTable, StoreScheduleTable, StoreTimeZoneTable
from src.config import DBURL

STORE_STATUS_FILE = "./static/store_status.csv"
STORE_SCHEDULE_FILE = "./static/store_schedule.csv"
STORE_TIMEZONE_FILE = "./static/store_timezone.csv"

async def upload_store_status():
    df = pd.read_csv(STORE_STATUS_FILE)

    await StoreStatusTable.bulk_create(
        [StoreStatusTable(**{
            "store_id": row["store_id"],
            "status": True if row["status"].strip()=="active" else False,
            "timestamp_utc": parser.parse(row["timestamp_utc"][:-4])
        }) for _, row in df.iterrows()],
        batch_size=100
    )

async def upload_schedule():
    df = pd.read_csv(STORE_SCHEDULE_FILE)

    await StoreScheduleTable.bulk_create(
        [StoreScheduleTable(**row.to_dict()) for _, row in df.iterrows()],
        batch_size=100
    )

async def upload_timezone():
    df = pd.read_csv(STORE_TIMEZONE_FILE)

    await StoreTimeZoneTable.bulk_create(
        [StoreTimeZoneTable(**row.to_dict()) for _, row in df.iterrows()],
        batch_size=100
    )

async def upload():
    await Tortoise.init(
        db_url=DBURL,
        modules={"models": ["src.models"]}
    )
    await upload_schedule()
    await upload_store_status()
    await upload_timezone()