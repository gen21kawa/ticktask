import pytest
from datetime import datetime
from src.api.models import Task, Project, ChecklistItem, TaskStatus, TaskPriority


def test_task_creation():
    """Test creating a Task model"""
    task = Task(
        id="test123",
        project_id="project123",
        title="Test Task",
        content="Test content",
        priority=TaskPriority.HIGH,
        status=TaskStatus.NORMAL
    )
    
    assert task.id == "test123"
    assert task.project_id == "project123"
    assert task.title == "Test Task"
    assert task.content == "Test content"
    assert task.priority == TaskPriority.HIGH
    assert task.status == TaskStatus.NORMAL


def test_task_with_subtasks():
    """Test creating a Task with subtasks"""
    subtask = ChecklistItem(
        id="sub1",
        title="Subtask 1",
        status=0
    )
    
    task = Task(
        id="test123",
        project_id="project123",
        title="Test Task",
        items=[subtask]
    )
    
    assert len(task.items) == 1
    assert task.items[0].title == "Subtask 1"
    assert task.items[0].status == 0


def test_project_creation():
    """Test creating a Project model"""
    project = Project(
        id="project123",
        name="Test Project",
        color="#FF0000",
        view_mode="list",
        kind="TASK"
    )
    
    assert project.id == "project123"
    assert project.name == "Test Project"
    assert project.color == "#FF0000"
    assert project.view_mode == "list"
    assert project.kind == "TASK"


def test_task_serialization():
    """Test Task model serialization with aliases"""
    task = Task(
        project_id="project123",
        title="Test Task",
        is_all_day=False,
        due_date=datetime(2024, 3, 15, 10, 0, 0)
    )
    
    # Test serialization with aliases
    data = task.model_dump(by_alias=True, exclude_none=True)
    
    assert "projectId" in data
    assert data["projectId"] == "project123"
    assert "isAllDay" in data
    assert data["isAllDay"] is False
    assert "dueDate" in data