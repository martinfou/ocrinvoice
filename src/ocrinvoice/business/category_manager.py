"""
Category Manager using SQLite Database

Manages expense categories using the new SQLite database system instead of JSON files.
"""

import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

from ocrinvoice.business.database_manager import DatabaseManager


class CategoryManager:
    """
    Category manager using SQLite database for data storage.
    
    Provides a clean interface for managing expense categories with proper
    data validation and relationships.
    """
    
    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        """
        Initialize the category manager.
        
        Args:
            db_manager: Database manager instance. If None, creates a new one.
        """
        self.db_manager = db_manager or DatabaseManager()
    
    def add_category(self, name: str, description: Optional[str] = None, cra_code: Optional[str] = None) -> Optional[int]:
        """
        Add a new category.
        
        Args:
            name: Category name
            description: Optional category description
            cra_code: Optional expense code
            
        Returns:
            Category ID if added successfully, None if it already exists
        """
        return self.db_manager.add_category(name, description, cra_code)
    
    def get_all_categories(self) -> List[Dict[str, Any]]:
        """
        Get all categories.
        
        Returns:
            List of category dictionaries
        """
        categories = self.db_manager.get_all_categories()
        return [
            {
                "id": str(category["id"]),
                "name": category["name"],
                "description": category["description"],
                "cra_code": category["cra_code"],
                "created_at": category["created_at"],
                "updated_at": category["updated_at"]
            }
            for category in categories
        ]
    
    def get_category(self, category_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a category by ID.
        
        Args:
            category_id: Category ID
            
        Returns:
            Category dictionary or None if not found
        """
        try:
            category = self.db_manager.get_category(int(category_id))
            if category:
                return {
                    "id": str(category["id"]),
                    "name": category["name"],
                    "description": category["description"],
                    "cra_code": category["cra_code"],
                    "created_at": category["created_at"],
                    "updated_at": category["updated_at"]
                }
        except (ValueError, TypeError):
            pass
        return None
    
    def get_category_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get a category by name.
        
        Args:
            name: Category name
            
        Returns:
            Category dictionary or None if not found
        """
        categories = self.get_all_categories()
        for category in categories:
            if category["name"] == name:
                return category
        return None
    
    def get_category_by_cra_code(self, cra_code: str) -> Optional[Dict[str, Any]]:
        """
        Get a category by expense code.
        
        Args:
            cra_code: Expense code
            
        Returns:
            Category dictionary or None if not found
        """
        categories = self.get_all_categories()
        for category in categories:
            if category.get("cra_code") == cra_code:
                return category
        return None
    
    def update_category(self, category_id: str, name: str, description: Optional[str] = None, 
                       cra_code: Optional[str] = None) -> bool:
        """
        Update a category.
        
        Args:
            category_id: Category ID
            name: New category name
            description: New category description
            cra_code: New expense code
            
        Returns:
            True if category was updated successfully, False otherwise
        """
        try:
            return self.db_manager.update_category(int(category_id), name, description, cra_code)
        except (ValueError, TypeError):
            return False
    
    def delete_category(self, category_id: str) -> bool:
        """
        Delete a category.
        
        Args:
            category_id: Category ID
            
        Returns:
            True if category was deleted successfully, False otherwise
        """
        try:
            return self.db_manager.delete_category(int(category_id))
        except (ValueError, TypeError):
            return False
    
    def category_exists(self, name: str) -> bool:
        """
        Check if a category exists by name.
        
        Args:
            name: Category name
            
        Returns:
            True if category exists, False otherwise
        """
        return self.get_category_by_name(name) is not None
    
    def cra_code_exists(self, cra_code: str) -> bool:
        """
        Check if an expense code exists.
        
        Args:
            cra_code: Expense code
            
        Returns:
            True if expense code exists, False otherwise
        """
        return self.get_category_by_cra_code(cra_code) is not None
    
    def get_category_names(self) -> List[str]:
        """
        Get list of all category names.
        
        Returns:
            List of category names
        """
        categories = self.get_all_categories()
        return [category["name"] for category in categories]
    
    def get_cra_codes(self) -> List[str]:
        """
        Get list of all expense codes.
        
        Returns:
            List of expense codes (excluding None values)
        """
        categories = self.get_all_categories()
        return [category["cra_code"] for category in categories if category.get("cra_code")]
    
    def get_stats(self) -> Dict[str, int]:
        """
        Get category statistics.
        
        Returns:
            Dictionary with category statistics
        """
        categories = self.get_all_categories()
        return {
            "total_categories": len(categories),
            "categories_with_descriptions": len([c for c in categories if c.get("description")]),
            "categories_with_cra_codes": len([c for c in categories if c.get("cra_code")])
        }
    
    def search_categories(self, search_term: str) -> List[Dict[str, Any]]:
        """
        Search categories by name, description, or expense code.
        
        Args:
            search_term: Search term
            
        Returns:
            List of matching categories
        """
        categories = self.get_all_categories()
        search_term_lower = search_term.lower()
        
        matching_categories = []
        for category in categories:
            name_match = search_term_lower in category["name"].lower()
            description_match = (
                category.get("description") and 
                search_term_lower in category["description"].lower()
            )
            cra_code_match = (
                category.get("cra_code") and 
                search_term_lower in category["cra_code"].lower()
            )
            
            if name_match or description_match or cra_code_match:
                matching_categories.append(category)
        
        return matching_categories
    
    def get_categories_by_cra_code_pattern(self, pattern: str) -> List[Dict[str, Any]]:
        """
        Get categories that match an expense code pattern.
        
        Args:
            pattern: Expense code pattern (e.g., "SDE*" for software development)
            
        Returns:
            List of matching categories
        """
        categories = self.get_all_categories()
        matching_categories = []
        
        for category in categories:
            cra_code = category.get("cra_code", "")
            if cra_code and pattern.lower() in cra_code.lower():
                matching_categories.append(category)
        
        return matching_categories
    
    def backup_categories(self) -> str:
        """
        Create a backup of the categories database.
        
        Returns:
            Path to the backup file
        """
        return self.db_manager.backup_database()
    
    def get_default_categories(self) -> List[Dict[str, Any]]:
        """
        Get a list of default CRA categories.
        
        Returns:
            List of default category dictionaries
        """
        return [
            {
                "name": "Software Development",
                "description": "Software development and programming expenses",
                "cra_code": "SDE001"
            },
            {
                "name": "Office Supplies",
                "description": "Office supplies and equipment",
                "cra_code": "OFS002"
            },
            {
                "name": "Travel Expenses",
                "description": "Business travel and accommodation",
                "cra_code": "TRA003"
            },
            {
                "name": "Marketing",
                "description": "Marketing and advertising expenses",
                "cra_code": "MAR004"
            },
            {
                "name": "Professional Services",
                "description": "Legal, accounting, and consulting services",
                "cra_code": "PRO005"
            }
        ]
    
    def initialize_default_categories(self) -> int:
        """
        Initialize the database with default categories if none exist.
        
        Returns:
            Number of categories added
        """
        existing_categories = self.get_all_categories()
        if existing_categories:
            return 0  # Categories already exist
        
        default_categories = self.get_default_categories()
        added_count = 0
        
        for category in default_categories:
            if self.add_category(category["name"], category["description"], category["cra_code"]):
                added_count += 1
        
        return added_count 