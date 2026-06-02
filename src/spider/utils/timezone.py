from datetime import datetime

from django.utils.timezone import *

default_date_format = "%Y-%m-%d"
default_time_format = "%H:%M"
default_datetime_format = "{} {}".format(default_date_format, default_time_format)


def datetime_converter(o):
    if isinstance(o, datetime):
        return o.isoformat()
