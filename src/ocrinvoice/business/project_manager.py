"""
Project Manager using SQLite Database

Manages projects using the new SQLite database system instead of JSON files.
"""

import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

from ocrinvoice.business.database_manager import DatabaseManager


class ProjectManager:
    """
    Project manager using SQLite database for data storage.
    
    Provides a clean interface for managing projects with proper
    data validation and relationships.
    """
    
    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        """
        Initialize the project manager.
        
        Args:
            db_manager: Database manager instance. If None, creates a new one.
        """
        self.db_manager = db_manager or DatabaseManager()
    
    def add_project(self, name: str, description: Optional[str] = None) -> bool:
        """
        Add a new project.
        
        Args:
            name: Project name
            description: Optional project description
            
        Returns:
            True if project was added successfully, False if it already exists
        """
        project_id = self.db_manager.add_project(name, description)
        return project_id is not None
    
    def get_all_projects(self) -> List[Dict[str, Any]]:
        """
        Get all projects.
        
        Returns:
            List of project dictionaries
        """
        projects = self.db_manager.get_all_projects()
        return [
            {
                "id": str(project["id"]),
                "name": project["name"],
                "description": project["description"],
                "created_at": project["created_at"],
                "updated_at": project["updated_at"]
            }
            for project in projects
        ]
    
    def get_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a project by ID.
        
        Args:
            project_id: Project ID
            
        Returns:
            Project dictionary or None if not found
        """
        try:
            project = self.db_manager.get_project(int(project_id))
            if project:
                return {
                    "id": str(project["id"]),
                    "name": project["name"],
                    "description": project["description"],
                    "created_at": project["created_at"],
                    "updated_at": project["updated_at"]
                }
        except (ValueError, TypeError):
            pass
        return None
    
    def get_project_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get a project by name.
        
        Args:
            name: Project name
            
        Returns:
            Project dictionary or None if not found
        """
        projects = self.get_all_projects()
        for project in projects:
            if project["name"] == name:
                return project
        return None
    
    def update_project(self, project_id: str, name: str, description: Optional[str] = None) -> bool:
        """
        Update a project.
        
        Args:
            project_id: Project ID
            name: New project name
            description: New project description
            
        Returns:
            True if project was updated successfully, False otherwise
        """
        try:
            return self.db_manager.update_project(int(project_id), name, description)
        except (ValueError, TypeError):
            return False
    
    def delete_project(self, project_id: str) -> bool:
        """
        Delete a project.
        
        Args:
            project_id: Project ID
            
        Returns:
            True if project was deleted successfully, False otherwise
        """
        try:
            return self.db_manager.delete_project(int(project_id))
        except (ValueError, TypeError):
            return False
    
    def project_exists(self, name: str) -> bool:
        """
        Check if a project exists by name.
        
        Args:
            name: Project name
            
        Returns:
            True if project exists, False otherwise
        """
        return self.get_project_by_name(name) is not None
    
    def get_project_names(self) -> List[str]:
        """
        Get list of all project names.
        
        Returns:
            List of project names
        """
        projects = self.get_all_projects()
        return [project["name"] for project in projects]
    
    def get_stats(self) -> Dict[str, int]:
        """
        Get project statistics.
        
        Returns:
            Dictionary with project statistics
        """
        projects = self.get_all_projects()
        return {
            "total_projects": len(projects),
            "projects_with_descriptions": len([p for p in projects if p.get("description")])
        }
    
    def search_projects(self, search_term: str) -> List[Dict[str, Any]]:
        """
        Search projects by name or description.
        
        Args:
            search_term: Search term
            
        Returns:
            List of matching projects
        """
        projects = self.get_all_projects()
        search_term_lower = search_term.lower()
        
        matching_projects = []
        for project in projects:
            name_match = search_term_lower in project["name"].lower()
            description_match = (
                project.get("description") and 
                search_term_lower in project["description"].lower()
            )
            
            if name_match or description_match:
                matching_projects.append(project)
        
        return matching_projects
    
    def backup_projects(self) -> str:
        """
        Create a backup of the projects database.
        
        Returns:
            Path to the backup file
        """
        return self.db_manager.backup_database()
    
    def reload_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        """
        Reload a project from the database.
        
        Args:
            project_id: Project ID to reload
            
        Returns:
            Updated project dictionary or None if not found
        """
        return self.get_project(project_id)
    
    def reload_projects(self) -> List[Dict[str, Any]]:
        """
        Reload all projects from the database.
        
        Returns:
            List of all project dictionaries
        """
        return self.get_all_projects()
    
    def get_default_projects(self) -> List[Dict[str, Any]]:
        """
        Get a list of default projects.
        
        Returns:
            List of default project dictionaries
        """
        return [
            {
                "name": "General",
                "description": "General business expenses and invoices"
            },
            {
                "name": "Software Development",
                "description": "Software development and programming projects"
            },
            {
                "name": "Marketing",
                "description": "Marketing and advertising projects"
            },
            {
                "name": "Consulting",
                "description": "Consulting and professional services"
            }
        ]
    
    def initialize_default_projects(self) -> int:
        """
        Initialize the database with default projects if none exist.
        
        Returns:
            Number of projects added
        """
        existing_projects = self.get_all_projects()
        if existing_projects:
            return 0  # Projects already exist
        
        default_projects = self.get_default_projects()
        added_count = 0
        
        for project in default_projects:
            if self.add_project(project["name"], project["description"]):
                added_count += 1
        
        return added_count
    
    def get_default_project(self) -> str:
        """
        Get the default project name.
        
        Returns:
            Default project name or empty string if no projects exist
        """
        projects = self.get_all_projects()
        if projects:
            # Return the first project as default
            return projects[0]["name"]
        return ""
