from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import arrow

from hamtask.models import Task
from hamtask.parsing import parse_csv_setting


def parse_sort_setting(value: str | None) -> list[tuple[str, bool]]:
    """Parse Taskwarrior report sort syntax.

    Returns ``(field, reverse)`` pairs. Taskwarrior uses ``field+`` for ascending
    and ``field-`` for descending, for example ``due+,urgency-``.
    """
    result: list[tuple[str, bool]] = []
    for item in parse_csv_setting(value):
        if item.endswith("-"):
            result.append((item[:-1], True))
        elif item.endswith("+"):
            result.append((item[:-1], False))
        else:
            result.append((item, False))
    return result


def sort_tasks(tasks: list[Task], sort_setting: str | None) -> list[Task]:
    sort_fields = parse_sort_setting(sort_setting)
    if not sort_fields:
        return tasks

    sorted_tasks = list(tasks)
    for field, reverse in reversed(sort_fields):
        sorted_tasks.sort(key=lambda task: sort_value(task, field), reverse=reverse)
    return sorted_tasks


def sort_value(task: Task, field: str) -> tuple[int, Any]:
    value = getattr(task, field, task.raw.get(field, None))
    if value is None or value == "":
        return (1, "")
    if field in {"due", "scheduled", "wait", "entry", "modified", "end", "start"}:
        return (0, parse_task_date(str(value)))
    if isinstance(value, list):
        return (0, " ".join(str(item) for item in value))
    return (0, value)


def parse_task_date(value: str) -> datetime:
    try:
        parsed = arrow.get(value, "YYYYMMDDTHHmmss[Z]") if value.endswith("Z") else arrow.get(value)
    except (arrow.ParserError, ValueError):
        return datetime.max.replace(tzinfo=UTC)
    return parsed.datetime
