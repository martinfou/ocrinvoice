import json
import os
from typing import Optional, Tuple, Dict, List
from pathlib import Path

# Import FuzzyMatcher from the utils module
try:
    from ocrinvoice.utils.fuzzy_matcher import FuzzyMatcher
except ImportError:
    # Fallback if import fails - create a simple FuzzyMatcher
    class FuzzyMatcher:
        @staticmethod
        def fuzzy_match(
            target: str, candidates: List[str], threshold: float = 0.3
        ) -> Optional[str]:
            # Simple fallback implementation
            for candidate in candidates:
                if (
                    target.lower() in candidate.lower()
                    or candidate.lower() in target.lower()
                ):
                    return candidate
            return None


class BusinessMappingManager:
    """
    Manages business name mappings for invoice OCR extraction.
    Supports exact matches, partial matches, and fuzzy matching with indicators.
    All outputs resolve to one of the official business names.
    """

    def __init__(self, mapping_file: Optional[str] = None):
        """
        Initialize the BusinessMappingManager with a mapping configuration file.

        Args:
            mapping_file: Path to the JSON configuration file containing business mappings.
                       If None, will try to find the file using the same logic as the config system.
        """
        self.mapping_file = self._resolve_mapping_file_path(mapping_file)
        self.config = self._load_config()

        # Load official business names
        self.official_names = set(self.config.get("official_names", []))
        if not self.official_names:
            print("Warning: No official business names defined in configuration.")

        # Validate that all mappings resolve to an official name
        self._validate_mappings()

    def _resolve_mapping_file_path(self, mapping_file: Optional[str]) -> str:
        """
        Resolve the mapping file path using the same logic as the config system.

        Args:
            mapping_file: Explicit path to mapping file, or None to auto-detect

        Returns:
            Resolved path to the mapping file
        """
        if mapping_file:
            return mapping_file

        # Try multiple locations in order of preference
        possible_paths = [
            # From current working directory
            Path.cwd() / "config" / "business_mappings.json",
            # From project root (when running from source)
            Path(__file__).parent.parent.parent.parent
            / "config"
            / "business_mappings.json",
            # From installed package
            Path(__file__).parent.parent.parent / "config" / "business_mappings.json",
            # From user's home directory
            Path.home() / ".ocrinvoice" / "business_mappings.json",
        ]

        for path in possible_paths:
            if path.exists():
                return str(path)

        # If no file found, return the first path as default
        return str(possible_paths[0])

    def _load_config(self) -> Dict[str, any]:
        """Load the business mapping configuration from JSON file."""
        if not os.path.exists(self.mapping_file):
            # Return default empty config if file doesn't exist
            return {
                "official_names": [],
                "exact_matches": {},
                "partial_matches": {},
                "fuzzy_candidates": [],
                "indicators": {},
                "confidence_weights": {
                    "exact_match": 1.0,
                    "partial_match": 0.8,
                    "fuzzy_match": 0.6,
                },
            }

        try:
            with open(self.mapping_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Could not load mapping file {self.mapping_file}: {e}")
            # Return default config instead of recursive call
            return {
                "official_names": [],
                "exact_matches": {},
                "partial_matches": {},
                "fuzzy_candidates": [],
                "indicators": {},
                "confidence_weights": {
                    "exact_match": 1.0,
                    "partial_match": 0.8,
                    "fuzzy_match": 0.6,
                },
            }

    def _validate_mappings(self) -> None:
        """Validate that all mappings resolve to an official business name."""

        def check_name(name: str) -> None:
            if name not in self.official_names:
                print(f"Warning: Mapping '{name}' is not in official_names list.")

        # Check exact_matches
        for mapping, business_name in self.config.get("exact_matches", {}).items():
            check_name(business_name)
        # Check partial_matches
        for mapping, business_name in self.config.get("partial_matches", {}).items():
            check_name(business_name)
        # Check fuzzy_candidates
        for business_name in self.config.get("fuzzy_candidates", []):
            check_name(business_name)

    def get_official_names(self) -> List[str]:
        """Return the list of official business names."""
        return sorted(list(self.official_names))

    def add_official_name(self, name: str) -> bool:
        """
        Add a new official business name.

        Args:
            name: The official business name to add

        Returns:
            True if added successfully, False if already exists
        """
        if name not in self.official_names:
            self.official_names.add(name)
            self.config["official_names"] = list(self.official_names)
            self._save_config()
            return True
        return False

    def remove_official_name(self, name: str) -> bool:
        """
        Remove an official business name.

        Args:
            name: The official business name to remove

        Returns:
            True if removed successfully, False if not found
        """
        if name in self.official_names:
            self.official_names.remove(name)
            self.config["official_names"] = list(self.official_names)
            self._save_config()
            return True
        return False

    def update_official_name(self, old_name: str, new_name: str) -> bool:
        """
        Update an official business name.

        Args:
            old_name: The current official business name
            new_name: The new official business name

        Returns:
            True if updated successfully, False if old name not found or new name already exists
        """
        if old_name not in self.official_names:
            return False
        if new_name in self.official_names and new_name != old_name:
            return False

        # Remove old name and add new name
        self.official_names.remove(old_name)
        self.official_names.add(new_name)
        self.config["official_names"] = list(self.official_names)

        # Update all mappings that reference the old name
        exact_matches = self.config.get("exact_matches", {})
        for alias, canonical in exact_matches.items():
            if canonical == old_name:
                exact_matches[alias] = new_name

        partial_matches = self.config.get("partial_matches", {})
        for alias, canonical in partial_matches.items():
            if canonical == old_name:
                partial_matches[alias] = new_name

        # Update fuzzy candidates
        fuzzy_candidates = self.config.get("fuzzy_candidates", [])
        if old_name in fuzzy_candidates:
            fuzzy_candidates.remove(old_name)
            fuzzy_candidates.append(new_name)

        # Update indicators
        indicators = self.config.get("indicators", {})
        if old_name in indicators:
            indicators[new_name] = indicators.pop(old_name)

        self._save_config()
        return True

    def is_official_name(self, name: str) -> bool:
        """Check if a name is in the official business names list (case-insensitive)."""
        if not name:
            return False
        # Normalize both the input name and official names to lowercase for case-insensitive comparison
        name_normalized = name.lower()
        official_names_normalized = {
            official.lower() for official in self.official_names
        }
        return name_normalized in official_names_normalized

    def find_business_match(self, text: str) -> Optional[Tuple[str, str, float]]:
        """
        Find a business match using exact, partial, or fuzzy matching.
        Returns the official business name.

        Args:
            text: The text to search for business names

        Returns:
            Tuple of (official_business_name, match_type, confidence) or None if no match
        """
        if not text or not isinstance(text, str):
            return None

        # Normalize text to lowercase for case-insensitive comparison
        text_normalized = text.lower().strip()
        print("[DEBUG] BusinessMappingManager: Searching for business matches in text")
        print(
            f"[DEBUG] BusinessMappingManager: Text sample (first 200 chars): {text_normalized[:200]}"
        )

        # 1. Exact matches (highest priority)
        exact_match = self._find_exact_match(text_normalized)
        if exact_match:
            business_name, match_type, confidence = exact_match
            print(
                f"[DEBUG] BusinessMappingManager: Found exact match: '{business_name}'"
            )
            return (business_name, match_type, confidence)

        # 2. Partial matches (medium priority)
        partial_match = self._find_partial_match(text_normalized)
        if partial_match:
            business_name, match_type, confidence = partial_match
            print(
                f"[DEBUG] BusinessMappingManager: Found partial match: '{business_name}'"
            )
            return (business_name, match_type, confidence)

        # 3. Fuzzy matches (lowest priority, requires indicators)
        fuzzy_match = self._find_fuzzy_match(text_normalized)
        if fuzzy_match:
            business_name, match_type, confidence = fuzzy_match
            print(
                f"[DEBUG] BusinessMappingManager: Found fuzzy match: '{business_name}'"
            )
            return (business_name, match_type, confidence)

        print("[DEBUG] BusinessMappingManager: No matches found")
        return None

    def _find_exact_match(self, text: str) -> Optional[Tuple[str, str, float]]:
        """Find exact string matches (case-insensitive, substring detection)."""
        exact_matches = self.config.get("exact_matches", {})

        # Normalize the input text (simple lowercase and whitespace normalization)
        text_norm = text.lower().strip()

        for mapping, business_name in exact_matches.items():
            # Check if the exact match string is found anywhere in the normalized text
            if mapping.lower() in text_norm:
                confidence = self.config.get("confidence_weights", {}).get(
                    "exact_match", 1.0
                )
                return (business_name, "exact_match", confidence)

        return None

    def _find_partial_match(self, text: str) -> Optional[Tuple[str, str, float]]:
        """Find partial substring matches (case-insensitive, robust to whitespace and Unicode)."""
        import unicodedata

        def normalize(s: str) -> str:
            # Lowercase, strip, normalize unicode, collapse whitespace
            s = s.lower()
            s = unicodedata.normalize("NFKC", s)
            s = " ".join(s.split())
            return s

        partial_matches = self.config.get("partial_matches", {})
        print("[DEBUG] BusinessMappingManager: Checking partial matches...")
        print(
            f"[DEBUG] BusinessMappingManager: Available partial matches: {list(partial_matches.keys())}"
        )
        print(f"[DEBUG] BusinessMappingManager: Text repr: {repr(text)}")
        text_norm = normalize(text)
        print(f"[DEBUG] BusinessMappingManager: Normalized text: {repr(text_norm)}")

        for mapping, business_name in partial_matches.items():
            mapping_norm = normalize(mapping)
            print(
                f"[DEBUG] BusinessMappingManager: Checking if mapping '{mapping}' (norm: '{mapping_norm}') is in text (norm)..."
            )
            if mapping_norm in text_norm:
                print(
                    f"[DEBUG] BusinessMappingManager: Found partial match! '{mapping_norm}' is in text (norm)"
                )
                confidence = self.config.get("confidence_weights", {}).get(
                    "partial_match", 0.8
                )
                return (business_name, "partial_match", confidence)

        print("[DEBUG] BusinessMappingManager: No partial matches found")
        return None

    def _find_fuzzy_match(self, text: str) -> Optional[Tuple[str, str, float]]:
        """Find fuzzy matches using indicators and similarity algorithms (case-insensitive)."""
        indicators = self.config.get("indicators", {})

        # Check if text contains indicators for any business (case-insensitive)
        for business_name, required_indicators in indicators.items():
            # Check if any indicator is in the normalized text
            if any(indicator.lower() in text for indicator in required_indicators):
                # Try fuzzy matching against this business
                match = FuzzyMatcher.fuzzy_match(
                    target=text, candidates=[business_name], threshold=0.8
                )
                if match:
                    confidence = self.config.get("confidence_weights", {}).get(
                        "fuzzy_match", 0.6
                    )
                    return (business_name, "fuzzy_match", confidence)

        return None

    def add_mapping(
        self, mapping: str, business_name: str, match_type: str = "exact_matches"
    ) -> None:
        """
        Add a new mapping to the configuration.

        Args:
            mapping: The mapping string to match
            business_name: The canonical business name
            match_type: Type of match ("exact_matches" or "partial_matches")
        """
        if match_type in self.config:
            self.config[match_type][mapping] = business_name
            self._save_config()

    def _save_config(self) -> None:
        """Save the current configuration back to the JSON file."""
        try:
            with open(self.mapping_file, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
        except IOError as e:
            print(f"Warning: Could not save mapping file {self.mapping_file}: {e}")

    def reload_config(self) -> None:
        """Reload the configuration from the JSON file."""
        self.config = self._load_config()
        # Reload official business names
        self.official_names = set(self.config.get("official_names", []))
        # Validate mappings
        self._validate_mappings()

    def get_all_business_names(self) -> List[str]:
        """Get all unique business names from the configuration."""
        business_names = set()

        # From exact matches
        business_names.update(self.config.get("exact_matches", {}).values())

        # From partial matches
        business_names.update(self.config.get("partial_matches", {}).values())

        # From fuzzy candidates
        business_names.update(self.config.get("fuzzy_candidates", []))

        return sorted(list(business_names))

    def get_stats(self) -> Dict[str, int]:
        """Get statistics about the mapping configuration."""
        return {
            "exact_matches": len(self.config.get("exact_matches", {})),
            "partial_matches": len(self.config.get("partial_matches", {})),
            "fuzzy_candidates": len(self.config.get("fuzzy_candidates", [])),
            "total_businesses": len(self.get_all_business_names()),
            "official_names": len(self.official_names),
        }

    def create_backup(
        self, backup_path: Optional[str] = None, auto_cleanup: bool = True
    ) -> str:
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

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[
                :-3
            ]  # Include milliseconds
            backup_dir = Path(self.mapping_file).parent / "backups"
            backup_dir.mkdir(exist_ok=True)
            backup_path = str(backup_dir / f"business_mappings_backup_{timestamp}.json")

        try:
            # Create backup with current configuration
            with open(backup_path, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)

            print(f"✅ Backup created successfully: {backup_path}")

            # Auto-cleanup old backups if enabled
            if auto_cleanup:
                self.cleanup_old_backups(keep_count=10)

            return backup_path
        except Exception as e:
            print(f"❌ Failed to create backup: {e}")
            raise

    def restore_backup(self, backup_path: str) -> bool:
        """
        Restore business mappings from a backup file.

        Args:
            backup_path: Path to the backup file to restore from

        Returns:
            True if restore was successful, False otherwise
        """
        if not os.path.exists(backup_path):
            print(f"❌ Backup file not found: {backup_path}")
            return False

        try:
            # Load backup configuration
            with open(backup_path, "r", encoding="utf-8") as f:
                backup_config = json.load(f)

            # Validate backup structure
            required_keys = [
                "official_names",
                "exact_matches",
                "partial_matches",
                "fuzzy_candidates",
            ]
            for key in required_keys:
                if key not in backup_config:
                    print(f"❌ Invalid backup file: missing '{key}' key")
                    return False

            # Create a backup of current configuration before restoring
            self.create_backup()

            # Restore configuration
            self.config = backup_config
            self.official_names = set(self.config.get("official_names", []))

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

    def list_backups(self) -> List[str]:
        """
        List available backup files.

        Returns:
            List of backup file paths, sorted by creation time (newest first)
        """
        backup_dir = Path(self.mapping_file).parent / "backups"
        if not backup_dir.exists():
            return []

        backup_files = []
        for file_path in backup_dir.glob("business_mappings_backup_*.json"):
            backup_files.append(str(file_path))

        # Sort by modification time (newest first)
        backup_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        return backup_files

    def get_backup_info(self, backup_path: str) -> Optional[Dict]:
        """
        Get information about a backup file.

        Args:
            backup_path: Path to the backup file

        Returns:
            Dictionary with backup information or None if file not found
        """
        if not os.path.exists(backup_path):
            return None

        try:
            with open(backup_path, "r", encoding="utf-8") as f:
                backup_config = json.load(f)

            return {
                "file_path": backup_path,
                "file_size": os.path.getsize(backup_path),
                "created_time": os.path.getctime(backup_path),
                "modified_time": os.path.getmtime(backup_path),
                "official_names_count": len(backup_config.get("official_names", [])),
                "exact_matches_count": len(backup_config.get("exact_matches", {})),
                "partial_matches_count": len(backup_config.get("partial_matches", {})),
                "fuzzy_candidates_count": len(
                    backup_config.get("fuzzy_candidates", [])
                ),
            }
        except Exception as e:
            print(f"❌ Failed to read backup info: {e}")
            return None

    def cleanup_old_backups(self, keep_count: int = 10) -> int:
        """
        Clean up old backup files, keeping only the specified number of most recent ones.

        Args:
            keep_count: Number of most recent backups to keep (default: 10)

        Returns:
            Number of backup files deleted
        """
        backup_files = self.list_backups()

        if len(backup_files) <= keep_count:
            return 0  # No cleanup needed

        # Sort by modification time (oldest first)
        backup_files.sort(key=lambda x: os.path.getmtime(x))

        # Files to delete (oldest ones)
        files_to_delete = backup_files[:-keep_count]

        deleted_count = 0
        for backup_path in files_to_delete:
            try:
                os.remove(backup_path)
                deleted_count += 1
                print(f"🗑️ Deleted old backup: {os.path.basename(backup_path)}")
            except Exception as e:
                print(f"❌ Failed to delete backup {backup_path}: {e}")

        if deleted_count > 0:
            print(
                f"✅ Cleaned up {deleted_count} old backup files, keeping {keep_count} most recent"
            )

        return deleted_count

    def create_startup_backup(self) -> Optional[str]:
        """
        Create a backup on application startup.

        Returns:
            Path to the created backup file, or None if failed
        """
        try:
            backup_path = self.create_backup()
            print(f"✅ Startup backup created: {os.path.basename(backup_path)}")

            # Clean up old backups after creating new one
            self.cleanup_old_backups(keep_count=10)

            return backup_path
        except Exception as e:
            print(f"❌ Failed to create startup backup: {e}")
            return None

    def create_shutdown_backup(self) -> Optional[str]:
        """
        Create a backup on application shutdown.

        Returns:
            Path to the created backup file, or None if failed
        """
        try:
            backup_path = self.create_backup()
            print(f"✅ Shutdown backup created: {os.path.basename(backup_path)}")

            # Clean up old backups after creating new one
            self.cleanup_old_backups(keep_count=10)

            return backup_path
        except Exception as e:
            print(f"❌ Failed to create shutdown backup: {e}")
            return None
