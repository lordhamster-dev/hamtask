from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class Annotation(BaseModel):
    entry: str | None = None
    description: str


class Task(BaseModel):
    id: int | None = None
    uuid: str
    description: str
    status: str | None = None
    project: str | None = None
    priority: str | None = None
    due: str | None = None
    scheduled: str | None = None
    start: str | None = None
    urgency: float | None = None
    tags: list[str] = Field(default_factory=list)
    annotations: list[Annotation] = Field(default_factory=list)

    # Preserve fields we do not model yet, including UDAs.
    raw: dict[str, Any] = Field(default_factory=dict, exclude=True)

    @classmethod
    def from_export(cls, data: dict[str, Any]) -> Task:
        known = {
            "id",
            "uuid",
            "description",
            "status",
            "project",
            "priority",
            "due",
            "scheduled",
            "start",
            "urgency",
            "tags",
            "annotations",
        }
        task = cls.model_validate(data)
        task.raw = {key: value for key, value in data.items() if key not in known}
        return task
