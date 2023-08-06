import re
from datetime import datetime
from typing import Union, List
from datetime import time as DTime

# ------------------------------------------------STR_TO----------------------------------------------------------------
from web_foundation.app.errors.application.application import InconsistencyError


def str_to_list(string: str) -> Union[List[str], None]:
    if not ",":
        return None
    return string.split(",")


def str_to_bool(string: str) -> Union[bool, None]:
    try:
        if string.lower() == "false":
            return False
        elif string.lower() == "true":
            return True
        else:
            return None
    except Exception as e:
        return None


# ------------------------------------------------VALIDATE--------------------------------------------------------------


def validate_date(date: str, check_gt_now=True) -> str:
    try:
        if "." in date:
            _date = datetime.strptime(date, "%d.%m.%Y")
            date = _date.isoformat()
        else:
            _date = datetime.fromisoformat(date)
    except ValueError as exception:
        raise InconsistencyError(exception)
    if check_gt_now and datetime.now() > _date:
        raise InconsistencyError(message="Incorrect date")
    return date


def validate_time(str_time: str) -> str:
    try:
        t = DTime.fromisoformat(str_time)
    except ValueError as exception:
        raise InconsistencyError(exception)
    return str_time


def validate_datetime(date_time: str, check_gt_now=False) -> str:  # TODO add timezones
    format_types = ["%d", "%m", "%Y", "%H", "%M", "%S"]
    try:
        if "." in date_time and date_time.count(".") > 1:
            date_nums = [ddd for ddd in re.findall(r"(\d*)", date_time) if ddd]
            _date = datetime.strptime(' '.join(date_nums), ' '.join(format_types[:len(date_nums)]))
        else:
            _date = datetime.fromisoformat(date_time)
        date = _date.astimezone().isoformat()
    except ValueError as exception:
        raise InconsistencyError(exception)
    if check_gt_now and datetime.now() > _date:
        raise InconsistencyError(message="Incorrect datetime")
    return date
