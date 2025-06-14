from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
from dateutil import parser as date_parser
from .client import TickTickClient
from .models import Task, TaskPriority, TaskStatus
import re


class TaskManager:
    def __init__(self, client: TickTickClient):
        self.client = client

    async def create_task(self, title: str, project_id: Optional[str] = None, 
                         due: Optional[str] = None, priority: Optional[int] = None,
                         content: Optional[str] = None, subtasks: Optional[List[str]] = None,
                         reminder: Optional[str] = None, **kwargs) -> Task:
        
        # Get default project if not specified
        if not project_id:
            projects = await self.client.get_projects()
            inbox = next((p for p in projects if p.name.lower() == "inbox"), None)
            if inbox:
                project_id = inbox.id
            elif projects:
                project_id = projects[0].id
            else:
                raise ValueError("No projects found")
        
        # Parse due date
        due_date = None
        if due:
            due_date = self._parse_date(due)
        
        # Build task data
        task_data = {
            "project_id": project_id,
            "priority": priority or TaskPriority.NONE,
        }
        
        if content:
            task_data["content"] = content
        
        if due_date:
            task_data["due_date"] = due_date
        
        # Add subtasks
        if subtasks:
            task_data["items"] = [{"title": subtask} for subtask in subtasks]
        
        # Add reminder
        if reminder:
            task_data["reminders"] = [self._parse_reminder(reminder)]
        
        # Add any additional kwargs
        task_data.update(kwargs)
        
        return await self.client.create_task(title, **task_data)

    async def list_tasks(self, project_id: Optional[str] = None, 
                        due_filter: Optional[str] = None,
                        priority: Optional[int] = None,
                        status: Optional[str] = None) -> List[Task]:
        
        all_tasks = []
        
        if project_id:
            project_data = await self.client.get_project_data(project_id)
            all_tasks = project_data.tasks
        else:
            # Get tasks from all projects
            projects = await self.client.get_projects()
            for project in projects:
                if not project.closed:
                    project_data = await self.client.get_project_data(project.id)
                    all_tasks.extend(project_data.tasks)
        
        # Apply filters
        filtered_tasks = all_tasks
        
        # Filter by due date
        if due_filter:
            filtered_tasks = self._filter_by_due_date(filtered_tasks, due_filter)
        
        # Filter by priority
        if priority is not None:
            filtered_tasks = [t for t in filtered_tasks if t.priority == priority]
        
        # Filter by status
        if status:
            if status.lower() == "completed":
                filtered_tasks = [t for t in filtered_tasks if t.status == TaskStatus.COMPLETED]
            elif status.lower() == "open":
                filtered_tasks = [t for t in filtered_tasks if t.status == TaskStatus.NORMAL]
        
        return filtered_tasks

    async def update_task(self, task_id: str, project_id: str, **kwargs) -> Task:
        # Parse dates if provided
        if "due" in kwargs:
            kwargs["due_date"] = self._parse_date(kwargs.pop("due"))
        
        return await self.client.update_task(task_id, project_id, **kwargs)

    async def complete_task(self, task_id: str, project_id: str) -> None:
        await self.client.complete_task(project_id, task_id)

    async def delete_task(self, task_id: str, project_id: str) -> None:
        await self.client.delete_task(project_id, task_id)

    async def batch_complete(self, task_ids: List[tuple]) -> int:
        """Complete multiple tasks. task_ids should be list of (project_id, task_id) tuples"""
        completed = 0
        for project_id, task_id in task_ids:
            try:
                await self.complete_task(task_id, project_id)
                completed += 1
            except Exception as e:
                print(f"Failed to complete task {task_id}: {e}")
        return completed

    def _parse_date(self, date_str: str) -> datetime:
        """Parse natural language dates"""
        date_str = date_str.lower().strip()
        now = datetime.now()
        
        # Handle relative dates
        if date_str == "today":
            return now.replace(hour=23, minute=59, second=59)
        elif date_str == "tomorrow":
            return (now + timedelta(days=1)).replace(hour=23, minute=59, second=59)
        elif date_str == "yesterday":
            return (now - timedelta(days=1)).replace(hour=23, minute=59, second=59)
        elif date_str == "next week":
            return (now + timedelta(weeks=1)).replace(hour=23, minute=59, second=59)
        elif date_str == "next month":
            # Add approximately one month
            if now.month == 12:
                return now.replace(year=now.year + 1, month=1, hour=23, minute=59, second=59)
            else:
                return now.replace(month=now.month + 1, hour=23, minute=59, second=59)
        
        # Handle "in X days/weeks" pattern
        in_pattern = re.match(r"in (\d+) (day|days|week|weeks|month|months)", date_str)
        if in_pattern:
            amount = int(in_pattern.group(1))
            unit = in_pattern.group(2)
            if "day" in unit:
                return (now + timedelta(days=amount)).replace(hour=23, minute=59, second=59)
            elif "week" in unit:
                return (now + timedelta(weeks=amount)).replace(hour=23, minute=59, second=59)
            elif "month" in unit:
                # Approximate month handling
                return (now + timedelta(days=amount * 30)).replace(hour=23, minute=59, second=59)
        
        # Handle "next Monday", "next Friday", etc.
        weekday_pattern = re.match(r"next (monday|tuesday|wednesday|thursday|friday|saturday|sunday)", date_str)
        if weekday_pattern:
            target_weekday = {
                "monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
                "friday": 4, "saturday": 5, "sunday": 6
            }[weekday_pattern.group(1)]
            
            days_ahead = target_weekday - now.weekday()
            if days_ahead <= 0:  # Target day already happened this week
                days_ahead += 7
            
            return (now + timedelta(days=days_ahead)).replace(hour=23, minute=59, second=59)
        
        # Try to parse as standard date
        try:
            parsed = date_parser.parse(date_str)
            # If no time specified, set to end of day
            if parsed.hour == 0 and parsed.minute == 0:
                parsed = parsed.replace(hour=23, minute=59, second=59)
            return parsed
        except:
            raise ValueError(f"Could not parse date: {date_str}")

    def _parse_reminder(self, reminder_str: str) -> str:
        """Parse reminder string to TickTick format"""
        # Simple implementation - can be expanded
        if reminder_str == "9:00" or reminder_str == "9am":
            return "TRIGGER:P0DT9H0M0S"
        elif reminder_str == "0" or reminder_str == "now":
            return "TRIGGER:PT0S"
        else:
            # Default to 9am reminder
            return "TRIGGER:P0DT9H0M0S"

    def _filter_by_due_date(self, tasks: List[Task], due_filter: str) -> List[Task]:
        """Filter tasks by due date"""
        now = datetime.now()
        today = now.date()
        
        filtered = []
        for task in tasks:
            if not task.due_date:
                continue
            
            task_date = task.due_date.date()
            
            if due_filter == "today" and task_date == today:
                filtered.append(task)
            elif due_filter == "tomorrow" and task_date == today + timedelta(days=1):
                filtered.append(task)
            elif due_filter == "week" and task_date <= today + timedelta(days=7):
                filtered.append(task)
            elif due_filter == "overdue" and task_date < today:
                filtered.append(task)
        
        return filtered