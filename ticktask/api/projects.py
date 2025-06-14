from typing import List, Optional
from .client import TickTickClient
from .models import Project, ProjectData


class ProjectManager:
    def __init__(self, client: TickTickClient):
        self.client = client

    async def list_projects(self) -> List[Project]:
        """List all projects"""
        return await self.client.get_projects()

    async def get_project(self, project_id: str) -> Project:
        """Get a specific project by ID"""
        return await self.client.get_project(project_id)

    async def get_project_by_name(self, name: str) -> Optional[Project]:
        """Find a project by name"""
        projects = await self.list_projects()
        for project in projects:
            if project.name.lower() == name.lower():
                return project
        return None

    async def get_project_data(self, project_id: str) -> ProjectData:
        """Get project with all its tasks and columns"""
        return await self.client.get_project_data(project_id)

    async def create_project(self, name: str, color: Optional[str] = None,
                           view_mode: str = "list", kind: str = "TASK") -> Project:
        """Create a new project"""
        return await self.client.create_project(name, color, view_mode, kind)

    async def update_project(self, project_id: str, **kwargs) -> Project:
        """Update an existing project"""
        return await self.client.update_project(project_id, **kwargs)

    async def delete_project(self, project_id: str) -> None:
        """Delete a project"""
        await self.client.delete_project(project_id)

    async def get_or_create_project(self, name: str, **kwargs) -> Project:
        """Get existing project by name or create if it doesn't exist"""
        project = await self.get_project_by_name(name)
        if project:
            return project
        return await self.create_project(name, **kwargs)