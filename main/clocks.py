from time import time, mktime, strftime, strptime, localtime
from datetime import date, datetime, timedelta

import logging
import zoneinfo

LOCAL_TIME_ZONE_INFO = zoneinfo.ZoneInfo('Asia/Shanghai')

ZERO_LEFT = 0  # 24:00:00
ZERO_RIGHT = 1 # 00:00:00

ONE_DAY = timedelta(days=1)
ONE_DAY_TIMESTAMP = 1000 * 60 * 60 * 24

RESOLUTION = 2
UNIT_HOURS = 24 / RESOLUTION
UNIT = timedelta(hours=UNIT_HOURS)
UNITS = [UNIT * i  for i in range(RESOLUTION + 1)]
UNIT_TIMESTAMP = ONE_DAY_TIMESTAMP // RESOLUTION # TODO
UNIT_TIMESTAMPS = [UNIT_TIMESTAMP * i  for i in range(RESOLUTION + 1)]

LOG_CLOCKS = False


def convert_datetime_to_timestamp(_datetime):
    local_datetime = _datetime.astimezone(LOCAL_TIME_ZONE_INFO)
    result = 1000 * int(mktime(local_datetime.timetuple()))
    if LOG_CLOCKS:
        logging.debug('%s -> %s' % (local_datetime, result))
    return result


def convert_timestr_yyyy_mm_dd_to_datetime(timestr):
    result = strptime(timestr, '%Y-%m-%d')
    if LOG_CLOCKS:
        logging.debug('%s -> %s' % (timestr, result))
    return result


def convert_datetime_to_timestr_yyyy_mm_dd(_datetime, zero_left_or_right=1):
    result = None
    if zero_left_or_right == ZERO_LEFT:
        result = (_datetime - timedelta(seconds=1)).strftime('%Y-%m-%d')
    else:
        result = _datetime.strftime('%Y-%m-%d')

    if LOG_CLOCKS:
        logging.debug('%s -> %s' % (_datetime, result))
    return result


def calculate_fraction(_datetime, zero_left_or_right=1):
    last_zero = datetime(
        year=date.today().year,
        month=date.today().month,
        day=date.today().day,
        tzinfo=LOCAL_TIME_ZONE_INFO,
    )
    numerator = ((last_zero - _datetime) // UNIT) % RESOLUTION
    denominator = RESOLUTION
    result = None
    if zero_left_or_right == ZERO_LEFT and numerator == 0:
        result = '%d/%d' % (denominator, denominator)
    else:
        result = '%d/%d' % (numerator, denominator)

    if LOG_CLOCKS:
        logging.debug('%s -> %s' % (_datetime, result))
    return result


def convert_datetime_to_timestr_yyyy_mm_dd_fraction(_datetime, zero_left_or_right=1):
    local_datetime = _datetime.astimezone(LOCAL_TIME_ZONE_INFO)
    timestr_yyyy_mm_dd = convert_datetime_to_timestr_yyyy_mm_dd(local_datetime, zero_left_or_right)
    fraction = calculate_fraction(_datetime, zero_left_or_right)
    result = '%s %s' % (timestr_yyyy_mm_dd, fraction)
    if LOG_CLOCKS:
        logging.debug('%s -> %s' % (_datetime, result))
    return result
