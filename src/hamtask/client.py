from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass

from hamtask.models import Task
from hamtask.parsing import split_task_args


class TaskwarriorError(RuntimeError):
    pass


@dataclass(frozen=True)
class TaskwarriorClient:
    executable: str = "task"

    def run(self, args: list[str]) -> subprocess.CompletedProcess[str]:
        result = subprocess.run(
            [self.executable, *args],
            shell=False,
            check=False,
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            message = result.stderr.strip() or result.stdout.strip() or "Taskwarrior command failed"
            raise TaskwarriorError(message)
        return result

    def export(self, filter_args: list[str]) -> list[Task]:
        result = self.run(["rc.json.array=on", *filter_args, "export"])
        if not result.stdout.strip():
            return []
        data = json.loads(result.stdout)
        if not isinstance(data, list):
            raise TaskwarriorError("Expected Taskwarrior export to return a JSON array")
        return [Task.from_export(item) for item in data]

    def export_raw_filter(self, raw_filter: str) -> list[Task]:
        return self.export(split_task_args(raw_filter))

    def add(self, raw_args: str) -> None:
        self.run(["add", *split_task_args(raw_args)])

    def modify(self, task_uuid: str, raw_args: str) -> None:
        self.run([task_uuid, "modify", *split_task_args(raw_args)])

    def edit(self, task_uuid: str) -> None:
        result = subprocess.run(
            [self.executable, task_uuid, "edit"],
            shell=False,
            check=False,
            timeout=None,
        )
        if result.returncode != 0:
            raise TaskwarriorError("Taskwarrior edit failed")

    def done(self, task_uuid: str) -> None:
        self.run([task_uuid, "done"])

    def start(self, task_uuid: str) -> None:
        self.run([task_uuid, "start"])

    def stop(self, task_uuid: str) -> None:
        self.run([task_uuid, "stop"])

    def undo(self) -> None:
        self.run(["undo", "rc.confirmation=no"])

    def delete(self, task_uuid: str) -> None:
        self.run([task_uuid, "delete", "rc.confirmation=no"])

    def annotate(self, task_uuid: str, text: str) -> None:
        self.run([task_uuid, "annotate", text])
