# -*- coding: utf-8 -*-
import re
from datetime import datetime, timedelta, timezone
from typing import Union

from plenary import constant

__all__ = [
    'datetime',
    'timedelta',
    'timezone',
    'now',
    'parse_datetime',
    'time_round'
]


TParseDateTime = Union[int, float, str, datetime]


_DATETIME_FORMATS = [
    constant.FORMAT_TIMESTAMP_CONSOLE,
    constant.FORMAT_TIMESTAMP_CONSOLE_SHORT,
    constant.FORMAT_TIMESTAMP_FILENAME,
    constant.FORMAT_TIMESTAMP_FILENAME_SHORT
]


_REGEX_TIMESTAMP = re.compile(r'^(\d+\.?\d*)([smun]?)$')


def now(as_local: bool = True) -> datetime:
    """ Get timezone aware current date/time as UTC or local time.

    :param as_local: if True get datetime in local timezone, else in UTC
    :return: datetime
    """
    dt_utc = datetime.now(timezone.utc)

    if not as_local:
        return dt_utc

    return dt_utc.astimezone()


class DateTimeParseError(ValueError):
    pass


def parse_datetime(value: TParseDateTime, numeric_utc: bool = True) -> datetime:
    """ Date/time or timestamp parser for use with argparse.

    :param value: input
    :param numeric_utc: if True treat numeric values as UTC based, otherwise assume local
    :return: datetime
    :raises ValueError: on invalid input
    """
    if isinstance(value, datetime):
        # Already a datetime
        return value

    if isinstance(value, int) or isinstance(value, float):
        # Parse from timestamp
        if numeric_utc:
            return datetime.utcfromtimestamp(value).replace(tzinfo=timezone.utc)
        else:
            return datetime.fromtimestamp(value).astimezone()

    timestamp_match = _REGEX_TIMESTAMP.match(value.lower())

    if timestamp_match is not None:
        timestamp = float(timestamp_match[1])

        if timestamp_match[2] == 'm':
            timestamp /= 1e3
        elif timestamp_match[2] == 'u':
            timestamp /= 1e6
        elif timestamp_match[2] == 'n':
            timestamp /= 1e9

        if numeric_utc:
            return datetime.utcfromtimestamp(timestamp).replace(tzinfo=timezone.utc)
        else:
            return datetime.fromtimestamp(timestamp).astimezone()
    else:
        try:
            # Try ISO format first
            return datetime.fromisoformat(value)
        except ValueError:
            for datetime_format in _DATETIME_FORMATS:
                try:
                    # Try other formats
                    return datetime.strptime(value, datetime_format)
                except ValueError:
                    pass

        raise DateTimeParseError(f"Provided value {value!r} does not match any known datetime format")


def time_round(t: datetime, nearest: timedelta) -> datetime:
    """ Round datetime to nearest interval defined as a timedelta.

    :param t: input datetime
    :param nearest: nearest timedelta to round to
    :return: datetime
    """
    t_utc = t.replace(tzinfo=timezone.utc)

    dt = (t_utc.timestamp() - round(t_utc.timestamp() / nearest.total_seconds()) * nearest.total_seconds())

    if t.tzinfo is not None:
        return (t.astimezone(timezone.utc) - timedelta(seconds=dt)).astimezone(t.tzinfo)
    else:
        return t - timedelta(seconds=dt)
