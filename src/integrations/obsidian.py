import click
import asyncio
from pathlib import Path
from datetime import datetime
from typing import List, Optional
import aiofiles
from ..api.client import TickTickClient
from ..api.auth import OAuth2Handler
from ..api.tasks import TaskManager
from ..api.projects import ProjectManager
from ..api.models import Task, Project, TaskStatus, TaskPriority
from ..utils.config import Config
from ..utils.formatting import ProgressDisplay


class ObsidianIntegration:
    def __init__(self, config: Config):
        self.config = config
        self.vault_path = config.obsidian_vault_path
        self.daily_notes_path = config.obsidian_daily_notes_path

    async def export_daily_log(self, tasks: List[Task], projects: List[Project]) -> Path:
        """Export tasks to Obsidian daily note"""
        # Create project lookup
        project_lookup = {p.id: p.name for p in projects}
        
        # Group tasks by status
        completed_tasks = [t for t in tasks if t.status == TaskStatus.COMPLETED]
        pending_tasks = [t for t in tasks if t.status == TaskStatus.NORMAL]
        
        # Group pending tasks by due date
        overdue_tasks = []
        today_tasks = []
        future_tasks = []
        
        today = datetime.now().date()
        for task in pending_tasks:
            if task.due_date:
                if task.due_date.date() < today:
                    overdue_tasks.append(task)
                elif task.due_date.date() == today:
                    today_tasks.append(task)
                else:
                    future_tasks.append(task)
        
        # Generate markdown content
        content = self._generate_daily_log_content(
            completed_tasks, overdue_tasks, today_tasks, future_tasks, project_lookup
        )
        
        # Determine file path
        date_str = datetime.now().strftime(self.config.date_format)
        daily_note_dir = self.vault_path / self.daily_notes_path
        daily_note_dir.mkdir(parents=True, exist_ok=True)
        file_path = daily_note_dir / f"{date_str}.md"
        
        # Check if file exists and append or create
        if file_path.exists():
            async with aiofiles.open(file_path, 'r') as f:
                existing_content = await f.read()
            
            # Append task log section
            if "## TickTick Task Log" not in existing_content:
                content = f"\n\n{content}"
                async with aiofiles.open(file_path, 'a') as f:
                    await f.write(content)
            else:
                # Replace existing task log section
                import re
                pattern = r'## TickTick Task Log.*?(?=\n## |\Z)'
                new_content = re.sub(pattern, content, existing_content, flags=re.DOTALL)
                async with aiofiles.open(file_path, 'w') as f:
                    await f.write(new_content)
        else:
            # Create new file
            full_content = f"# Daily Note - {date_str}\n\n{content}"
            async with aiofiles.open(file_path, 'w') as f:
                await f.write(full_content)
        
        return file_path

    def _generate_daily_log_content(self, completed: List[Task], overdue: List[Task], 
                                   today: List[Task], future: List[Task], 
                                   project_lookup: dict) -> str:
        """Generate markdown content for daily log"""
        lines = ["## TickTick Task Log"]
        lines.append(f"\n*Generated at: {datetime.now().strftime(self.config.time_format)}*\n")
        
        # Completed tasks
        if completed:
            lines.append("### ✅ Completed Tasks")
            for task in completed:
                project_name = project_lookup.get(task.project_id, "Unknown")
                priority = self._get_priority_emoji(task.priority)
                lines.append(f"- [x] {task.title} ({project_name}){priority}")
                if task.content:
                    lines.append(f"  - {task.content}")
        
        # Overdue tasks
        if overdue:
            lines.append("\n### ⚠️ Overdue Tasks")
            for task in overdue:
                project_name = project_lookup.get(task.project_id, "Unknown")
                priority = self._get_priority_emoji(task.priority)
                due = task.due_date.strftime(self.config.date_format) if task.due_date else ""
                lines.append(f"- [ ] {task.title} ({project_name}) 📅 {due}{priority}")
                if task.content:
                    lines.append(f"  - {task.content}")
        
        # Today's tasks
        if today:
            lines.append("\n### 📅 Today's Tasks")
            for task in today:
                project_name = project_lookup.get(task.project_id, "Unknown")
                priority = self._get_priority_emoji(task.priority)
                lines.append(f"- [ ] {task.title} ({project_name}){priority}")
                if task.content:
                    lines.append(f"  - {task.content}")
                if task.items:
                    for item in task.items:
                        check = "[x]" if item.status == 1 else "[ ]"
                        lines.append(f"  - {check} {item.title}")
        
        # Future tasks
        if future:
            lines.append("\n### 📆 Upcoming Tasks")
            for task in future[:5]:  # Limit to 5 upcoming tasks
                project_name = project_lookup.get(task.project_id, "Unknown")
                priority = self._get_priority_emoji(task.priority)
                due = task.due_date.strftime(self.config.date_format) if task.due_date else ""
                lines.append(f"- [ ] {task.title} ({project_name}) 📅 {due}{priority}")
        
        # Summary
        lines.append("\n### 📊 Summary")
        lines.append(f"- Total completed: {len(completed)}")
        lines.append(f"- Overdue: {len(overdue)}")
        lines.append(f"- Due today: {len(today)}")
        lines.append(f"- Upcoming: {len(future)}")
        
        return "\n".join(lines)

    def _get_priority_emoji(self, priority: int) -> str:
        """Get emoji for task priority"""
        priority_map = {
            TaskPriority.HIGH: " 🔴",
            TaskPriority.MEDIUM: " 🟡",
            TaskPriority.LOW: " 🔵"
        }
        return priority_map.get(TaskPriority(priority), "")

    async def sync_tasks(self, direction: str = "to-obsidian") -> None:
        """Sync tasks between TickTick and Obsidian"""
        # This is a placeholder for future bidirectional sync
        raise NotImplementedError("Task sync not yet implemented")


