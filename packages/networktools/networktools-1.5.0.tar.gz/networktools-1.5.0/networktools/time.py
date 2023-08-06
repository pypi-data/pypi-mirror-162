"""
Some time related functions

"""

from datetime import datetime, timedelta
from pytz import timezone
import pytz
from typing import Optional, Dict, Tuple, Union
from pydantic import validate_arguments, Field
from pydantic.typing import Annotated
from numbers import Number

def timestamp() -> float:
    this_tz = pytz.timezone('UTC')
    now_naive = datetime.utcnow()
    nowt = this_tz.localize(now_naive)
    return nowt.timestamp()


def now() -> datetime:
    this_tz = pytz.timezone('UTC')
    nowt = datetime.utcnow()
    start_date = this_tz.localize(nowt)
    return start_date


def now_str(format_date:Optional[str]=None) -> str:
    this_tz = pytz.timezone('UTC')
    nowt = datetime.now(tz=this_tz).astimezone(tz=this_tz)
    if not format_date:
        return nowt.isoformat()
    return nowt.strftime(format_date)

# https://pydantic-docs.helpmanual.io/usage/schema/#field-customisation
WeekYear = Annotated[int, Field(ge=1)]
MillisecondsWeek = Annotated[int, Field(ge=0, le=604800000)]

@validate_arguments
def gps_week2time(week:WeekYear, time_week:MillisecondsWeek) -> datetime:
    # start date
    try:
        this_tz = pytz.timezone('UTC')
        t0 = datetime(1980, 1, 6)
        start_date = this_tz.localize(t0)
    except Exception as e:
        print(f"Error en generar start_date {e}")
        raise e
        # how many weeks and milliseconds after start_date
    delta = timedelta(weeks=week, milliseconds=time_week)
    final_date = start_date+delta
    return final_date



def gps_time(
        data: Dict[str, Dict[str, int]],
        leap:int=18) -> Tuple[datetime, str]:
    fd = datetime.utcnow()
    utc = timezone("UTC")
    final_date = utc.localize(fd)
    if 'UTC' in data.keys():
        datautc = data['UTC']
        time_week = datautc['GPS_MS_OF_WEEK']
        week = datautc['GPS_WEEK']
        offset = datautc['UTC_OFFSET']
        offset_time = timedelta(seconds=-offset)
        final_date = gps_week2time(week, time_week)+offset_time
        source = 'UTC'
    elif 'TIME' in data.keys():
        LEAP = leap
        time = data['TIME']
        GPS_WEEK = time['GPS_WEEK']
        GPS_TIME = time['GPS_TIME']  # miliseconds
        offset_time = timedelta(seconds=-LEAP)
        final_date = gps_week2time(GPS_WEEK, GPS_TIME)+offset_time
        source = 'TIME'
    elif "POSITION_BLOCK" in data.keys():
        GPS_WEEK = data["POSITION_BLOCK"].get("GPS_WEEK",1)
        GPS_MILLISECONDS = data["POSITION_BLOCK"].get("GPS_MILLISECONDS",0)
        offset_time = timedelta(seconds=-leap)
        source = 'POSITION_BLOCK'
        final_date = gps_week2time(
            GPS_WEEK,
            GPS_MILLISECONDS) + offset_time
    return final_date, source


def get_datetime_di(delta: int = 600) -> str:
    #"Datetime UTC Isoformat":
    df = datetime.now(tz=pytz.utc)
    di = df+timedelta(seconds=-delta)
    return di.astimezone(tz=pytz.utc).isoformat()
