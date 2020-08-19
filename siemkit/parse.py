#   Copyright (C) 2020 CyberSIEM(R)
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

from typing import Any
from collections import deque
import datetime
import re

from siemkit import random

import pytimeparse
# * pytimeparse - MIT License
#     by: wroberts
#     source: https://github.com/wroberts/pytimeparse

import hfilesize
#  * hfilesize - MIT License
#     by: simonzack
#     source: https://github.com/simonzack/hfilesize

import dateparser
# * dateparser - BSD 3-Clause License
#     source: https://github.com/scrapinghub/dateparser
#     license: https://github.com/scrapinghub/dateparser/blob/master/LICENSE


def time(time_string: str) -> datetime.datetime:
    """
    Parse a time string into a datetime object.

        e.g.:

        A string of:
         "21/11/1988"

        Results in:
         datetime.datetime(1988, 11, 21, 0, 0)

    Relative time ("ago") is also supported:

        A string of:
         "1 day ago"

        Results in a `datetime` object set to 1 day before
         the current time of execution.


    :param time_string:
    :return: datetime object
    """
    return dateparser.parse(time_string)


def timedelta(time_delta_string: str) -> datetime.timedelta:
    """
    Parse a time delta string into a timedelta object

        e.g.:

        A string of:
         "2 weeks, 1 day, 12 hours, 30 minutes and 15 seconds"

        Results in:
         datetime.timedelta(days=15, seconds=45015)

        Words like `every` and `and` are ignored.

        A random timedelta can also be acquired using `from` and `to` words:
            "from every 1 second to 2 minutes"

        This will produce a random timedelta between `1 second` to `2 minutes`.

    :param time_delta_string:
    :return: timedelta object
    """
    time_delta_string = time_delta_string.lower().replace("and", '').replace('every', '')

    assigned_range = re.match(r'^.*?from\s(.*?)\sto\s(.*?$)', time_delta_string)

    if assigned_range:
        from_time_string, to_time_string = assigned_range.groups()
        result = random.timedelta(
            datetime.timedelta(seconds=pytimeparse.parse(from_time_string)),
            datetime.timedelta(seconds=pytimeparse.parse(to_time_string))
        )
    else:
        result = datetime.timedelta(seconds=pytimeparse.parse(time_delta_string))

    return result


def size(size_string: str) -> int:
    """
    Parse a file or bandwidth string unit size to a bytes size.

        e.g.:

        A string of:
            "10MB"

        Results in:
            10485760

    :param size_string:
    :return:
    """
    return hfilesize.FileSize(size_string)


def boolean(bool_string: str) -> bool:

    bool_string = bool_string.strip().lower()
    return bool_string in ('t', 'true', 'yes', 'ok', 'on', '1', 'some')


def variable(var_string: str, var_dict: dict) -> Any:

    assign = None

    keys = var_string
    if '=' in var_string:
        m = re.match(r"^\s?([^=\s]+?)\s?=\s?(.*?)\s?$", var_string)
        if m:
            keys, assign = m.groups()

    keys = deque(keys.split('.'))

    while keys:
        if assign is not None and len(keys) == 1:
            if isinstance(var_dict, str):
                var_dict = {var_dict: None}
            var_dict[keys[0]] = assign
            keys.clear()
        else:
            key = keys.popleft()
            if key not in var_dict:
                if isinstance(var_dict, str):
                    var_dict = {var_dict: None}
                var_dict[key] = {}

            var_dict = var_dict.get(key)

    if not assign and not var_dict:
        return None

    return assign or var_dict

