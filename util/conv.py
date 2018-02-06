# Various datetime helper/conversion functions

import datetime as dt
from sys import exit
import re


def dt_to_str(timestamp: dt.datetime):
    """ Convert datetime to string and ensure there are always .xxxxxx microseconds """
    strtime = str(timestamp)
    if '.' not in strtime:
        strtime += ".000000"
    return strtime


def dt_approx_by_delta(zerodtime: dt.datetime, starttime: dt.datetime, delta: dt.timedelta):
    timedifference = starttime - zerodtime
    multiply = timedifference // delta

    if multiply > 0:
        multiply -= 1

    return zerodtime + (multiply*delta)


def dt_clear_microsecond(intime: dt.datetime) -> dt.datetime:
    return intime.replace(microsecond=0)

def dt_clear_second(intime: dt.datetime) -> dt.datetime:
    return intime.replace(microsecond=0, second=0)

def dt_clear_minute(intime: dt.datetime) -> dt.datetime:
    return intime.replace(microsecond=0, second=0, minute=0)

def dt_clear_hour(intime: dt.datetime) -> dt.datetime:
    return intime.replace(microsecond=0, second=0, minute=0, hour=0)



def parse_datetimestring_to_dt(instring: str) -> dt.datetime:
    if 'T' in instring:
        cleaned = instring.replace("T"," ")
    else:
        cleaned = instring

    # with microseconds?
    m = re.search('(\d\d\d\d\d\d)$', cleaned)
    if m:
        return dt.datetime.strptime(cleaned, '%Y-%m-%d %H:%M:%S.%f')

    # with seconds?
    m = re.search(' (\d\d:\d\d:\d\d)$', cleaned)
    if m:
        return dt.datetime.strptime(cleaned, '%Y-%m-%d %H:%M:%S')

    # with minutes?
    m = re.search(' (\d\d:\d\d)$', cleaned)
    if m:
        return dt.datetime.strptime(cleaned, '%Y-%m-%d %H:%M')

    # just date?
    m = re.search('^(\d\d\d\d-\d\d-\d\d)', cleaned)
    if m:
        return dt.datetime.strptime(cleaned, '%Y-%m-%d')

    print("Help! Unknown datetime format:")
    print(instring)
    exit(1)


# borrowed&modified from https://gist.github.com/thatalextaylor/7408395
def printNiceTimeDelta(intimedelta):
    seconds = int(intimedelta.total_seconds())
    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    return '%3d-%02d:%02d:%02d' % (days, hours, minutes, seconds)
