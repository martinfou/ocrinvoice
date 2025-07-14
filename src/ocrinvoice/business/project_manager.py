"""
Project Manager

Manages project names for file naming templates.
Supports CRUD operations for projects with JSON-based storage.
"""

import json
import os
from typing import Optional, Dict, List
from pathlib import Path
from datetime import datetime


class ProjectManager:
    """
    Manages project names for invoice OCR file naming.
    Supports adding, editing, deleting, and listing projects.
    All project names are normalized to use hyphens for multi-word projects.
    """

    def __init__(self, project_file: Optional[str] = None):
        """
        Initialize the ProjectManager with a project configuration file.

        Args:
            project_file: Path to the JSON configuration file containing projects.
                       If None, will try to find the file using the same logic as the config system.
        """
        self.project_file = self._resolve_project_file_path(project_file)
        self.projects = self._load_projects()

    def _resolve_project_file_path(self, project_file: Optional[str]) -> str:
        """
        Resolve the project file path using the same logic as the config system.

        Args:
            project_file: Explicit path to project file, or None to auto-detect

        Returns:
            Resolved path to the project file
        """
        if project_file:
            return project_file

        # Try multiple locations in order of preference
        possible_paths = [
            # From current working directory
            Path.cwd() / "config" / "projects.json",
            # From project root (when running from source)
            Path(__file__).parent.parent.parent.parent / "config" / "projects.json",
            # From installed package
            Path(__file__).parent.parent.parent / "config" / "projects.json",
            # From user's home directory
            Path.home() / ".ocrinvoice" / "projects.json",
        ]

        for path in possible_paths:
            if path.exists():
                return str(path)

        # If no file found, return the first path as default
        return str(possible_paths[0])

    def _load_projects(self) -> Dict[str, Dict[str, str]]:
        """Load the project configuration from JSON file."""
        if not os.path.exists(self.project_file):
            # Return default empty config if file doesn't exist
            return {}

        try:
            with open(self.project_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Could not load project file {self.project_file}: {e}")
            return {}

    def _save_projects(self) -> None:
        """Save the project configuration to JSON file."""
        # Ensure the directory exists
        os.makedirs(os.path.dirname(self.project_file), exist_ok=True)

        try:
            with open(self.project_file, "w", encoding="utf-8") as f:
                json.dump(self.projects, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Error saving project file {self.project_file}: {e}")
            raise

    def _normalize_project_name(self, name: str) -> str:
        """
        Normalize project name to use hyphens for multi-word projects.

        Args:
            name: The project name to normalize

        Returns:
            Normalized project name with hyphens
        """
        # Remove extra whitespace and replace spaces/hyphens with single hyphens
        normalized = " ".join(name.split())
        normalized = normalized.replace(" ", "-").replace("_", "-")

        # Remove multiple consecutive hyphens
        while "--" in normalized:
            normalized = normalized.replace("--", "-")

        # Remove leading/trailing hyphens
        normalized = normalized.strip("-")

        return normalized.lower()

    def get_projects(self) -> List[Dict[str, str]]:
        """
        Get all projects as a list of dictionaries.

        Returns:
            List of project dictionaries with keys: id, name, description, created_date
        """
        projects_list = []
        for project_id, project_data in self.projects.items():
            project_dict = {
                "id": project_id,
                "name": project_data.get("name", project_id),
                "description": project_data.get("description", ""),
                "created_date": project_data.get("created_date", ""),
            }
            projects_list.append(project_dict)

        # Sort by name
        return sorted(projects_list, key=lambda x: x["name"].lower())

    def get_project_names(self) -> List[str]:
        """
        Get list of all project names.

        Returns:
            List of project names
        """
        return [project["name"] for project in self.get_projects()]

    def add_project(self, name: str, description: str = "") -> str:
        """
        Add a new project.

        Args:
            name: The project name
            description: Optional project description

        Returns:
            The normalized project ID

        Raises:
            ValueError: If project name is empty or already exists
        """
        if not name or not name.strip():
            raise ValueError("Project name cannot be empty")

        normalized_id = self._normalize_project_name(name)

        if normalized_id in self.projects:
            raise ValueError(f"Project '{name}' already exists")

        project_data = {
            "name": name.strip(),
            "description": description.strip(),
            "created_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

        self.projects[normalized_id] = project_data
        self._save_projects()

        return normalized_id

    def update_project(self, project_id: str, name: str, description: str = "") -> bool:
        """
        Update an existing project.

        Args:
            project_id: The current project ID
            name: The new project name
            description: The new project description

        Returns:
            True if updated successfully, False if project not found

        Raises:
            ValueError: If project name is empty or conflicts with existing project
        """
        if not name or not name.strip():
            raise ValueError("Project name cannot be empty")

        if project_id not in self.projects:
            return False

        new_normalized_id = self._normalize_project_name(name)

        # Check if new name conflicts with existing project (excluding current)
        if new_normalized_id in self.projects and new_normalized_id != project_id:
            raise ValueError(f"Project '{name}' already exists")

        # Update project data
        self.projects[project_id]["name"] = name.strip()
        self.projects[project_id]["description"] = description.strip()

        # If ID changed, move to new ID
        if new_normalized_id != project_id:
            self.projects[new_normalized_id] = self.projects.pop(project_id)

        self._save_projects()
        return True

    def delete_project(self, project_id: str) -> bool:
        """
        Delete a project.

        Args:
            project_id: The project ID to delete

        Returns:
            True if deleted successfully, False if project not found
        """
        if project_id not in self.projects:
            return False

        del self.projects[project_id]
        self._save_projects()
        return True

    def get_project(self, project_id: str) -> Optional[Dict[str, str]]:
        """
        Get a specific project by ID.

        Args:
            project_id: The project ID

        Returns:
            Project dictionary or None if not found
        """
        if project_id not in self.projects:
            return None

        project_data = self.projects[project_id]
        return {
            "id": project_id,
            "name": project_data.get("name", project_id),
            "description": project_data.get("description", ""),
            "created_date": project_data.get("created_date", ""),
        }

    def project_exists(self, project_id: str) -> bool:
        """
        Check if a project exists.

        Args:
            project_id: The project ID to check

        Returns:
            True if project exists, False otherwise
        """
        return project_id in self.projects

    def get_default_project(self) -> str:
        """
        Get the default project name.

        Returns:
            Default project name ("project")
        """
        return "project"

    def reload_projects(self) -> None:
        """Reload projects from the configuration file."""
        self.projects = self._load_projects()

    def get_stats(self) -> Dict[str, int]:
        """
        Get project statistics.

        Returns:
            Dictionary with project statistics
        """
        return {
            "total_projects": len(self.projects),
        }
