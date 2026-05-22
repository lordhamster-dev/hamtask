from __future__ import annotations

import shlex

import arrow


def split_task_args(raw: str) -> list[str]:
    """Split raw Taskwarrior arguments using shell-like quoting rules."""
    return shlex.split(raw)


def parse_csv_setting(value: str | None) -> list[str]:
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


def format_task_datetime(value: str) -> str:
    try:
        parsed = arrow.get(value, "YYYYMMDDTHHmmss[Z]") if value.endswith("Z") else arrow.get(value)
    except (arrow.ParserError, ValueError):
        return value
    return parsed.format("YYYY-MM-DD HH:mm:ss")
