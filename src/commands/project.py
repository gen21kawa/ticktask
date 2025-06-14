import click
import asyncio
from typing import Optional
from ..api.client import TickTickClient
from ..api.auth import OAuth2Handler
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
def project():
    """Manage projects"""
    pass


@project.command('list')
@click.pass_context
def list_projects(ctx):
    """List all projects"""
    config = ctx.obj['config']
    progress = ProgressDisplay()
    formatter = TaskFormatter()
    
    async def list_all():
        async with get_client(config) as client:
            project_manager = ProjectManager(client)
            projects = await project_manager.list_projects()
            formatter.format_projects_table(projects)
            click.echo(f"\nTotal projects: {len(projects)}")
    
    try:
        asyncio.run(list_all())
    except Exception as e:
        progress.show_error(f"Failed to list projects: {e}")


@project.command()
@click.argument('name')
@click.option('--color', help='Hex color code (e.g., #FF0000)')
@click.option('--kind', type=click.Choice(['TASK', 'NOTE']), default='TASK', help='Project kind')
@click.pass_context
def create(ctx, name: str, color: Optional[str], kind: str):
    """Create a new project"""
    config = ctx.obj['config']
    progress = ProgressDisplay()
    
    async def create_project():
        async with get_client(config) as client:
            project_manager = ProjectManager(client)
            project = await project_manager.create_project(name, color=color, kind=kind)
            progress.show_success(f"Created project: {project.name}")
            click.echo(f"Project ID: {project.id}")
    
    try:
        asyncio.run(create_project())
    except Exception as e:
        progress.show_error(f"Failed to create project: {e}")


@project.command()
@click.argument('project_id')
@click.pass_context
def show(ctx, project_id: str):
    """Show project details with tasks"""
    config = ctx.obj['config']
    progress = ProgressDisplay()
    formatter = TaskFormatter()
    
    async def show_project():
        async with get_client(config) as client:
            project_manager = ProjectManager(client)
            
            # Try to find by name first
            if not project_id.startswith('6'):  # Assuming IDs start with 6
                project = await project_manager.get_project_by_name(project_id)
                if project:
                    project_id = project.id
                else:
                    progress.show_error(f"Project '{project_id}' not found")
                    return
            
            # Get project data
            project_data = await project_manager.get_project_data(project_id)
            
            # Display project info
            click.echo(f"\n[bold cyan]Project: {project_data.project.name}[/bold cyan]")
            click.echo(f"ID: {project_data.project.id}")
            click.echo(f"Color: {project_data.project.color or 'None'}")
            click.echo(f"View Mode: {project_data.project.view_mode}")
            click.echo(f"Kind: {project_data.project.kind}")
            
            # Display tasks
            if project_data.tasks:
                click.echo(f"\nTasks ({len(project_data.tasks)}):")
                formatter.format_tasks_table(project_data.tasks)
            else:
                click.echo("\nNo tasks in this project")
            
            # Display columns if kanban view
            if project_data.project.view_mode == "kanban" and project_data.columns:
                click.echo(f"\nKanban Columns ({len(project_data.columns)}):")
                for col in project_data.columns:
                    click.echo(f"  - {col.name}")
    
    try:
        asyncio.run(show_project())
    except Exception as e:
        progress.show_error(f"Failed to show project: {e}")


@project.command()
@click.argument('project_id')
@click.option('--name', help='New project name')
@click.option('--color', help='New color (hex code)')
@click.option('--view-mode', type=click.Choice(['list', 'kanban', 'timeline']), help='View mode')
@click.pass_context
def update(ctx, project_id: str, name: Optional[str], color: Optional[str], view_mode: Optional[str]):
    """Update a project"""
    config = ctx.obj['config']
    progress = ProgressDisplay()
    
    async def update_project():
        async with get_client(config) as client:
            project_manager = ProjectManager(client)
            
            # Build update data
            update_data = {}
            if name:
                update_data['name'] = name
            if color:
                update_data['color'] = color
            if view_mode:
                update_data['view_mode'] = view_mode
            
            # Update project
            project = await project_manager.update_project(project_id, **update_data)
            progress.show_success(f"Updated project: {project.name}")
    
    try:
        asyncio.run(update_project())
    except Exception as e:
        progress.show_error(f"Failed to update project: {e}")


@project.command()
@click.argument('project_id')
@click.pass_context
def delete(ctx, project_id: str):
    """Delete a project"""
    config = ctx.obj['config']
    progress = ProgressDisplay()
    
    if not click.confirm("Are you sure you want to delete this project? All tasks will be lost!"):
        return
    
    async def delete_project():
        async with get_client(config) as client:
            project_manager = ProjectManager(client)
            await project_manager.delete_project(project_id)
            progress.show_success("Project deleted!")
    
    try:
        asyncio.run(delete_project())
    except Exception as e:
        progress.show_error(f"Failed to delete project: {e}")