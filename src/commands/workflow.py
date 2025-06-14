import click
import asyncio
from datetime import datetime, timedelta
from typing import List
from ..api.client import TickTickClient
from ..api.auth import OAuth2Handler
from ..api.tasks import TaskManager
from ..api.projects import ProjectManager
from ..utils.formatting import TaskFormatter, ProgressDisplay
from ..utils.config import Config


def get_client(config: Config) -> TickTickClient:
    """Create a TickTick client with authentication"""
    auth_handler = OAuth2Handler(
        client_id=config.client_id,
        client_secret=config.client_secret,
        redirect_uri=config.redirect_uri
    )
    return TickTickClient(auth_handler=auth_handler)


@click.group()
def workflow():
    """Workflow automation commands"""
    pass


@workflow.command('daily-plan')
@click.option('--export-obsidian', is_flag=True, help='Export to Obsidian')
@click.pass_context
def daily_plan(ctx, export_obsidian: bool):
    """Generate daily plan with today's and overdue tasks"""
    config = ctx.obj['config']
    progress = ProgressDisplay()
    formatter = TaskFormatter()
    
    async def generate_plan():
        async with get_client(config) as client:
            task_manager = TaskManager(client)
            project_manager = ProjectManager(client)
            
            # Get workflow config
            include_overdue = config.get("workflows.daily_plan.include_overdue", True)
            include_today = config.get("workflows.daily_plan.include_today", True)
            include_tomorrow = config.get("workflows.daily_plan.include_tomorrow", False)
            
            # Get all projects for display
            projects = await project_manager.list_projects()
            
            all_tasks = []
            
            # Get overdue tasks
            if include_overdue:
                progress.show_progress("Fetching overdue tasks")
                overdue_tasks = await task_manager.list_tasks(due_filter="overdue")
                all_tasks.extend(overdue_tasks)
            
            # Get today's tasks
            if include_today:
                progress.show_progress("Fetching today's tasks")
                today_tasks = await task_manager.list_tasks(due_filter="today")
                all_tasks.extend(today_tasks)
            
            # Get tomorrow's tasks
            if include_tomorrow:
                progress.show_progress("Fetching tomorrow's tasks")
                tomorrow_tasks = await task_manager.list_tasks(due_filter="tomorrow")
                all_tasks.extend(tomorrow_tasks)
            
            # Remove duplicates
            seen_ids = set()
            unique_tasks = []
            for task in all_tasks:
                if task.id not in seen_ids:
                    seen_ids.add(task.id)
                    unique_tasks.append(task)
            
            # Sort by priority and due date
            unique_tasks.sort(key=lambda t: (
                -(t.priority or 0),  # Higher priority first
                t.due_date or datetime.max  # Earlier dates first
            ))
            
            # Display plan
            click.echo("\n=== Daily Plan ===")
            click.echo(f"Date: {datetime.now().strftime('%Y-%m-%d')}")
            click.echo()
            
            if include_overdue:
                overdue = [t for t in unique_tasks if t.due_date and t.due_date.date() < datetime.now().date()]
                if overdue:
                    click.echo(f"[red]Overdue Tasks ({len(overdue)}):[/red]")
                    formatter.format_tasks_table(overdue, projects)
                    click.echo()
            
            if include_today:
                today = [t for t in unique_tasks if t.due_date and t.due_date.date() == datetime.now().date()]
                if today:
                    click.echo(f"[yellow]Today's Tasks ({len(today)}):[/yellow]")
                    formatter.format_tasks_table(today, projects)
                    click.echo()
            
            if include_tomorrow:
                tomorrow = [t for t in unique_tasks if t.due_date and t.due_date.date() == (datetime.now() + timedelta(days=1)).date()]
                if tomorrow:
                    click.echo(f"[cyan]Tomorrow's Tasks ({len(tomorrow)}):[/cyan]")
                    formatter.format_tasks_table(tomorrow, projects)
                    click.echo()
            
            # Export to Obsidian if requested
            if export_obsidian:
                from ..integrations.obsidian import ObsidianIntegration
                obsidian_int = ObsidianIntegration(config)
                file_path = await obsidian_int.export_daily_log(unique_tasks, projects)
                progress.show_success(f"Exported to Obsidian: {file_path}")
            
            # Show summary
            click.echo(f"\nTotal tasks in plan: {len(unique_tasks)}")
            
            # Ask for prioritization
            if click.confirm("\nWould you like to prioritize tasks?"):
                await prioritize_tasks(unique_tasks, task_manager, projects, formatter)
    
    try:
        asyncio.run(generate_plan())
    except Exception as e:
        progress.show_error(f"Failed to generate daily plan: {e}")


