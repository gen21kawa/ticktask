from rich.console import Console
from rich.table import Table
from rich.tree import Tree
from rich.text import Text
from typing import List, Optional
from datetime import datetime
import json
from ..api.models import Task, Project, TaskPriority, TaskStatus


class TaskFormatter:
    def __init__(self):
        self.console = Console()

    def format_tasks_table(self, tasks: List[Task], projects: Optional[List[Project]] = None) -> None:
        """Display tasks in a table format"""
        table = Table(title="Tasks", show_header=True, header_style="bold magenta")
        table.add_column("ID", style="cyan", width=12)
        table.add_column("Title", style="white")
        table.add_column("Project", style="yellow")
        table.add_column("Due", style="red")
        table.add_column("Priority", style="magenta")
        table.add_column("Status", style="green")

        # Create project lookup
        project_lookup = {}
        if projects:
            project_lookup = {p.id: p.name for p in projects}

        for task in tasks:
            # Format due date
            due_str = ""
            if task.due_date:
                due_date = task.due_date
                today = datetime.now().date()
                task_date = due_date.date()
                
                if task_date < today:
                    due_str = f"[red]{due_date.strftime('%Y-%m-%d')} (overdue)[/red]"
                elif task_date == today:
                    due_str = f"[yellow]Today[/yellow]"
                elif (task_date - today).days == 1:
                    due_str = f"[cyan]Tomorrow[/cyan]"
                else:
                    due_str = due_date.strftime('%Y-%m-%d')

            # Format priority
            priority_map = {
                TaskPriority.NONE: "",
                TaskPriority.LOW: "[blue]Low[/blue]",
                TaskPriority.MEDIUM: "[yellow]Medium[/yellow]",
                TaskPriority.HIGH: "[red]High[/red]"
            }
            priority_str = priority_map.get(TaskPriority(task.priority), "")

            # Format status
            status_str = "[green]✓[/green]" if task.status == TaskStatus.COMPLETED else "○"

            # Get project name
            project_name = project_lookup.get(task.project_id, task.project_id[:8] + "...")

            table.add_row(
                task.id[:12] if task.id else "",
                task.title,
                project_name,
                due_str,
                priority_str,
                status_str
            )

        self.console.print(table)

    def format_tasks_json(self, tasks: List[Task]) -> str:
        """Format tasks as JSON"""
        tasks_data = []
        for task in tasks:
            task_dict = task.model_dump(by_alias=True, exclude_none=True)
            # Convert datetime objects to strings
            if task.due_date:
                task_dict["dueDate"] = task.due_date.isoformat()
            if task.start_date:
                task_dict["startDate"] = task.start_date.isoformat()
            if task.completed_time:
                task_dict["completedTime"] = task.completed_time.isoformat()
            tasks_data.append(task_dict)
        
        return json.dumps(tasks_data, indent=2)

    def format_tasks_markdown(self, tasks: List[Task], projects: Optional[List[Project]] = None) -> str:
        """Format tasks as Markdown"""
        # Create project lookup
        project_lookup = {}
        if projects:
            project_lookup = {p.id: p.name for p in projects}

        md_lines = ["# Tasks\n"]
        
        # Group tasks by project
        tasks_by_project = {}
        for task in tasks:
            project_name = project_lookup.get(task.project_id, "Unknown Project")
            if project_name not in tasks_by_project:
                tasks_by_project[project_name] = []
            tasks_by_project[project_name].append(task)

        for project_name, project_tasks in tasks_by_project.items():
            md_lines.append(f"\n## {project_name}\n")
            
            for task in project_tasks:
                # Task checkbox
                check = "[x]" if task.status == TaskStatus.COMPLETED else "[ ]"
                
                # Priority indicator
                priority_indicators = {
                    TaskPriority.HIGH: " 🔴",
                    TaskPriority.MEDIUM: " 🟡",
                    TaskPriority.LOW: " 🔵"
                }
                priority = priority_indicators.get(TaskPriority(task.priority), "")
                
                # Due date
                due = ""
                if task.due_date:
                    due = f" (Due: {task.due_date.strftime('%Y-%m-%d')})"
                
                md_lines.append(f"- {check} {task.title}{priority}{due}")
                
                # Add content if exists
                if task.content:
                    md_lines.append(f"  - {task.content}")
                
                # Add subtasks
                if task.items:
                    for item in task.items:
                        item_check = "[x]" if item.status == 1 else "[ ]"
                        md_lines.append(f"  - {item_check} {item.title}")

        return "\n".join(md_lines)

    def format_projects_table(self, projects: List[Project]) -> None:
        """Display projects in a table format"""
        table = Table(title="Projects", show_header=True, header_style="bold magenta")
        table.add_column("ID", style="cyan", width=12)
        table.add_column("Name", style="white")
        table.add_column("Color", style="yellow")
        table.add_column("View Mode", style="blue")
        table.add_column("Kind", style="green")
        table.add_column("Status", style="red")

        for project in projects:
            status = "[red]Closed[/red]" if project.closed else "[green]Active[/green]"
            
            # Show color as colored block if possible
            color_display = project.color or "None"
            if project.color and project.color.startswith("#"):
                color_display = f"[{project.color}]███[/{project.color}] {project.color}"
            
            table.add_row(
                project.id[:12] if project.id else "",
                project.name,
                color_display,
                project.view_mode,
                project.kind,
                status
            )

        self.console.print(table)

    def format_task_detail(self, task: Task, project_name: Optional[str] = None) -> None:
        """Display detailed task information"""
        self.console.print(f"\n[bold cyan]Task Details[/bold cyan]")
        self.console.print(f"[bold]ID:[/bold] {task.id}")
        self.console.print(f"[bold]Title:[/bold] {task.title}")
        
        if project_name:
            self.console.print(f"[bold]Project:[/bold] {project_name}")
        
        if task.content:
            self.console.print(f"[bold]Content:[/bold] {task.content}")
        
        if task.desc:
            self.console.print(f"[bold]Description:[/bold] {task.desc}")
        
        # Priority
        priority_map = {
            TaskPriority.NONE: "None",
            TaskPriority.LOW: "[blue]Low[/blue]",
            TaskPriority.MEDIUM: "[yellow]Medium[/yellow]",
            TaskPriority.HIGH: "[red]High[/red]"
        }
        self.console.print(f"[bold]Priority:[/bold] {priority_map.get(TaskPriority(task.priority), 'None')}")
        
        # Dates
        if task.start_date:
            self.console.print(f"[bold]Start Date:[/bold] {task.start_date.strftime('%Y-%m-%d %H:%M')}")
        
        if task.due_date:
            self.console.print(f"[bold]Due Date:[/bold] {task.due_date.strftime('%Y-%m-%d %H:%M')}")
        
        # Status
        status = "[green]Completed[/green]" if task.status == TaskStatus.COMPLETED else "[yellow]Pending[/yellow]"
        self.console.print(f"[bold]Status:[/bold] {status}")
        
        if task.completed_time:
            self.console.print(f"[bold]Completed:[/bold] {task.completed_time.strftime('%Y-%m-%d %H:%M')}")
        
        # Reminders
        if task.reminders:
            self.console.print(f"[bold]Reminders:[/bold] {', '.join(task.reminders)}")
        
        # Subtasks
        if task.items:
            self.console.print("\n[bold]Subtasks:[/bold]")
            for item in task.items:
                check = "[green]✓[/green]" if item.status == 1 else "○"
                self.console.print(f"  {check} {item.title}")


class ProgressDisplay:
    def __init__(self):
        self.console = Console()

    def show_progress(self, message: str) -> None:
        """Show a progress message"""
        self.console.print(f"[yellow]⏳[/yellow] {message}...")

    def show_success(self, message: str) -> None:
        """Show a success message"""
        self.console.print(f"[green]✓[/green] {message}")

    def show_error(self, message: str) -> None:
        """Show an error message"""
        self.console.print(f"[red]✗[/red] {message}")

    def show_info(self, message: str) -> None:
        """Show an info message"""
        self.console.print(f"[blue]ℹ[/blue] {message}")