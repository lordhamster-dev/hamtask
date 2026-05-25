from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from hamtask.app import HamtaskApp
from hamtask.config import load_config


def main(
    report: Annotated[
        str,
        typer.Argument(help="Taskwarrior report name to load from taskrc."),
    ] = "default",
    taskrc: Annotated[
        Path | None,
        typer.Option(help="Path to taskrc. Defaults to ~/.taskrc or ~/.config/task/taskrc."),
    ] = None,
) -> None:
    HamtaskApp(config=load_config(taskrc, report=report)).run()


if __name__ == "__main__":
    typer.run(main)
