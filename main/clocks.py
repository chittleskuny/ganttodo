from time import time, mktime, strftime, strptime, localtime
from datetime import date, datetime, timedelta

import logging

ZERO_LEFT = 0  # 24:00:00
ZERO_RIGHT = 1 # 00:00:00

ONE_DAY = timedelta(days=1)
ONE_DAY_TIMESTAMP = 1000 * 60 * 60 * 24

RESOLUTION = 2
UNIT_TIMESTAMP = ONE_DAY_TIMESTAMP // RESOLUTION # TODO
UNIT_TIMESTAMPS = [UNIT_TIMESTAMP * i  for i in range(RESOLUTION + 1)]

LOG_CLOCKS = False


def convert_datetime_to_timestamp(_datetime):
    result = 1000 * int(mktime(_datetime.timetuple()))
    if LOG_CLOCKS:
        logging.debug('%s -> %s' % (_datetime, result))
    return result


def convert_timestamp_to_datetime(timestamp):
    result = date.fromtimestamp(timestamp / 1000)
    if LOG_CLOCKS:
        logging.debug('%s -> %s' % (timestamp, result))
    return result


def convert_timestr_yyyy_mm_dd_to_datetime(timestr):
    result = strptime(timestr, '%Y-%m-%d')
    if LOG_CLOCKS:
        logging.debug('%s -> %s' % (timestr, result))
    return result


def convert_timestamp_to_timestr_yyyy_mm_dd(timestamp, zero_left_or_right=1):
    result = None
    if zero_left_or_right == ZERO_LEFT:
        result =  strftime('%Y-%m-%d', localtime(timestamp / 1000 - 1))
    else:
        result = strftime('%Y-%m-%d', localtime(timestamp / 1000))

    if LOG_CLOCKS:
        logging.debug('%s -> %s' % (timestamp, result))
    return result


def convert_datetime_to_timestr_yyyy_mm_dd(_datetime, zero_left_or_right=1):
    result = None
    if zero_left_or_right == ZERO_LEFT:
        result = (_datetime - datetime.timedelta(seconds=1)).strftime('%Y-%m-%d')
    else:
        result = _datetime.strftime('%Y-%m-%d')

    if LOG_CLOCKS:
        logging.debug('%s -> %s' % (_datetime, result))
    return result


def convert_datetime_to_timestr_yyyy_mm_dd_hh_mm_ss(_datetime):
    result = None
    result = _datetime.strftime('%Y-%m-%d %H:%M:%S')

    if LOG_CLOCKS:
        logging.debug('%s -> %s' % (_datetime, result))
    return result


def calculate_fraction(timestamp, zero_left_or_right=1):
    today_timestamp = convert_datetime_to_timestamp(date.today())
    numerator = (abs(today_timestamp - timestamp) // UNIT_TIMESTAMP) % RESOLUTION
    denominator = RESOLUTION
    result = None
    if zero_left_or_right == ZERO_LEFT and numerator == 0:
        result = '%d/%d' % (denominator, denominator)
    else:
        result = '%d/%d' % (numerator, denominator)

    if LOG_CLOCKS:
        logging.debug('%s -> %s' % (timestamp, result))
    return result


def convert_timestamp_to_timestr_yyyy_mm_dd_fraction(timestamp, zero_left_or_right=1):
    timestr_yyyy_mm_dd = convert_timestamp_to_timestr_yyyy_mm_dd(timestamp, zero_left_or_right)
    fraction = calculate_fraction(timestamp, zero_left_or_right)
    result = '%s %s' % (timestr_yyyy_mm_dd, fraction)
    if LOG_CLOCKS:
        logging.debug('%s -> %s' % (timestamp, result))
    return result


def convert_datetime_to_timestr_yyyy_mm_dd_fraction(_datetime, zero_left_or_right=1):
    timestr_yyyy_mm_dd = convert_datetime_to_timestr_yyyy_mm_dd(_datetime, zero_left_or_right)
    fraction = calculate_fraction(convert_datetime_to_timestamp(_datetime), zero_left_or_right)
    result = '%s %s' % (timestr_yyyy_mm_dd, fraction)
    if LOG_CLOCKS:
        logging.debug('%s -> %s' % (_datetime, result))
    return result