async def prioritize_tasks(tasks: List, task_manager: TaskManager, projects: List, formatter: TaskFormatter):
    """Interactive task prioritization"""
    click.echo("\nPrioritizing tasks...")
    
    for i, task in enumerate(tasks[:5]):  # Limit to top 5 for prioritization
        project_name = next((p.name for p in projects if p.id == task.project_id), "Unknown")
        click.echo(f"\n[{i+1}] {task.title} ({project_name})")
        
        if task.content:
            click.echo(f"    {task.content}")
        
        new_priority = click.prompt(
            "Priority (0=None, 1=Low, 3=Medium, 5=High, Enter to skip)",
            type=click.Choice(['0', '1', '3', '5', '']),
            default='',
            show_default=False
        )
        
        if new_priority:
            await task_manager.update_task(
                task.id,
                task.project_id,
                priority=int(new_priority)
            )
            click.echo(f"    ✓ Updated priority")


@workflow.command('apply-template')
@click.argument('template_name')
@click.pass_context
def apply_template(ctx, template_name: str):
    """Apply a task template"""
    config = ctx.obj['config']
    progress = ProgressDisplay()
    
    # This is a placeholder - templates would be defined in config
    click.echo(f"Applying template: {template_name}")
    progress.show_error("Template functionality not yet implemented")


@workflow.command('batch-complete')
@click.option('--project', '-p', help='Filter by project')
@click.option('--pattern', help='Title pattern to match')
@click.pass_context
def batch_complete(ctx, project: str, pattern: str):
    """Complete multiple tasks matching criteria"""
    config = ctx.obj['config']
    progress = ProgressDisplay()
    
    async def complete_batch():
        async with get_client(config) as client:
            task_manager = TaskManager(client)
            project_manager = ProjectManager(client)
            
            # Resolve project
            project_id = None
            if project:
                if project.startswith('6'):
                    project_id = project
                else:
                    found_project = await project_manager.get_project_by_name(project)
                    if found_project:
                        project_id = found_project.id
            
            # Get tasks
            tasks = await task_manager.list_tasks(project_id=project_id, status="open")
            
            # Filter by pattern if provided
            if pattern:
                pattern_lower = pattern.lower()
                tasks = [t for t in tasks if pattern_lower in t.title.lower()]
            
            if not tasks:
                progress.show_info("No matching tasks found")
                return
            
            # Show tasks to be completed
            click.echo(f"\nFound {len(tasks)} tasks to complete:")
            for task in tasks[:10]:  # Show first 10
                click.echo(f"  - {task.title}")
            if len(tasks) > 10:
                click.echo(f"  ... and {len(tasks) - 10} more")
            
            if not click.confirm("\nComplete all these tasks?"):
                return
            
            # Complete tasks
            task_ids = [(t.project_id, t.id) for t in tasks]
            completed = await task_manager.batch_complete(task_ids)
            
            progress.show_success(f"Completed {completed}/{len(tasks)} tasks")
    
    try:
        asyncio.run(complete_batch())
    except Exception as e:
        progress.show_error(f"Failed to complete tasks: {e}")