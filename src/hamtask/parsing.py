from __future__ import annotations

import shlex


def split_task_args(raw: str) -> list[str]:
    """Split raw Taskwarrior arguments using shell-like quoting rules."""
    return shlex.split(raw)


def parse_csv_setting(value: str | None) -> list[str]:
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]
