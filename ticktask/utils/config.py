import yaml
import os
from pathlib import Path
from typing import Dict, Any, Optional


class Config:
    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or self._get_default_config_path()
        self.config_data = self._load_config()

    def _get_default_config_path(self) -> Path:
        # Check for config in current directory
        local_config = Path("ticktask_config.yaml")
        if local_config.exists():
            return local_config
        
        # Check for config in home directory
        home_config = Path.home() / ".ticktask" / "config.yaml"
        if home_config.exists():
            return home_config
        
        # Default to home directory
        return home_config

    def _load_config(self) -> Dict[str, Any]:
        if not self.config_path.exists():
            return self._get_default_config()
        
        try:
            with open(self.config_path, "r") as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            print(f"Error loading config: {e}")
            return self._get_default_config()

    def _get_default_config(self) -> Dict[str, Any]:
        return {
            "api": {
                "base_url": "https://api.ticktick.com",
                "client_id": os.getenv("TICKTICK_CLIENT_ID", ""),
                "client_secret": os.getenv("TICKTICK_CLIENT_SECRET", ""),
                "redirect_uri": "http://localhost:8080/callback"
            },
            "defaults": {
                "project": "inbox",
                "priority": 0,
                "reminder": "9:00"
            },
            "obsidian": {
                "vault_path": str(Path.home() / "Documents" / "ObsidianVault"),
                "daily_notes_path": "Daily Notes",
                "task_log_template": "templates/task-log.md"
            },
            "workflows": {
                "daily_plan": {
                    "include_overdue": True,
                    "include_today": True,
                    "include_tomorrow": False
                }
            },
            "formatting": {
                "date_format": "%Y-%m-%d",
                "time_format": "%H:%M",
                "timezone": "America/Los_Angeles"
            }
        }

    def save(self) -> None:
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, "w") as f:
            yaml.dump(self.config_data, f, default_flow_style=False)

    def get(self, key: str, default: Any = None) -> Any:
        keys = key.split(".")
        value = self.config_data
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value

    def set(self, key: str, value: Any) -> None:
        keys = key.split(".")
        data = self.config_data
        for k in keys[:-1]:
            if k not in data:
                data[k] = {}
            data = data[k]
        data[keys[-1]] = value

    @property
    def client_id(self) -> str:
        return self.get("api.client_id", "")

    @property
    def client_secret(self) -> str:
        return self.get("api.client_secret", "")

    @property
    def redirect_uri(self) -> str:
        return self.get("api.redirect_uri", "http://localhost:8080/callback")

    @property
    def obsidian_vault_path(self) -> Path:
        return Path(self.get("obsidian.vault_path", Path.home() / "Documents" / "ObsidianVault"))

    @property
    def obsidian_daily_notes_path(self) -> str:
        return self.get("obsidian.daily_notes_path", "Daily Notes")

    @property
    def default_project(self) -> str:
        return self.get("defaults.project", "inbox")

    @property
    def default_priority(self) -> int:
        return self.get("defaults.priority", 0)

    @property
    def date_format(self) -> str:
        return self.get("formatting.date_format", "%Y-%m-%d")

    @property
    def time_format(self) -> str:
        return self.get("formatting.time_format", "%H:%M")

    @property
    def timezone(self) -> str:
        return self.get("formatting.timezone", "UTC")