def get_client(config: Config) -> TickTickClient:
    """Create a TickTick client with authentication"""
    auth_handler = OAuth2Handler(
        client_id=config.client_id,
        client_secret=config.client_secret,
        redirect_uri=config.redirect_uri
    )
    return TickTickClient(auth_handler=auth_handler)


@click.group()
def obsidian():
    """Obsidian integration commands"""
    pass


@obsidian.command('daily-log')
@click.option('--date', help='Date to export (default: today)')
@click.pass_context
def daily_log(ctx, date: Optional[str]):
    """Export task log to Obsidian daily note"""
    config = ctx.obj['config']
    progress = ProgressDisplay()
    
    async def export_log():
        async with get_client(config) as client:
            task_manager = TaskManager(client)
            project_manager = ProjectManager(client)
            
            # Get all projects
            projects = await project_manager.list_projects()
            
            # Get tasks
            progress.show_progress("Fetching tasks")
            all_tasks = []
            
            # Get overdue tasks
            overdue_tasks = await task_manager.list_tasks(due_filter="overdue")
            all_tasks.extend(overdue_tasks)
            
            # Get today's tasks
            today_tasks = await task_manager.list_tasks(due_filter="today")
            all_tasks.extend(today_tasks)
            
            # Get this week's tasks
            week_tasks = await task_manager.list_tasks(due_filter="week")
            all_tasks.extend(week_tasks)
            
            # Get completed tasks (from today)
            completed_tasks = await task_manager.list_tasks(status="completed")
            # Filter to today's completed tasks
            today = datetime.now().date()
            completed_today = [t for t in completed_tasks if t.completed_time and t.completed_time.date() == today]
            all_tasks.extend(completed_today)
            
            # Remove duplicates
            seen_ids = set()
            unique_tasks = []
            for task in all_tasks:
                if task.id not in seen_ids:
                    seen_ids.add(task.id)
                    unique_tasks.append(task)
            
            # Export to Obsidian
            obsidian_int = ObsidianIntegration(config)
            file_path = await obsidian_int.export_daily_log(unique_tasks, projects)
            
            progress.show_success(f"Exported to: {file_path}")
            
            # Open in default editor if available
            import platform
            if platform.system() == "Darwin":  # macOS
                import subprocess
                subprocess.run(["open", str(file_path)])
            elif platform.system() == "Windows":
                import os
                os.startfile(str(file_path))
    
    try:
        asyncio.run(export_log())
    except Exception as e:
        progress.show_error(f"Failed to export daily log: {e}")


@obsidian.command('sync')
@click.option('--direction', type=click.Choice(['to-obsidian', 'from-obsidian', 'bidirectional']), 
              default='to-obsidian', help='Sync direction')
@click.option('--vault', help='Path to Obsidian vault (overrides config)')
@click.pass_context
def sync(ctx, direction: str, vault: Optional[str]):
    """Sync tasks between TickTick and Obsidian"""
    config = ctx.obj['config']
    progress = ProgressDisplay()
    
    if vault:
        config.set("obsidian.vault_path", vault)
    
    progress.show_error("Sync functionality not yet implemented")
    click.echo("\nThis feature will allow:")
    click.echo("- Syncing TickTick tasks to Obsidian task format")
    click.echo("- Creating TickTick tasks from Obsidian notes")
    click.echo("- Bidirectional sync with conflict resolution")