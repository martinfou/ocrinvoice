"""
Category Manager

Manages CRA expense categories for the OCR invoice application.
Handles CRUD operations for categories with CRA codes.
"""

import json
import os
from typing import Dict, List, Optional
from datetime import datetime
import uuid


class CategoryManager:
    """
    Manager for CRA expense categories.
    
    Handles storage and retrieval of expense categories with their
    associated CRA codes for tax purposes.
    """

    def __init__(self, config_dir: str = "config"):
        """
        Initialize the category manager.
        
        Args:
            config_dir: Directory to store category configuration
        """
        self.config_dir = config_dir
        self.categories_file = os.path.join(config_dir, "categories.json")
        self.categories: List[Dict[str, str]] = []
        self._load_categories()

    def _load_categories(self) -> None:
        """Load categories from the configuration file."""
        try:
            if os.path.exists(self.categories_file):
                with open(self.categories_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.categories = data.get("categories", [])
            else:
                # Initialize with default CRA categories
                self.categories = self._get_default_categories()
                self._save_categories()
        except Exception as e:
            print(f"Error loading categories: {e}")
            # Fallback to default categories
            self.categories = self._get_default_categories()

    def _save_categories(self) -> None:
        """Save categories to the configuration file."""
        try:
            # Ensure config directory exists
            os.makedirs(self.config_dir, exist_ok=True)
            
            data = {
                "categories": self.categories,
                "last_updated": datetime.now().isoformat()
            }
            
            with open(self.categories_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving categories: {e}")

    def _get_default_categories(self) -> List[Dict[str, str]]:
        """Get default CRA expense categories."""
        return [
            {
                "id": str(uuid.uuid4()),
                "name": "Office Supplies",
                "description": "General office supplies and stationery",
                "cra_code": "8520",
                "created_date": datetime.now().isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Meals and Entertainment",
                "description": "Business meals and entertainment expenses",
                "cra_code": "8530",
                "created_date": datetime.now().isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Travel Expenses",
                "description": "Business travel and accommodation",
                "cra_code": "8540",
                "created_date": datetime.now().isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Vehicle Expenses",
                "description": "Vehicle operating costs and maintenance",
                "cra_code": "8550",
                "created_date": datetime.now().isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Professional Fees",
                "description": "Legal, accounting, and professional services",
                "cra_code": "8560",
                "created_date": datetime.now().isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Advertising and Promotion",
                "description": "Marketing, advertising, and promotional expenses",
                "cra_code": "8570",
                "created_date": datetime.now().isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Insurance",
                "description": "Business insurance premiums",
                "cra_code": "8580",
                "created_date": datetime.now().isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Utilities",
                "description": "Electricity, water, gas, and other utilities",
                "cra_code": "8590",
                "created_date": datetime.now().isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Rent",
                "description": "Office and equipment rental expenses",
                "cra_code": "8600",
                "created_date": datetime.now().isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Telephone and Internet",
                "description": "Communication and internet service costs",
                "cra_code": "8610",
                "created_date": datetime.now().isoformat()
            }
        ]

    def get_categories(self) -> List[Dict[str, str]]:
        """
        Get all categories.
        
        Returns:
            List of category dictionaries
        """
        return self.categories.copy()

    def get_category(self, category_id: str) -> Optional[Dict[str, str]]:
        """
        Get a specific category by ID.
        
        Args:
            category_id: The category ID
            
        Returns:
            Category dictionary or None if not found
        """
        for category in self.categories:
            if category.get("id") == category_id:
                return category.copy()
        return None

    def get_category_by_code(self, cra_code: str) -> Optional[Dict[str, str]]:
        """
        Get a category by CRA code.
        
        Args:
            cra_code: The CRA expense code
            
        Returns:
            Category dictionary or None if not found
        """
        for category in self.categories:
            if category.get("cra_code") == cra_code:
                return category.copy()
        return None

    def add_category(self, name: str, description: str, cra_code: str) -> str:
        """
        Add a new category.
        
        Args:
            name: Category name
            description: Category description
            cra_code: CRA expense code
            
        Returns:
            The ID of the newly created category
            
        Raises:
            ValueError: If CRA code already exists
        """
        # Check for duplicate CRA code
        cra_code = cra_code.strip()
        existing_category = self.get_category_by_code(cra_code)
        if existing_category:
            raise ValueError(f"CRA code '{cra_code}' is already used by category '{existing_category['name']}'")
        
        category_id = str(uuid.uuid4())
        category = {
            "id": category_id,
            "name": name.strip(),
            "description": description.strip(),
            "cra_code": cra_code,
            "created_date": datetime.now().isoformat()
        }
        
        self.categories.append(category)
        self._save_categories()
        return category_id

    def update_category(self, category_id: str, name: str, description: str, cra_code: str) -> bool:
        """
        Update an existing category.
        
        Args:
            category_id: The category ID to update
            name: New category name
            description: New category description
            cra_code: New CRA expense code
            
        Returns:
            True if category was updated, False if not found
            
        Raises:
            ValueError: If CRA code already exists in another category
        """
        cra_code = cra_code.strip()
        
        # Check for duplicate CRA code in other categories
        existing_category = self.get_category_by_code(cra_code)
        if existing_category and existing_category.get("id") != category_id:
            raise ValueError(f"CRA code '{cra_code}' is already used by category '{existing_category['name']}'")
        
        for category in self.categories:
            if category.get("id") == category_id:
                category["name"] = name.strip()
                category["description"] = description.strip()
                category["cra_code"] = cra_code
                self._save_categories()
                return True
        return False

    def delete_category(self, category_id: str) -> bool:
        """
        Delete a category.
        
        Args:
            category_id: The category ID to delete
            
        Returns:
            True if category was deleted, False if not found
        """
        for i, category in enumerate(self.categories):
            if category.get("id") == category_id:
                del self.categories[i]
                self._save_categories()
                return True
        return False

    def search_categories(self, search_term: str) -> List[Dict[str, str]]:
        """
        Search categories by name, description, or CRA code.
        
        Args:
            search_term: Search term to match against
            
        Returns:
            List of matching category dictionaries
        """
        search_term = search_term.lower().strip()
        if not search_term:
            return self.categories.copy()
        
        matches = []
        for category in self.categories:
            name = category.get("name", "").lower()
            description = category.get("description", "").lower()
            cra_code = category.get("cra_code", "").lower()
            
            if (search_term in name or 
                search_term in description or 
                search_term in cra_code):
                matches.append(category.copy())
        
        return matches

    def get_category_names(self) -> List[str]:
        """
        Get list of category names.
        
        Returns:
            List of category names
        """
        return [category.get("name", "") for category in self.categories]

    def get_category_codes(self) -> List[str]:
        """
        Get list of CRA codes.
        
        Returns:
            List of CRA codes
        """
        return [category.get("cra_code", "") for category in self.categories]

    def reload_categories(self) -> None:
        """Reload categories from the configuration file."""
        self._load_categories()

    def backup_categories(self) -> str:
        """
        Create a backup of the categories.
        
        Returns:
            Path to the backup file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = os.path.join(self.config_dir, f"categories_backup_{timestamp}.json")
        
        try:
            data = {
                "categories": self.categories,
                "backup_date": datetime.now().isoformat(),
                "original_file": self.categories_file
            }
            
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            return backup_file
        except Exception as e:
            print(f"Error creating backup: {e}")
            return ""

    def restore_categories(self, backup_file: str) -> bool:
        """
        Restore categories from a backup file.
        
        Args:
            backup_file: Path to the backup file
            
        Returns:
            True if restore was successful, False otherwise
        """
        try:
            with open(backup_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.categories = data.get("categories", [])
                self._save_categories()
            return True
        except Exception as e:
            print(f"Error restoring categories: {e}")
            return False 