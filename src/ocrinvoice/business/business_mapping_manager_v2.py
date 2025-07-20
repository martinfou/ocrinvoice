"""
Business Mapping Manager V2

Enhanced business mapping manager that supports the new hierarchical structure
while maintaining backward compatibility with the old format.
"""

import json
import os
import unicodedata
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set
from datetime import datetime

from ocrinvoice.utils.fuzzy_matcher import FuzzyMatcher


class BusinessMappingManagerV2:
    """
    Enhanced business mapping manager supporting hierarchical structure.
    
    Supports both old (v1) and new (v2) business mappings formats.
    Automatically detects format and handles accordingly.
    """

    def __init__(self, mapping_file: Optional[str] = None):
        """
        Initialize the business mapping manager.
        
        Args:
            mapping_file: Path to the business mappings file. If None, uses default.
        """
        self.mapping_file = self._resolve_mapping_file_path(mapping_file)
        
        # Load configuration
        self.config = self._load_config()
        self.version = self.config.get("version", "1.0")
        
        # Initialize data structures
        self.businesses = {}  # business_id -> business_data
        self.canonical_names = set()
        
        # Load businesses from config
        self._load_businesses()
        
        # Validate mappings
        self._validate_mappings()
        
        # Get backup configuration
        self.backup_config = self.config.get("backup", {})
        self.max_backups_to_keep = self.backup_config.get("max_backups_to_keep", 10)
        self.auto_cleanup = self.backup_config.get("auto_cleanup", True)
        self.cleanup_on_startup = self.backup_config.get("cleanup_on_startup", True)
        self.cleanup_on_shutdown = self.backup_config.get("cleanup_on_shutdown", True)

    def _resolve_mapping_file_path(self, mapping_file: Optional[str]) -> str:
        """Resolve the mapping file path."""
        if mapping_file is None:
            # Try v2 first, then fall back to v1
            config_dir = Path(__file__).parent.parent.parent.parent / "config"
            v2_file = config_dir / "business_mappings_v2.json"
            v1_file = config_dir / "business_mappings.json"
            
            if v2_file.exists():
                return str(v2_file)
            elif v1_file.exists():
                return str(v1_file)
            else:
                # Create default v2 file
                return str(v2_file)
        else:
            return mapping_file

    def _load_config(self) -> Dict[str, Any]:
        """Load the configuration from file."""
        if not os.path.exists(self.mapping_file):
            # Create default v2 structure
            return self._create_default_config()
            
        try:
            with open(self.mapping_file, "r", encoding="utf-8") as f:
                config = json.load(f)
            
            # Detect version
            if "version" in config:
                self.version = config["version"]
            else:
                self.version = "1.0"
                
            return config
        except Exception as e:
            print(f"Warning: Could not load mapping file {self.mapping_file}: {e}")
            return self._create_default_config()

    def _create_default_config(self) -> Dict[str, Any]:
        """Create a default v2 configuration."""
        # Try to load backup settings from default config
        backup_config = {}
        try:
            from ocrinvoice.config import get_config
            default_config = get_config()
            backup_config = default_config.get("business", {}).get("backup", {})
        except Exception as e:
            print(f"Warning: Could not load default backup config: {e}")
            # Use hardcoded defaults
            backup_config = {
                "max_backups_to_keep": 10,
                "auto_cleanup": True,
                "cleanup_on_startup": True,
                "cleanup_on_shutdown": True
            }
        
        return {
            "version": "2.0",
            "created": datetime.now().isoformat(),
            "businesses": [],
            "confidence_weights": {
                "exact_match": 1.0,
                "variant_match": 0.8,
                "fuzzy_match": 0.6
            },
            "backup": backup_config
        }

    def _load_businesses(self):
        """Load businesses from the configuration."""
        if self.version == "2.0":
            self._load_v2_businesses()
        else:
            self._load_v1_businesses()

    def _load_v2_businesses(self):
        """Load businesses from v2 structure."""
        businesses = self.config.get("businesses", [])
        
        for business in businesses:
            business_id = business["id"]
            # Handle both old and new field names for backward compatibility
            business_name = business.get("business_name") or business.get("canonical_name", "")
            
            self.businesses[business_id] = business
            self.canonical_names.add(business_name)  # Keep canonical_names for backward compatibility

    def _load_v1_businesses(self):
        """Load businesses from v1 structure (backward compatibility)."""
        # Extract canonical names
        canonical_names = self.config.get("canonical_names", [])
        self.canonical_names = set(canonical_names)
        
        # Create business entries from v1 structure
        exact_matches = self.config.get("exact_matches", {})
        partial_matches = self.config.get("partial_matches", {})
        fuzzy_candidates = self.config.get("fuzzy_candidates", [])
        indicators = self.config.get("indicators", {})
        
        # Group by canonical name
        business_groups = {}
        
        # Add exact matches
        for keyword, canonical in exact_matches.items():
            if canonical not in business_groups:
                business_groups[canonical] = {"exact": [], "variant": [], "fuzzy": False}
            business_groups[canonical]["exact"].append(keyword)
        
        # Add variant matches (converted from partial)
        for keyword, canonical in partial_matches.items():
            if canonical not in business_groups:
                business_groups[canonical] = {"exact": [], "variant": [], "fuzzy": False}
            business_groups[canonical]["variant"].append(keyword)
        
        # Add fuzzy candidates
        for canonical in fuzzy_candidates:
            if canonical not in business_groups:
                business_groups[canonical] = {"exact": [], "variant": [], "fuzzy": False}
            business_groups[canonical]["fuzzy"] = True
        
        # Create business entries
        for canonical_name, groups in business_groups.items():
            business_id = self._generate_business_id(canonical_name)
            
            aliases = []
            
            # Add exact matches
            for keyword in groups["exact"]:
                aliases.append({
                    "keyword": keyword,
                    "match_type": "exact",
                    "case_sensitive": False,
                    "fuzzy_matching": True
                })
            
            # Add variant matches
            for keyword in groups["variant"]:
                aliases.append({
                    "keyword": keyword,
                    "match_type": "variant",
                    "case_sensitive": False,
                    "fuzzy_matching": True
                })
            
            # Add fuzzy match
            if groups["fuzzy"]:
                aliases.append({
                    "keyword": canonical_name,
                    "match_type": "fuzzy",
                    "case_sensitive": False,
                    "fuzzy_matching": True
                })
            
            # Get indicators
            business_indicators = indicators.get(canonical_name, [])
            
            business_entry = {
                "id": business_id,
                "business_name": canonical_name,  # Changed from canonical_name
                "keywords": aliases,  # Changed from aliases
                "indicators": business_indicators,
                "metadata": {
                    "created": datetime.now().isoformat(),
                    "migrated_from_v1": True
                }
            }
            
            self.businesses[business_id] = business_entry

    def _generate_business_id(self, business_name: str) -> str:
        """Generate a business ID from the business name."""
        import re
        id_base = re.sub(r'[^a-zA-Z0-9\s-]', '', business_name.lower())
        id_base = re.sub(r'\s+', '-', id_base.strip())
        return id_base

    def _validate_mappings(self) -> None:
        """Validate the business mappings for consistency."""
        # Check for duplicate business IDs
        business_ids = [b["id"] for b in self.businesses.values()]
        if len(business_ids) != len(set(business_ids)):
            print("Warning: Duplicate business IDs found")
        
        # Check for duplicate business names (with backward compatibility)
        business_names = []
        for business in self.businesses.values():
            # Handle both old and new field names for backward compatibility
            business_name = business.get("business_name") or business.get("canonical_name", "")
            business_names.append(business_name)
        
        if len(business_names) != len(set(business_names)):
            print("Warning: Duplicate business names found")

    def get_canonical_names(self) -> List[str]:
        """Get all canonical business names."""
        return sorted(list(self.canonical_names))

    def add_canonical_name(self, name: str) -> bool:
        """Add a business name."""
        if name in self.canonical_names:
            return False
        
        # Generate business ID
        business_id = self._generate_business_id(name)
        
        # Create business entry
        business_entry = {
            "id": business_id,
            "business_name": name,  # Changed from canonical_name
            "keywords": [],  # Changed from aliases
            "indicators": [],
            "metadata": {
                "created": datetime.now().isoformat(),
                "added_via_gui": True,
                "updated": datetime.now().isoformat()
            }
        }
        
        # Add to data structures
        self.businesses[business_id] = business_entry
        self.canonical_names.add(name)
        
        # Save to file
        self._save_config()
        return True

    def remove_canonical_name(self, name: str) -> bool:
        """Remove a business name."""
        if name not in self.canonical_names:
            return False
        
        # Find the business by name
        business_to_remove = None
        for business_id, business in self.businesses.items():
            # Handle both old and new field names for backward compatibility
            business_name = business.get("business_name") or business.get("canonical_name", "")
            if business_name == name:
                business_to_remove = business_id
                break
        
        if business_to_remove:
            # Remove from data structures
            del self.businesses[business_to_remove]
            self.canonical_names.remove(name)
            
            # Save to file
            self._save_config()
            return True
        
        return False

    def update_canonical_name(self, old_name: str, new_name: str) -> bool:
        """Update a business name."""
        if old_name not in self.canonical_names:
            return False
        
        if new_name in self.canonical_names:
            return False
        
        # Find the business by name
        for business in self.businesses.values():
            # Handle both old and new field names for backward compatibility
            business_name = business.get("business_name") or business.get("canonical_name", "")
            if business_name == old_name:
                # Update the business name
                business["business_name"] = new_name  # Changed from canonical_name
                business["metadata"]["updated"] = datetime.now().isoformat()
                
                # Update data structures
                self.canonical_names.remove(old_name)
                self.canonical_names.add(new_name)
                
                # Save to file
                self._save_config()
                return True
        
        return False

    def is_canonical_name(self, name: str) -> bool:
        """Check if a name is a canonical business name."""
        return name in self.canonical_names

    def find_business_match(self, text: str) -> Optional[Tuple[str, str, float]]:
        """Find a business match in the given text."""
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
        if result:
            return result
        
        return None

    def _find_exact_match(self, text: str) -> Optional[Tuple[str, str, float]]:
        """Find exact matches."""
        def normalize(s: str) -> str:
            s = s.lower()
            s = unicodedata.normalize("NFKC", s)
            s = " ".join(s.split())
            return s
        
        def create_spaced_variants(s: str) -> List[str]:
            variants = [s]
            no_spaces = s.replace(" ", "")
            if no_spaces != s:
                variants.append(no_spaces)
            spaced = " ".join(no_spaces)
            if spaced != s:
                variants.append(spaced)
            return variants
        
        text_norm = normalize(text)
        
        for business in self.businesses.values():
            # Handle both old and new field names for backward compatibility
            business_name = business.get("business_name") or business.get("canonical_name", "")
            keywords = business.get("keywords") or business.get("aliases", [])
            
            for keyword in keywords:
                if keyword["match_type"] == "exact":
                    keyword_text = keyword["keyword"]
                    keyword_norm = normalize(keyword_text)
                    
                    # Check direct match
                    if keyword_norm == text_norm:
                        confidence = self.config.get("confidence_weights", {}).get("exact_match", 1.0)
                        return (business_name, "exact_match", confidence)
                    
                    # Check spaced variants
                    keyword_variants = create_spaced_variants(keyword_norm)
                    for variant in keyword_variants:
                        if variant == text_norm:
                            confidence = self.config.get("confidence_weights", {}).get("exact_match", 1.0)
                            return (business_name, "exact_match", confidence)
        
        return None

    def _find_variant_match(self, text: str) -> Optional[Tuple[str, str, float]]:
        """Find variant matches (alternative names, OCR errors, abbreviations)."""
        def normalize(s: str) -> str:
            s = s.lower()
            s = unicodedata.normalize("NFKC", s)
            s = " ".join(s.split())
            return s
        
        def create_spaced_variants(s: str) -> List[str]:
            variants = [s]
            no_spaces = s.replace(" ", "")
            if no_spaces != s:
                variants.append(no_spaces)
            spaced = " ".join(no_spaces)
            if spaced != s:
                variants.append(spaced)
            return variants
        
        text_norm = normalize(text)
        
        for business in self.businesses.values():
            # Handle both old and new field names for backward compatibility
            business_name = business.get("business_name") or business.get("canonical_name", "")
            keywords = business.get("keywords") or business.get("aliases", [])
            
            for keyword in keywords:
                if keyword["match_type"] == "variant":
                    keyword_text = keyword["keyword"]
                    keyword_norm = normalize(keyword_text)
                    
                    # Check direct substring match
                    if keyword_norm in text_norm:
                        confidence = self.config.get("confidence_weights", {}).get("variant_match", 0.8)
                        return (business_name, "variant_match", confidence)
                    
                    # Check spaced variants
                    keyword_variants = create_spaced_variants(keyword_norm)
                    for variant in keyword_variants:
                        if variant in text_norm:
                            confidence = self.config.get("confidence_weights", {}).get("variant_match", 0.8)
                            return (business_name, "variant_match", confidence)
        
        return None

    def _find_fuzzy_match(self, text: str) -> Optional[Tuple[str, str, float]]:
        """Find fuzzy matches using indicators."""
        text_lower = text.lower()
        
        for business in self.businesses.values():
            indicators = business["indicators"]
            
            # Handle both old and new field names for backward compatibility
            business_name = business.get("business_name") or business.get("canonical_name", "")
            
            # Check if text contains any indicators
            if any(indicator.lower() in text_lower for indicator in indicators):
                # Try fuzzy matching against the business name
                match = FuzzyMatcher.fuzzy_match(
                    target=text, 
                    candidates=[business_name],
                    threshold=0.8
                )
                if match:
                    confidence = self.config.get("confidence_weights", {}).get("fuzzy_match", 0.6)
                    return (business_name, "fuzzy_match", confidence)
        
        return None

    def add_keyword(self, business_id: str, keyword: str, match_type: str = "exact") -> bool:
        """Add a keyword to a business."""
        if business_id not in self.businesses:
            return False
        
        business = self.businesses[business_id]
        
        # Handle both old and new field names for backward compatibility
        keywords = business.get("keywords") or business.get("aliases", [])
        
        # Check if keyword already exists
        for existing_keyword in keywords:
            if existing_keyword["keyword"] == keyword and existing_keyword["match_type"] == match_type:
                return False
        
        # Add new keyword
        new_keyword = {
            "keyword": keyword,
            "match_type": match_type,
            "case_sensitive": False,
            "fuzzy_matching": True
        }
        
        keywords.append(new_keyword)
        # Update the business with the new field name
        business["keywords"] = keywords
        business["metadata"]["updated"] = datetime.now().isoformat()
        
        self._save_config()
        return True

    def remove_keyword(self, business_id: str, keyword: str, match_type: str) -> bool:
        """Remove a keyword from a business."""
        if business_id not in self.businesses:
            return False
        
        business = self.businesses[business_id]
        
        # Handle both old and new field names for backward compatibility
        keywords = business.get("keywords") or business.get("aliases", [])
        
        # Find and remove the keyword
        for i, existing_keyword in enumerate(keywords):
            if existing_keyword["keyword"] == keyword and existing_keyword["match_type"] == match_type:
                del keywords[i]
                # Update the business with the new field name
                business["keywords"] = keywords
                business["metadata"]["updated"] = datetime.now().isoformat()
                self._save_config()
                return True
        
        return False

    def get_business_keywords(self, business_id: str) -> List[Dict[str, Any]]:
        """Get all keywords for a business."""
        if business_id not in self.businesses:
            return []
        
        business = self.businesses[business_id]
        # Handle both old and new field names for backward compatibility
        return business.get("keywords") or business.get("aliases", [])

    def get_all_businesses(self) -> List[Dict[str, Any]]:
        """Get all businesses."""
        return list(self.businesses.values())

    def get_business_by_id(self, business_id: str) -> Optional[Dict[str, Any]]:
        """Get a business by ID."""
        return self.businesses.get(business_id)

    def get_business_by_name(self, business_name: str) -> Optional[Dict[str, Any]]:
        """Get a business by business name."""
        for business in self.businesses.values():
            # Handle both old and new field names for backward compatibility
            current_business_name = business.get("business_name") or business.get("canonical_name", "")
            if current_business_name == business_name:
                return business
        return None

    def _save_config(self) -> None:
        """Save the configuration to file."""
        try:
            # Convert to v2 format for saving
            config_v2 = {
                "version": "2.0",
                "updated": datetime.now().isoformat(),
                "businesses": list(self.businesses.values()),
                "confidence_weights": self.config.get("confidence_weights", {
                    "exact_match": 1.0,
                    "variant_match": 0.8,
                    "fuzzy_match": 0.6
                }),
                "backup": self.config.get("backup", {})
            }
            
            with open(self.mapping_file, "w", encoding="utf-8") as f:
                json.dump(config_v2, f, indent=4, ensure_ascii=False)
                
        except Exception as e:
            print(f"Warning: Could not save mapping file {self.mapping_file}: {e}")

    def get_stats(self) -> Dict[str, int]:
        """Get statistics about the business mappings."""
        total_keywords = 0
        exact_keywords = 0
        variant_keywords = 0
        fuzzy_keywords = 0
        
        for business in self.businesses.values():
            # Handle both old and new field names for backward compatibility
            keywords = business.get("keywords") or business.get("aliases", [])
            total_keywords += len(keywords)
            exact_keywords += len([k for k in keywords if k["match_type"] == "exact"])
            variant_keywords += len([k for k in keywords if k["match_type"] == "variant"])
            fuzzy_keywords += len([k for k in keywords if k["match_type"] == "fuzzy"])
        
        total_indicators = sum(len(b["indicators"]) for b in self.businesses.values())
        
        return {
            "total_businesses": len(self.businesses),
            "total_keywords": total_keywords,
            "exact_keywords": exact_keywords,
            "variant_keywords": variant_keywords,
            "fuzzy_keywords": fuzzy_keywords,
            "total_indicators": total_indicators,
            "business_names": len(self.canonical_names)
        }

    def get_all_dropdown_names(self) -> List[str]:
        """Get all names for dropdown (business names + all keywords)."""
        names = list(self.canonical_names)
        
        # Add all keywords
        for business in self.businesses.values():
            # Handle both old and new field names for backward compatibility
            keywords = business.get("keywords") or business.get("aliases", [])
            for keyword in keywords:
                keyword_text = keyword["keyword"]
                if keyword_text not in names:
                    names.append(keyword_text)
        
        return sorted(names)

    def create_startup_backup(self) -> Optional[str]:
        """Create a backup of the business mappings on startup."""
        try:
            import shutil
            from datetime import datetime
            from pathlib import Path
            
            # Create backup directory
            backup_dir = Path(self.mapping_file).parent / "backups"
            backup_dir.mkdir(exist_ok=True)
            
            # Create backup filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"business_mappings_v2_startup_backup_{timestamp}.json"
            backup_file = str(backup_dir / backup_filename)
            
            # Copy the current file
            shutil.copy2(self.mapping_file, backup_file)
            
            print(f"✅ Startup backup created: {backup_filename}")
            
            # Clean up old backups if enabled
            if self.cleanup_on_startup:
                self.cleanup_old_backups(keep_count=self.max_backups_to_keep)
            
            return backup_file
        except Exception as e:
            print(f"Warning: Could not create startup backup: {e}")
            return None

    def create_shutdown_backup(self) -> Optional[str]:
        """Create a backup of the business mappings on shutdown."""
        try:
            import shutil
            from datetime import datetime
            from pathlib import Path
            
            # Create backup directory
            backup_dir = Path(self.mapping_file).parent / "backups"
            backup_dir.mkdir(exist_ok=True)
            
            # Create backup filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"business_mappings_v2_shutdown_backup_{timestamp}.json"
            backup_file = str(backup_dir / backup_filename)
            
            # Copy the current file
            shutil.copy2(self.mapping_file, backup_file)
            
            print(f"✅ Shutdown backup created: {backup_filename}")
            
            # Clean up old backups if enabled
            if self.cleanup_on_shutdown:
                self.cleanup_old_backups(keep_count=self.max_backups_to_keep)
            
            return backup_file
        except Exception as e:
            print(f"Warning: Could not create shutdown backup: {e}")
            return None

    def cleanup_old_backups(self, keep_count: int = 10) -> int:
        """
        Clean up old backup files, keeping only the most recent ones.
        
        Args:
            keep_count: Number of recent backups to keep (default: 10)
            
        Returns:
            Number of backup files deleted
        """
        try:
            import os
            from pathlib import Path
            import glob
            
            # Get the backup directory
            backup_dir = Path(self.mapping_file).parent / "backups"
            if not backup_dir.exists():
                return 0  # No backup directory, nothing to clean
            
            # Find all backup files (both startup and shutdown backups, plus manual backups)
            backup_patterns = [
                "business_mappings_v2_startup_backup_*.json",
                "business_mappings_v2_shutdown_backup_*.json",
                "business_mappings_backup_*.json"
            ]
            
            backup_files = []
            for pattern in backup_patterns:
                backup_files.extend(glob.glob(str(backup_dir / pattern)))
            
            if len(backup_files) <= keep_count:
                return 0  # No cleanup needed
            
            # Sort by modification time (oldest first)
            backup_files.sort(key=lambda x: os.path.getmtime(x))
            
            # Delete oldest files, keeping the most recent ones
            files_to_delete = backup_files[:-keep_count]
            deleted_count = 0
            
            for backup_file in files_to_delete:
                try:
                    os.remove(backup_file)
                    deleted_count += 1
                    print(f"🗑️ Deleted old backup: {os.path.basename(backup_file)}")
                except Exception as e:
                    print(f"Warning: Could not delete backup {backup_file}: {e}")
            
            if deleted_count > 0:
                print(f"✅ Cleaned up {deleted_count} old backup files, keeping {keep_count} recent ones")
            
            return deleted_count
            
        except Exception as e:
            print(f"Warning: Could not cleanup old backups: {e}")
            return 0

    def create_backup(self, backup_path: Optional[str] = None, auto_cleanup: bool = True) -> str:
        """
        Create a backup of the current business mappings configuration.
        
        Args:
            backup_path: Optional path for the backup file. If None, creates a timestamped file.
            auto_cleanup: Whether to automatically clean up old backups (default: True)
            
        Returns:
            Path to the created backup file
        """
        if backup_path is None:
            # Create timestamped backup filename with microsecond precision
            from datetime import datetime
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]  # Include milliseconds
            backup_dir = Path(self.mapping_file).parent / "backups"
            backup_dir.mkdir(exist_ok=True)
            backup_path = str(backup_dir / f"business_mappings_backup_{timestamp}.json")
        
        try:
            # Create backup with current configuration
            with open(backup_path, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            
            print(f"✅ Backup created successfully: {backup_path}")
            
            # Auto-cleanup old backups if enabled
            if auto_cleanup and self.auto_cleanup:
                self.cleanup_old_backups(keep_count=self.max_backups_to_keep)
            
            return backup_path
        except Exception as e:
            print(f"❌ Failed to create backup: {e}")
            raise

    def list_backups(self) -> List[str]:
        """
        List available backup files.
        
        Returns:
            List of backup file paths, sorted by creation time (newest first)
        """
        try:
            import os
            from pathlib import Path
            import glob
            
            backup_dir = Path(self.mapping_file).parent / "backups"
            if not backup_dir.exists():
                return []
            
            backup_files = []
            for file_path in backup_dir.glob("business_mappings_backup_*.json"):
                backup_files.append(str(file_path))
            
            # Sort by modification time (newest first)
            backup_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
            return backup_files
            
        except Exception as e:
            print(f"Warning: Could not list backups: {e}")
            return []

    def get_backup_info(self, backup_path: str) -> Optional[Dict]:
        """
        Get information about a backup file.
        
        Args:
            backup_path: Path to the backup file
            
        Returns:
            Dictionary with backup information or None if file not found
        """
        try:
            import os
            import json
            
            if not os.path.exists(backup_path):
                return None
            
            # Get file info
            stat = os.stat(backup_path)
            file_size = stat.st_size
            created_time = stat.st_ctime
            modified_time = stat.st_mtime
            
            # Load backup data to get counts
            with open(backup_path, "r", encoding="utf-8") as f:
                backup_data = json.load(f)
            
            # Extract counts from v2 format
            businesses = backup_data.get("businesses", [])
            total_keywords = sum(len(b.get("keywords", [])) for b in businesses)
            total_indicators = sum(len(b.get("indicators", [])) for b in businesses)
            
            return {
                "file_path": backup_path,
                "file_size": file_size,
                "created_time": created_time,
                "modified_time": modified_time,
                "businesses_count": len(businesses),
                "total_keywords": total_keywords,
                "total_indicators": total_indicators,
                # For compatibility with old format
                "official_names_count": len(businesses),
                "exact_matches_count": total_keywords,
                "partial_matches_count": 0,
                "fuzzy_candidates_count": total_indicators
            }
            
        except Exception as e:
            print(f"Warning: Could not get backup info: {e}")
            return None

    def restore_backup(self, backup_path: str) -> bool:
        """
        Restore business mappings from a backup file.
        
        Args:
            backup_path: Path to the backup file to restore from
            
        Returns:
            True if restore was successful, False otherwise
        """
        try:
            import os
            import json
            
            if not os.path.exists(backup_path):
                print(f"❌ Backup file not found: {backup_path}")
                return False
            
            # Load backup configuration
            with open(backup_path, "r", encoding="utf-8") as f:
                backup_config = json.load(f)
            
            # Create a backup of current configuration before restoring
            self.create_backup()
            
            # Restore configuration
            self.config = backup_config
            
            # Reload businesses from the restored config
            self._load_businesses()
            
            # Save restored configuration
            self._save_config()
            
            # Validate mappings after restore
            self._validate_mappings()
            
            print(f"✅ Backup restored successfully from: {backup_path}")
            return True
            
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON in backup file: {e}")
            return False
        except Exception as e:
            print(f"❌ Failed to restore backup: {e}")
            return False 