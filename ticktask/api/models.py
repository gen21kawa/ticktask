from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from enum import IntEnum


class TaskStatus(IntEnum):
    NORMAL = 0
    COMPLETED = 2


class SubtaskStatus(IntEnum):
    NORMAL = 0
    COMPLETED = 1


class TaskPriority(IntEnum):
    NONE = 0
    LOW = 1
    MEDIUM = 3
    HIGH = 5


class ChecklistItem(BaseModel):
    id: Optional[str] = None
    title: str
    status: SubtaskStatus = SubtaskStatus.NORMAL
    completed_time: Optional[datetime] = Field(None, alias="completedTime")
    is_all_day: bool = Field(True, alias="isAllDay")
    sort_order: int = Field(0, alias="sortOrder")
    start_date: Optional[datetime] = Field(None, alias="startDate")
    time_zone: str = Field("UTC", alias="timeZone")

    class Config:
        populate_by_name = True
        use_enum_values = True


class Task(BaseModel):
    id: Optional[str] = None
    project_id: str = Field(alias="projectId")
    title: str
    content: Optional[str] = None
    desc: Optional[str] = None
    is_all_day: bool = Field(True, alias="isAllDay")
    start_date: Optional[datetime] = Field(None, alias="startDate")
    due_date: Optional[datetime] = Field(None, alias="dueDate")
    time_zone: str = Field("UTC", alias="timeZone")
    reminders: List[str] = Field(default_factory=list)
    repeat_flag: Optional[str] = Field(None, alias="repeatFlag")
    priority: TaskPriority = TaskPriority.NONE
    status: TaskStatus = TaskStatus.NORMAL
    completed_time: Optional[datetime] = Field(None, alias="completedTime")
    sort_order: int = Field(0, alias="sortOrder")
    items: List[ChecklistItem] = Field(default_factory=list)

    class Config:
        populate_by_name = True
        use_enum_values = True


class Project(BaseModel):
    id: Optional[str] = None
    name: str
    color: Optional[str] = None
    sort_order: int = Field(0, alias="sortOrder")
    closed: bool = False
    group_id: Optional[str] = Field(None, alias="groupId")
    view_mode: str = Field("list", alias="viewMode")
    permission: Optional[str] = None
    kind: str = "TASK"

    class Config:
        populate_by_name = True


class Column(BaseModel):
    id: Optional[str] = None
    project_id: str = Field(alias="projectId")
    name: str
    sort_order: int = Field(0, alias="sortOrder")

    class Config:
        populate_by_name = True


class ProjectData(BaseModel):
    project: Project
    tasks: List[Task]
    columns: List[Column]

    class Config:
        populate_by_name = True