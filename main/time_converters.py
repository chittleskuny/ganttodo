from time import time, mktime, strftime, localtime
from datetime import date, datetime, timedelta


ONE_DAY = timedelta(days=1)
ONE_DAY_TIMESTAMP = 1000 * 60 * 60 * 24

RESOLUTION = 2
UNIT = ONE_DAY_TIMESTAMP // RESOLUTION # TODO


def convert_datetime_to_timestamp(_datetime):
    return 1000 * int(mktime(_datetime.timetuple()))


def convert_timestamp_to_datetime(timestamp):
    return date.fromtimestamp(timestamp / 1000)


def convert_timestamp_to_timestr_yyyy_mm_dd(timestamp):
    return strftime('%Y-%m-%d', localtime(timestamp / 1000))


def convert_datetime_to_timestr_yyyy_mm_dd_fraction(_datetime):
    timestr_yyyy_mm_dd = _datetime.strptime('%Y-%m-%d')

    timestamp = convert_datetime_to_timestamp(_datetime)
    today_timestamp = convert_datetime_to_timestamp(date.today())
    numerator = (abs(today_timestamp - timestamp) // UNIT) % RESOLUTION
    denominator = RESOLUTION
    fraction = '%d/%d' % (numerator, denominator)

    return '%s %s' % (timestr_yyyy_mm_dd, fraction)


def convert_timestamp_to_timestr_yyyy_mm_dd_fraction(timestamp):
    timestr_yyyy_mm_dd = convert_timestamp_to_timestr_yyyy_mm_dd(timestamp)

    today_timestamp = convert_datetime_to_timestamp(date.today())
    numerator = (abs(today_timestamp - timestamp) // UNIT) % RESOLUTION
    denominator = RESOLUTION
    fraction = '%d/%d' % (numerator, denominator)

    return '%s %s' % (timestr_yyyy_mm_dd, fraction)
