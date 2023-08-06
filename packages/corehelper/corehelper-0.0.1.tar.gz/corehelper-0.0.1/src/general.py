from datetime import datetime
from zoneinfo import ZoneInfo
import uuid


def numbers_to_sql_in(ids):
    if len(ids) == 1:
        return f"({ids[0]})"
    return tuple(ids)


def strings_to_sql_in(strings):
    if len(strings) > 1:
        return "(" + ",".join(["'" + str(string) + "'" for string in strings]) + ")"
    return f"('{strings[0]}')"


def pluck(key, lst):
    return [x.get(key) for x in lst]


def unique(lst):
    unique_items = []
    for item in lst:
        if item not in unique_items:
            unique_items.append(item)
    return unique_items


def fix_timezone(date, timezone="America/Santiago"):
    return date.astimezone(ZoneInfo(timezone))


def now():
    return fix_timezone(datetime.now())


def print_log(message, level, log_level=3):
    if level <= int(log_level) != 0:
        print(message)


def generate_uuid(keyword):
    return uuid.uuid3(uuid.NAMESPACE_DNS, keyword)


def calculate_average(lst):
    total = 0
    count = 0
    for item in lst:
        total += total + item
        count += 1

    if total == 0 or count == 0:
        return 0

    return total / count


def calculate_percentage(value, total, decimals=2):
    if value is None or value == 0:
        return 0

    if total is None or total == 0:
        return 0

    return round((value * 100 / total), decimals)


def optional(value):
    return value is not None and value or 0

