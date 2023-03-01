import pandas as pd, datetime, sys
from dateutil import tz
import asyncio
import multiprocessing

from .repository import complete_report_status, get_last_week_status, get_all_schedules, get_all_store_timezones,\
    CURRENT_TIME
from .config import DEFAULT_TIMEZONE, REPORT_DIR, REPORT_LINK, BASEURL


def parse_time(t:str):
    times = t.split(":")
    for i in range(3):
        times[i] = int(times[i])
    return times

def resample_and_calculate(store_id: int, df: pd.DataFrame, schedule_dict:dict, timezones:dict):
    df["status"] = df["status"].apply(lambda x: 1 if x==True else 0)

    df.set_index("timestamp_utc", inplace=True)
    df = df.resample("1H").ffill(limit=1).interpolate(method="linear")
    df_interpolated = df.reset_index()

    df_interpolated['status'] = df_interpolated['status'].apply(lambda x: 1 if x >= 0.5 else 0)

    df_interpolated["timestamp_utc"] = pd.to_datetime(df_interpolated["timestamp_utc"],utc=True)
    df_interpolated['timestamp_utc'] = df_interpolated['timestamp_utc'].dt.round('H')
    df_interpolated.drop_duplicates(subset=['store_id', 'timestamp_utc'], keep='last', inplace=True)


    df_interpolated["timestamp_local"] = df_interpolated.apply(lambda row: row["timestamp_utc"].astimezone(tz.gettz(timezones.get(row["store_id"],DEFAULT_TIMEZONE))), axis=1)
    df_interpolated["week_day"] = df_interpolated.apply(lambda row: row["timestamp_local"].weekday(), axis=1)

    default_time_data = {
        "start_time": [0, 0, 0],
        "end_time": [23, 59, 59]
    }

    data = {
        "store_id": store_id,
        "last_week_uptime_hours": 0,
        "last_week_downtime_hours": 0,
        "last_day_uptime_hours": 0,
        "last_day_downtime_hours": 0,
        "last_hour_uptime_minutes": 0,
        "last_hour_downtime_minutes": 0
    }

    timezone = tz.gettz(timezones.get(store_id, DEFAULT_TIMEZONE))
    cnttime = CURRENT_TIME.astimezone(timezone)
    last_week_start = cnttime - datetime.timedelta(days=7)
    last_day_start = cnttime - datetime.timedelta(days=1)
    last_hour_start = cnttime - datetime.timedelta(hours=1)

    for idx, row in df_interpolated.iterrows():
        weekday = row["week_day"]
        start_time_data = schedule_dict.get((store_id, weekday), default_time_data)["start_time"]
        end_time_data = schedule_dict.get((store_id, weekday), default_time_data)["end_time"]
        timestamp = row["timestamp_local"]

        start_time = datetime.datetime(
            year=timestamp.year,
            month=timestamp.month,
            day=timestamp.day,
            hour=start_time_data[0],
            minute=start_time_data[1],
            second=start_time_data[2],
            tzinfo=timestamp.tzinfo
        )
        end_time = datetime.datetime(
            year=timestamp.year,
            month=timestamp.month,
            day=timestamp.day,
            hour=end_time_data[0],
            minute=end_time_data[1],
            second=end_time_data[2],
            tzinfo=timestamp.tzinfo
        )

        end_time = min(end_time, cnttime)


        def calculate_time(min_time):
            if min_time<=start_time<timestamp<=end_time:
                return min(end_time-timestamp, datetime.timedelta(hours=1))
            if start_time<=min_time<timestamp<=end_time:
                return min(end_time-timestamp, datetime.timedelta(hours=1))
            if min_time<=timestamp<start_time<end_time:
                if start_time <= timestamp + datetime.timedelta(hours=1) <= end_time:
                    return datetime.timedelta(hours=1) - (start_time-timestamp)
                elif start_time<end_time<=timestamp+datetime.timedelta(hours=1):
                    return end_time-start_time
            if start_time <= timestamp <= min_time <= end_time:
                if min_time <= timestamp + datetime.timedelta(hours=1) <= end_time:
                    return datetime.timedelta(hours=1) - (min_time-timestamp)
                elif min_time<end_time<=timestamp+datetime.timedelta(hours=1):
                    return end_time-min_time
            if timestamp <= start_time <= min_time <= end_time:
                if min_time <= timestamp + datetime.timedelta(hours=1) <= end_time:
                    return datetime.timedelta(hours=1) - (min_time-timestamp)
                elif min_time<end_time<=timestamp+datetime.timedelta(hours=1):
                    return end_time-min_time
            if timestamp <= min_time<=start_time<=end_time:
                if start_time <= timestamp + datetime.timedelta(hours=1) <= end_time:
                    return datetime.timedelta(hours=1) - (start_time-timestamp)
                elif start_time<end_time<=timestamp+datetime.timedelta(hours=1):
                    return end_time-start_time
            return datetime.timedelta(hours=0)


        if row["status"]==1:
            data["last_week_uptime_hours"] += round(calculate_time(last_week_start).total_seconds()/3600, 2)
            data["last_day_uptime_hours"] += round(calculate_time(last_day_start).total_seconds()/3600, 2)
            data["last_hour_uptime_minutes"] += round(calculate_time(last_hour_start).total_seconds()/60, 2)
        if row["status"]==0:
            data["last_week_downtime_hours"] +=  round(calculate_time(last_week_start).total_seconds()/3600, 2)
            data["last_day_downtime_hours"] += round(calculate_time(last_day_start).total_seconds()/3600, 2)
            data["last_hour_downtime_minutes"] += round(calculate_time(last_hour_start).total_seconds()/60, 2)
    
    return data

async def start_report_generation(report_id: str)->None:
    store_status_data = await get_last_week_status()
    store_time_zones = await get_all_store_timezones()
    timezones = {}
    for store_timzone in store_time_zones:
        timezones[store_timzone["store_id"]] = store_timzone["timezone_str"]

    store_schedule = await get_all_schedules()
    schedule_dict = {}
    for sch in store_schedule:
        schedule_dict[(sch["store_id"], sch["day"])] = {
            "start_time": parse_time(sch["start_time_local"]),
            "end_time": parse_time(sch["end_time_local"])
        }


    df = pd.DataFrame(store_status_data)
    df["timestamp_utc"] = pd.to_datetime(df["timestamp_utc"], utc=True)

    report_data = []
    with multiprocessing.Pool(max_workers=3) as pool:
        try:
            report_data = pool.starmap(resample_and_calculate, [(store_id, storedf, schedule_dict, timezones) for store_id, storedf in df.groupby("store_id")])
        except Exception as e:
            exc_type, exc_value, traceback = sys.exc_info()
            print(f"Exception: {exc_type} - {exc_value}")
            raise e
    newdf = pd.DataFrame(report_data)
    newdf.to_csv(REPORT_DIR+"/"+report_id+".csv")
    await complete_report_status(report_id=report_id, report_link=BASEURL+REPORT_LINK+"/"+report_id+".csv")

def generate_report(report_id: str):
    loop = asyncio.get_event_loop()
    loop.set_debug(enabled=True)
    loop.run_until_complete(start_report_generation(report_id=report_id))
    loop.close()