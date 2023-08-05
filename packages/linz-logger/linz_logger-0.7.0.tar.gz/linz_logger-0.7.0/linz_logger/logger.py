import os
import time
from enum import Enum
from functools import partial

import structlog
from structlog.contextvars import bind_contextvars, clear_contextvars, merge_contextvars, unbind_contextvars
from structlog.exceptions import DropEvent


class LogLevel(Enum):
    """
    Convert to pinojs standard level numbers
    """

    critical = 60
    exception = 50
    error = 50
    warn = 40
    warning = 40
    info = 30
    debug = 20
    notset = 10
    trace = 10


current_level = LogLevel.debug
clear_contextvars()


def set_level(level: LogLevel):
    """
    Set the loggging level.
    All logs less than the given value will not be displayed.
    """
    global current_level
    current_level = level


def set_contextvars(key_value: dict):
    """Set the context variables.

    Args:
        key_value (dict): A dictionnary of key-value pairs.
    """
    bind_contextvars(**key_value)


def remove_contextvars(keys):
    """Remove the context variables.

    Args:
        keys (list): A list of keys.
    """
    unbind_contextvars(*keys)


def level_filter(_, __, event_dict: dict):
    """
    Silently drop logs lower than the set level.
    """
    if event_dict.get("level", 0) < current_level.value:
        raise DropEvent
    return event_dict


structlog.PrintLogger.trace = structlog.PrintLogger.msg
pid = os.getpid()
# This is a standard format for the function so it needs all three arguments
# Even thought we do not use them
# pylint: disable=unused-argument
def add_default_keys(current_logger, method_name: str, event_dict: dict):
    """
    Configure structlog to output the same format as pinojs
    {
        "level": 30,
        "time": 1571696532994,
        "pid": 10671,
        "hostname": "Ubuntu1",
        "id": "01DQR6KQG0K60TP4T1C4VC5P74",
        "msg": "SomeMessage",
        "v": 1
    }
    """
    event_dict["level"] = LogLevel[method_name].value if LogLevel[method_name] else 10
    # Time needs to be in ms
    event_dict["time"] = int(time.time() * 1000)
    # Standard keys that need to be added
    event_dict["v"] = 1
    event_dict["pid"] = pid
    # Remap event -> msg
    event_dict["msg"] = event_dict["event"]
    del event_dict["event"]
    return event_dict


structlog.configure(
    processors=[
        merge_contextvars,
        add_default_keys,
        level_filter,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer(),
    ]
)


def get_log():
    """
    get a instance of the JSON logger
    """
    log = structlog.get_logger()
    log.trace = partial(trace, log)
    return log


def trace(self, event, **kw):
    """
    add trace level
    """
    return self._proxy_to_logger("trace", event, **kw)
