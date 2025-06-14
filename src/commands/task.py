import click
import asyncio
from typing import Optional, List
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
def task():
    """Manage tasks"""
    pass


@task.command()
@click.argument('title')
@click.option('--project', '-p', help='Project ID or name')
@click.option('--due', '-d', help='Due date (YYYY-MM-DD or natural language)')
@click.option('--priority', type=click.Choice(['0', '1', '3', '5']), default='0', help='Task priority')
@click.option('--content', '-c', help='Task description')
@click.option('--reminder', '-r', help='Reminder time')
@click.option('--subtask', '-s', multiple=True, help='Add subtask (can be used multiple times)')
@click.pass_context
def create(ctx, title: str, project: Optional[str], due: Optional[str], 
          priority: str, content: Optional[str], reminder: Optional[str], 
          subtask: List[str]):
    """Create a new task"""
    config = ctx.obj['config']
    progress = ProgressDisplay()
    formatter = TaskFormatter()
    
    async def create_task():
        async with get_client(config) as client:
            task_manager = TaskManager(client)
            project_manager = ProjectManager(client)
            
            # Resolve project
            project_id = project
            if project and not project.startswith('6'):  # Assuming IDs start with 6
                # Try to find project by name
                found_project = await project_manager.get_project_by_name(project)
                if found_project:
                    project_id = found_project.id
                else:
                    progress.show_error(f"Project '{project}' not found")
                    return
            
            # Create task
            task = await task_manager.create_task(
                title=title,
                project_id=project_id,
                due=due,
                priority=int(priority),
                content=content,
                subtasks=list(subtask) if subtask else None,
                reminder=reminder
            )
            
            progress.show_success(f"Created task: {task.title}")
            if task.id:
                click.echo(f"Task ID: {task.id}")
    
    try:
        asyncio.run(create_task())
    except Exception as e:
        progress.show_error(f"Failed to create task: {e}")


@task.command('list')
@click.option('--project', '-p', help='Filter by project')
@click.option('--due', help='Filter by due date (today, tomorrow, week, overdue)')
@click.option('--priority', type=click.Choice(['0', '1', '3', '5']), help='Filter by priority')
@click.option('--status', type=click.Choice(['open', 'completed']), help='Filter by status')
@click.option('--format', type=click.Choice(['table', 'json', 'markdown']), default='table', help='Output format')
@click.pass_context
def list_tasks(ctx, project: Optional[str], due: Optional[str], 
               priority: Optional[str], status: Optional[str], format: str):
    """List tasks"""
    config = ctx.obj['config']
    progress = ProgressDisplay()
    formatter = TaskFormatter()
    
    async def list_all_tasks():
        async with get_client(config) as client:
            task_manager = TaskManager(client)
            project_manager = ProjectManager(client)
            
            # Get all projects for display
            projects = await project_manager.list_projects()
            
            # Resolve project filter
            project_id = None
            if project:
                if project.startswith('6'):  # Assuming IDs start with 6
                    project_id = project
                else:
                    # Try to find project by name
                    found_project = await project_manager.get_project_by_name(project)
                    if found_project:
                        project_id = found_project.id
                    else:
                        progress.show_error(f"Project '{project}' not found")
                        return
            
            # Get tasks
            tasks = await task_manager.list_tasks(
                project_id=project_id,
                due_filter=due,
                priority=int(priority) if priority else None,
                status=status
            )
            
            # Format output
            if format == 'json':
                click.echo(formatter.format_tasks_json(tasks))
            elif format == 'markdown':
                click.echo(formatter.format_tasks_markdown(tasks, projects))
            else:
                formatter.format_tasks_table(tasks, projects)
            
            # Show summary
            if format == 'table':
                click.echo(f"\nTotal tasks: {len(tasks)}")
    
    try:
        asyncio.run(list_all_tasks())
    except Exception as e:
        progress.show_error(f"Failed to list tasks: {e}")


@task.command()
@click.argument('task_id')
@click.option('--project', '-p', required=True, help='Project ID')
@click.option('--title', help='New title')
@click.option('--due', '-d', help='New due date')
@click.option('--priority', type=click.Choice(['0', '1', '3', '5']), help='New priority')
@click.option('--content', '-c', help='New content')
@click.pass_context
def update(ctx, task_id: str, project: str, title: Optional[str], 
          due: Optional[str], priority: Optional[str], content: Optional[str]):
    """Update a task"""
    config = ctx.obj['config']
    progress = ProgressDisplay()
    
    async def update_task():
        async with get_client(config) as client:
            task_manager = TaskManager(client)
            
            # Build update data
            update_data = {}
            if title:
                update_data['title'] = title
            if due:
                update_data['due'] = due
            if priority:
                update_data['priority'] = int(priority)
            if content:
                update_data['content'] = content
            
            # Update task
            task = await task_manager.update_task(task_id, project, **update_data)
            progress.show_success(f"Updated task: {task.title}")
    
    try:
        asyncio.run(update_task())
    except Exception as e:
        progress.show_error(f"Failed to update task: {e}")


@task.command()
@click.argument('task_id')
@click.option('--project', '-p', required=True, help='Project ID')
@click.pass_context
def complete(ctx, task_id: str, project: str):
    """Complete a task"""
    config = ctx.obj['config']
    progress = ProgressDisplay()
    
    async def complete_task():
        async with get_client(config) as client:
            task_manager = TaskManager(client)
            await task_manager.complete_task(task_id, project)
            progress.show_success("Task completed!")
    
    try:
        asyncio.run(complete_task())
    except Exception as e:
        progress.show_error(f"Failed to complete task: {e}")


@task.command()
@click.argument('task_id')
@click.option('--project', '-p', required=True, help='Project ID')
@click.pass_context
def delete(ctx, task_id: str, project: str):
    """Delete a task"""
    config = ctx.obj['config']
    progress = ProgressDisplay()
    
    if not click.confirm("Are you sure you want to delete this task?"):
        return
    
    async def delete_task():
        async with get_client(config) as client:
            task_manager = TaskManager(client)
            await task_manager.delete_task(task_id, project)
            progress.show_success("Task deleted!")
    
    try:
        asyncio.run(delete_task())
    except Exception as e:
        progress.show_error(f"Failed to delete task: {e}")