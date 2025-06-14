from typing import Optional, Dict, Any, List
import httpx
from datetime import datetime
import logging
from .models import Task, Project, ProjectData, ChecklistItem
from .auth import OAuth2Handler

logger = logging.getLogger(__name__)


class TickTickClient:
    def __init__(self, access_token: Optional[str] = None, auth_handler: Optional[OAuth2Handler] = None):
        self.base_url = "https://api.ticktick.com/open/v1"
        self.access_token = access_token
        self.auth_handler = auth_handler
        self._client = None

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def connect(self):
        if not self.access_token and self.auth_handler:
            self.access_token = await self.auth_handler.get_access_token()
            if not self.access_token:
                self.access_token = await self.auth_handler.login()
        
        if not self.access_token:
            raise ValueError("No access token available")
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        self._client = httpx.AsyncClient(headers=headers, timeout=30.0)

    async def close(self):
        if self._client:
            await self._client.aclose()
            self._client = None

    async def _ensure_client(self):
        if not self._client:
            await self.connect()

    async def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        await self._ensure_client()
        url = f"{self.base_url}/{endpoint}"
        response = await self._client.get(url, params=params)
        response.raise_for_status()
        return response.json()

    async def post(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        await self._ensure_client()
        url = f"{self.base_url}/{endpoint}"
        response = await self._client.post(url, json=data)
        response.raise_for_status()
        return response.json()

    async def delete(self, endpoint: str) -> None:
        await self._ensure_client()
        url = f"{self.base_url}/{endpoint}"
        response = await self._client.delete(url)
        response.raise_for_status()

    # Project methods
    async def get_projects(self) -> List[Project]:
        data = await self.get("project")
        return [Project(**project) for project in data]

    async def get_project(self, project_id: str) -> Project:
        data = await self.get(f"project/{project_id}")
        return Project(**data)

    async def get_project_data(self, project_id: str) -> ProjectData:
        data = await self.get(f"project/{project_id}/data")
        return ProjectData(**data)

    async def create_project(self, name: str, color: Optional[str] = None, 
                           view_mode: str = "list", kind: str = "TASK") -> Project:
        data = {
            "name": name,
            "viewMode": view_mode,
            "kind": kind
        }
        if color:
            data["color"] = color
        
        response = await self.post("project", data)
        return Project(**response)

    async def update_project(self, project_id: str, **kwargs) -> Project:
        data = {}
        if "name" in kwargs:
            data["name"] = kwargs["name"]
        if "color" in kwargs:
            data["color"] = kwargs["color"]
        if "view_mode" in kwargs:
            data["viewMode"] = kwargs["view_mode"]
        if "kind" in kwargs:
            data["kind"] = kwargs["kind"]
        
        response = await self.post(f"project/{project_id}", data)
        return Project(**response)

    async def delete_project(self, project_id: str) -> None:
        await self.delete(f"project/{project_id}")

    # Task methods
    async def get_task(self, project_id: str, task_id: str) -> Task:
        data = await self.get(f"project/{project_id}/task/{task_id}")
        return Task(**data)

    async def create_task(self, title: str, project_id: str, **kwargs) -> Task:
        data = {
            "title": title,
            "projectId": project_id
        }
        
        # Handle optional fields
        if "content" in kwargs:
            data["content"] = kwargs["content"]
        if "desc" in kwargs:
            data["desc"] = kwargs["desc"]
        if "is_all_day" in kwargs:
            data["isAllDay"] = kwargs["is_all_day"]
        if "start_date" in kwargs:
            date = kwargs["start_date"]
            if isinstance(date, datetime):
                data["startDate"] = date.strftime("%Y-%m-%dT%H:%M:%S+0000")
            else:
                data["startDate"] = date
        if "due_date" in kwargs:
            date = kwargs["due_date"]
            if isinstance(date, datetime):
                data["dueDate"] = date.strftime("%Y-%m-%dT%H:%M:%S+0000")
            else:
                data["dueDate"] = date
        if "time_zone" in kwargs:
            data["timeZone"] = kwargs["time_zone"]
        if "reminders" in kwargs:
            data["reminders"] = kwargs["reminders"]
        if "repeat_flag" in kwargs:
            data["repeatFlag"] = kwargs["repeat_flag"]
        if "priority" in kwargs:
            data["priority"] = kwargs["priority"]
        if "sort_order" in kwargs:
            data["sortOrder"] = kwargs["sort_order"]
        if "items" in kwargs:
            items = []
            for item in kwargs["items"]:
                if isinstance(item, dict):
                    items.append(item)
                elif isinstance(item, ChecklistItem):
                    items.append(item.model_dump(by_alias=True, exclude_none=True))
            data["items"] = items
        
        response = await self.post("task", data)
        return Task(**response)

    async def update_task(self, task_id: str, project_id: str, **kwargs) -> Task:
        data = {
            "id": task_id,
            "projectId": project_id
        }
        
        # Handle optional fields (same as create_task)
        if "title" in kwargs:
            data["title"] = kwargs["title"]
        if "content" in kwargs:
            data["content"] = kwargs["content"]
        if "desc" in kwargs:
            data["desc"] = kwargs["desc"]
        if "is_all_day" in kwargs:
            data["isAllDay"] = kwargs["is_all_day"]
        if "start_date" in kwargs:
            date = kwargs["start_date"]
            if isinstance(date, datetime):
                data["startDate"] = date.strftime("%Y-%m-%dT%H:%M:%S+0000")
            else:
                data["startDate"] = date
        if "due_date" in kwargs:
            date = kwargs["due_date"]
            if isinstance(date, datetime):
                data["dueDate"] = date.strftime("%Y-%m-%dT%H:%M:%S+0000")
            else:
                data["dueDate"] = date
        if "time_zone" in kwargs:
            data["timeZone"] = kwargs["time_zone"]
        if "reminders" in kwargs:
            data["reminders"] = kwargs["reminders"]
        if "repeat_flag" in kwargs:
            data["repeatFlag"] = kwargs["repeat_flag"]
        if "priority" in kwargs:
            data["priority"] = kwargs["priority"]
        if "sort_order" in kwargs:
            data["sortOrder"] = kwargs["sort_order"]
        if "items" in kwargs:
            items = []
            for item in kwargs["items"]:
                if isinstance(item, dict):
                    items.append(item)
                elif isinstance(item, ChecklistItem):
                    items.append(item.model_dump(by_alias=True, exclude_none=True))
            data["items"] = items
        
        response = await self.post(f"task/{task_id}", data)
        return Task(**response)

    async def complete_task(self, project_id: str, task_id: str) -> None:
        await self.post(f"project/{project_id}/task/{task_id}/complete", {})

    async def delete_task(self, project_id: str, task_id: str) -> None:
        await self.delete(f"project/{project_id}/task/{task_id}")