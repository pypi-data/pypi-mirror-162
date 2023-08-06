# -*- coding: utf-8 -*-
import os
from datetime import timezone
from getpass import getuser
from socket import getfqdn
from tempfile import gettempdir
from typing import Any, Mapping

from plenary import constant, localtime

__all__ = [
    'generate_format'
]


_format_system: Mapping[str, str] = {
    'path_home': os.path.expanduser('~'),
    'path_temp': gettempdir(),
    'sys_hostname': getfqdn(),
    'sys_username': getuser(),
    **{'env_' + env_var: env_val for env_var, env_val in os.environ.items()}
}


def generate_format(format_spec: str, *args: Any, **kwargs: Any) -> str:
    """ Format specified string with system and environment variables.

    :param format_spec: formatted string specification
    :param args: additional position format arguments
    :param kwargs: additional keyword format arguments
    :return: formatted string
    :raises IndexError: on invalid format specification
    :raises KeyError: on format specification with unknown field codes
    """
    timestamp = localtime.now()
    timestamp_utc = timestamp.astimezone(timezone.utc)

    format_mapping = {
        'date': timestamp.strftime(constant.FORMAT_DATE),
        'date_utc': timestamp_utc.strftime(constant.FORMAT_DATE),
        'time': timestamp.strftime(constant.FORMAT_TIME),
        'time_utc': timestamp_utc.strftime(constant.FORMAT_TIME),
        'datetime_filename': timestamp.strftime(constant.FORMAT_TIMESTAMP_FILENAME),
        'datetime_console': timestamp.strftime(constant.FORMAT_TIMESTAMP_CONSOLE),
        'datetime_utc_filename': timestamp_utc.strftime(constant.FORMAT_TIMESTAMP_FILENAME),
        'datetime_utc_console': timestamp_utc.strftime(constant.FORMAT_TIMESTAMP_CONSOLE),
        'datetime_iso': timestamp.isoformat(),
        'datetime_utc_iso': timestamp_utc.isoformat(),
        'timestamp_s': str(int(timestamp.timestamp())),
        'timestamp_ms': str(int(timestamp.timestamp() * 1000)),
        'timestamp_us': str(int(timestamp.timestamp() * 1000000))
    }

    format_mapping.update(_format_system)
    format_mapping.update(kwargs)

    return format_spec.format(*args, **format_mapping)
