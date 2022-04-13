from time import time, mktime, strftime, strptime, localtime
from datetime import date, datetime, timedelta


import logging


ONE_DAY = timedelta(days=1)
ONE_DAY_TIMESTAMP = 1000 * 60 * 60 * 24

RESOLUTION = 2
UNIT = ONE_DAY_TIMESTAMP // RESOLUTION # TODO

LOG_TIME_CONVERTERS = False


def convert_timestamp_to_datetime(timestamp):
    result = date.fromtimestamp(timestamp / 1000)
    if LOG_TIME_CONVERTERS:
        logging.debug('%s -> %s' % (timestamp, result))
    return result


def convert_timestr_yyyy_mm_dd_to_datetime(timestr):
    result = strptime(timestr, '%Y-%m-%d')
    if LOG_TIME_CONVERTERS:
        logging.debug('%s -> %s' % (timestr, result))
    return result


def convert_datetime_to_timestamp(_datetime):
    result = 1000 * int(mktime(_datetime.timetuple()))
    if LOG_TIME_CONVERTERS:
        logging.debug('%s -> %s' % (_datetime, result))
    return result


def convert_timestamp_to_timestr_yyyy_mm_dd(timestamp):
    result = strftime('%Y-%m-%d', localtime(timestamp / 1000))
    if LOG_TIME_CONVERTERS:
        logging.debug('%s -> %s' % (timestamp, result))
    return result


def convert_datetime_to_timestr_yyyy_mm_dd_fraction(_datetime):
    timestr_yyyy_mm_dd = _datetime.strftime('%Y-%m-%d')

    timestamp = convert_datetime_to_timestamp(_datetime)
    today_timestamp = convert_datetime_to_timestamp(date.today())
    numerator = (abs(today_timestamp - timestamp) // UNIT) % RESOLUTION
    denominator = RESOLUTION
    fraction = '%d/%d' % (numerator, denominator)

    result = '%s %s' % (timestr_yyyy_mm_dd, fraction)
    if LOG_TIME_CONVERTERS:
        logging.debug('%s -> %s' % (_datetime, result))
    return result


def convert_timestamp_to_timestr_yyyy_mm_dd_fraction(timestamp):
    timestr_yyyy_mm_dd = convert_timestamp_to_timestr_yyyy_mm_dd(timestamp)

    today_timestamp = convert_datetime_to_timestamp(date.today())
    numerator = (abs(today_timestamp - timestamp) // UNIT) % RESOLUTION
    denominator = RESOLUTION
    fraction = '%d/%d' % (numerator, denominator)

    result = '%s %s' % (timestr_yyyy_mm_dd, fraction)
    if LOG_TIME_CONVERTERS:
        logging.debug('%s -> %s' % (timestamp, result))
    return 
