"""
Business Mapping Manager using SQLite Database

Enhanced business mapping manager that uses SQLite for data storage
instead of JSON files. Provides better performance, data integrity,
and relationship management.
"""

import os
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

from ocrinvoice.business.database_manager import DatabaseManager
from ocrinvoice.utils.fuzzy_matcher import FuzzyMatcher


class BusinessMappingManagerSQLite:
    """
    Enhanced business mapping manager using SQLite database.
    
    Provides a clean, consistent interface for managing business data
    with proper relationships, validation, and performance.
    """
    
    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        """
        Initialize the business mapping manager.
        
        Args:
            db_manager: Database manager instance. If None, creates a new one.
        """
        self.db_manager = db_manager or DatabaseManager()
        self.fuzzy_matcher = FuzzyMatcher()
        
        # Initialize fuzzy matcher with existing businesses
        self._update_fuzzy_matcher()
    
    def _update_fuzzy_matcher(self) -> None:
        """Update the fuzzy matcher with current business data."""
        businesses = self.db_manager.get_all_businesses()
        business_names = [business["business_name"] for business in businesses]
        self.fuzzy_matcher.update_candidates(business_names)
    
    def add_business_name(self, name: str, metadata: Optional[Dict] = None) -> bool:
        """
        Add a business name.
        
        Args:
            name: The business name
            metadata: Optional metadata dictionary
            
        Returns:
            True if business was added successfully, False if it already exists
        """
        business_id = self.db_manager.add_business(name, metadata)
        if business_id:
            self._update_fuzzy_matcher()
            return True
        return False
    
    def get_business_names(self) -> List[str]:
        """
        Get all business names.
        
        Returns:
            List of business names
        """
        businesses = self.db_manager.get_all_businesses()
        return [business["business_name"] for business in businesses]
    
    # Compatibility methods for backward compatibility
    def add_canonical_name(self, name: str, metadata: Optional[Dict] = None) -> bool:
        """Compatibility method - use add_business_name instead."""
        return self.add_business_name(name, metadata)
    
    def get_canonical_names(self) -> List[str]:
        """Compatibility method - use get_business_names instead."""
        return self.get_business_names()
    
    def get_all_businesses(self) -> List[Dict[str, Any]]:
        """
        Get all businesses with their keywords.
        
        Returns:
            List of business dictionaries with keywords
        """
        businesses = self.db_manager.get_all_businesses()
        result = []
        
        for business in businesses:
            business_dict = {
                "id": str(business["id"]),
                "business_name": business["business_name"],
                "created_at": business["created_at"],
                "updated_at": business["updated_at"],
                "metadata": business.get("metadata", "{}"),
                "keywords": []
            }
            
            # Get keywords for this business
            keywords = self.db_manager.get_business_aliases(business["id"])
            for keyword in keywords:
                business_dict["keywords"].append({
                    "keyword": keyword["keyword"],
                    "match_type": keyword["match_type"],
                    "case_sensitive": keyword["case_sensitive"],
                    "fuzzy_matching": keyword["fuzzy_matching"]
                })
            
            result.append(business_dict)
        
        return result
    
    def get_business_by_id(self, business_id: str) -> Optional[Dict[str, Any]]:
        """
        Get business by ID.
        
        Args:
            business_id: Business ID
            
        Returns:
            Business dictionary or None if not found
        """
        try:
            business = self.db_manager.get_business(int(business_id))
            if business:
                business_dict = {
                    "id": str(business["id"]),
                    "business_name": business["business_name"],
                    "created_at": business["created_at"],
                    "updated_at": business["updated_at"],
                    "metadata": business.get("metadata", "{}"),
                    "keywords": []
                }
                
                # Get keywords for this business
                keywords = self.db_manager.get_business_aliases(business["id"])
                for keyword in keywords:
                    business_dict["keywords"].append({
                        "keyword": keyword["keyword"],
                        "match_type": keyword["match_type"],
                        "case_sensitive": keyword["case_sensitive"],
                        "fuzzy_matching": keyword["fuzzy_matching"]
                    })
                
                return business_dict
        except (ValueError, TypeError):
            pass
        return None
    
    def get_business_by_name(self, business_name: str) -> Optional[Dict[str, Any]]:
        """
        Get business by business name.
        
        Args:
            business_name: Business name
            
        Returns:
            Business dictionary or None if not found
        """
        business = self.db_manager.get_business_by_name(business_name)
        if business:
            return self.get_business_by_id(str(business["id"]))
        return None
    
    def update_business_name(self, old_name: str, new_name: str) -> bool:
        """
        Update a business name.
        
        Args:
            old_name: Current business name
            new_name: New business name
            
        Returns:
            True if updated successfully, False otherwise
        """
        business = self.db_manager.get_business_by_name(old_name)
        if business:
            success = self.db_manager.update_business(business["id"], new_name)
            if success:
                self._update_fuzzy_matcher()
            return success
        return False
    
    def remove_business_name(self, name: str) -> bool:
        """
        Remove a business name.
        
        Args:
            name: Business name to remove
            
        Returns:
            True if removed successfully, False otherwise
        """
        business = self.db_manager.get_business_by_name(name)
        if business:
            success = self.db_manager.delete_business(business["id"])
            if success:
                self._update_fuzzy_matcher()
            return success
        return False
    
    def is_business_name(self, name: str) -> bool:
        """
        Check if a name is a business name.
        
        Args:
            name: Name to check
            
        Returns:
            True if it's a business name, False otherwise
        """
        return self.db_manager.get_business_by_name(name) is not None
    
    # Additional compatibility methods
    def update_canonical_name(self, old_name: str, new_name: str) -> bool:
        """Compatibility method - use update_business_name instead."""
        return self.update_business_name(old_name, new_name)
    
    def remove_canonical_name(self, name: str) -> bool:
        """Compatibility method - use remove_business_name instead."""
        return self.remove_business_name(name)
    
    def is_canonical_name(self, name: str) -> bool:
        """Compatibility method - use is_business_name instead."""
        return self.is_business_name(name)
    
    def add_keyword(self, business_id: str, keyword: str, match_type: str = "exact",
                   case_sensitive: bool = False, fuzzy_matching: bool = True) -> bool:
        """
        Add a keyword/alias for a business.
        
        Args:
            business_id: Business ID
            keyword: Keyword/alias to add
            match_type: Type of matching (exact, variant, fuzzy)
            case_sensitive: Whether matching is case sensitive
            fuzzy_matching: Whether to use fuzzy matching
            
        Returns:
            True if keyword was added successfully, False otherwise
        """
        try:
            return self.db_manager.add_business_alias(
                int(business_id), keyword, match_type, case_sensitive, fuzzy_matching
            )
        except (ValueError, TypeError):
            return False
    
    def remove_keyword(self, business_id: str, keyword: str, match_type: str) -> bool:
        """
        Remove a keyword/alias for a business.
        
        Args:
            business_id: Business ID
            keyword: Keyword/alias to remove
            match_type: Type of matching
            
        Returns:
            True if keyword was removed successfully, False otherwise
        """
        try:
            return self.db_manager.remove_keyword(int(business_id), keyword, match_type)
        except (ValueError, TypeError):
            return False
    
    def get_business_keywords(self, business_id: str) -> List[Dict[str, Any]]:
        """
        Get all keywords/aliases for a business.
        
        Args:
            business_id: Business ID
            
        Returns:
            List of keyword dictionaries
        """
        try:
            aliases = self.db_manager.get_business_aliases(int(business_id))
            return [
                {
                    "keyword": alias["keyword"],
                    "match_type": alias["match_type"],
                    "case_sensitive": alias["case_sensitive"],
                    "fuzzy_matching": alias["fuzzy_matching"]
                }
                for alias in aliases
            ]
        except (ValueError, TypeError):
            return []
    
    def find_business_match(self, text: str) -> Optional[Tuple[str, str, float]]:
        """
        Find a business match in the given text.
        
        Args:
            text: Text to search for business matches
            
        Returns:
            Tuple of (business_id, canonical_name, confidence) or None if no match
        """
        # Try exact match first
        result = self._find_exact_match(text)
        if result:
            return result
        
        # Try variant match
        result = self._find_variant_match(text)
        if result:
            return result
        
        # Try fuzzy match
        result = self._find_fuzzy_match(text)
        return result
    
    def _find_exact_match(self, text: str) -> Optional[Tuple[str, str, float]]:
        """Find exact match for text."""
        business = self.db_manager.find_business_by_keyword(text, "exact")
        if business:
            return (str(business["id"]), business["canonical_name"], 1.0)
        return None
    
    def _find_variant_match(self, text: str) -> Optional[Tuple[str, str, float]]:
        """Find variant match for text."""
        business = self.db_manager.find_business_by_keyword(text, "variant")
        if business:
            return (str(business["id"]), business["canonical_name"], 0.9)
        return None
    
    def _find_fuzzy_match(self, text: str) -> Optional[Tuple[str, str, float]]:
        """Find fuzzy match for text."""
        # First try database fuzzy matches
        business = self.db_manager.find_business_by_keyword(text, "fuzzy")
        if business:
            return (str(business["id"]), business["canonical_name"], 0.8)
        
        # Then try fuzzy matcher with canonical names
        best_match = self.fuzzy_matcher.find_best_match(text)
        if best_match:
            business = self.db_manager.get_business_by_name(best_match[0])
            if business:
                return (str(business["id"]), business["canonical_name"], best_match[1])
        
        return None
    
    def get_stats(self) -> Dict[str, int]:
        """
        Get business mapping statistics.
        
        Returns:
            Dictionary with business statistics
        """
        db_stats = self.db_manager.get_stats()
        return {
            "businesses": db_stats["businesses"],
            "aliases": db_stats["aliases"],
            "total_businesses": db_stats["businesses"],
            "total_aliases": db_stats["aliases"]
        }
    
    def get_all_dropdown_names(self) -> List[str]:
        """
        Get all business names for dropdown display.
        
        Returns:
            List of business names
        """
        return self.get_canonical_names()
    
    def create_backup(self) -> str:
        """
        Create a backup of the business data.
        
        Returns:
            Path to the backup file
        """
        return self.db_manager.backup_database()
    
    def create_startup_backup(self) -> Optional[str]:
        """
        Create a backup on application startup.
        
        Returns:
            Path to the backup file or None if failed
        """
        try:
            return self.db_manager.backup_database()
        except Exception as e:
            print(f"⚠️ Startup backup failed: {e}")
            return None
    
    def create_shutdown_backup(self) -> Optional[str]:
        """
        Create a backup on application shutdown.
        
        Returns:
            Path to the backup file or None if failed
        """
        try:
            return self.db_manager.backup_database()
        except Exception as e:
            print(f"⚠️ Shutdown backup failed: {e}")
            return None
    
    def migrate_from_json(self, json_file_path: str) -> bool:
        """
        Migrate data from JSON format to SQLite.
        
        Args:
            json_file_path: Path to JSON file to migrate from
            
        Returns:
            True if migration was successful, False otherwise
        """
        success = self.db_manager.migrate_from_json(json_file_path)
        if success:
            self._update_fuzzy_matcher()
        return success 