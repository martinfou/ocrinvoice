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
    All outputs resolve to one of the canonical business names.
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

        # Load business names
        self.business_names = set(self.config.get("business_names", []))
        if not self.business_names:
            print("Warning: No business names defined in configuration.")

        # Validate that all mappings resolve to a business name
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
                "business_names": [],
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
                config = json.load(f)

            # Migrate from old "official_names" to "business_names" if needed
            if "official_names" in config and "business_names" not in config:
                config["business_names"] = config.pop("official_names")
                print("Migrated 'official_names' to 'business_names' in configuration")
                # Save the migrated config
                with open(self.mapping_file, "w", encoding="utf-8") as f:
                    json.dump(config, f, indent=4, ensure_ascii=False)
            
            # Migrate from old "canonical_names" to "business_names" if needed
            if "canonical_names" in config and "business_names" not in config:
                config["business_names"] = config.pop("canonical_names")
                print("Migrated 'canonical_names' to 'business_names' in configuration")
                # Save the migrated config
                with open(self.mapping_file, "w", encoding="utf-8") as f:
                    json.dump(config, f, indent=4, ensure_ascii=False)

            return config
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Could not load mapping file {self.mapping_file}: {e}")
            # Return default config instead of recursive call
            return {
                "business_names": [],
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
        """Validate that all mappings resolve to a business name."""

        def check_name(name: str) -> None:
            if name not in self.business_names:
                print(f"Warning: Mapping '{name}' is not in business_names list.")

        # Check exact_matches
        for mapping, business_name in self.config.get("exact_matches", {}).items():
            check_name(business_name)
        # Check partial_matches
        for mapping, business_name in self.config.get("partial_matches", {}).items():
            check_name(business_name)
        # Check fuzzy_candidates
        for business_name in self.config.get("fuzzy_candidates", []):
            check_name(business_name)

    def get_business_names(self) -> List[str]:
        """Return the list of business names."""
        return sorted(list(self.business_names))

    def add_business_name(self, name: str) -> bool:
        """
        Add a new business name.

        Args:
            name: The business name to add

        Returns:
            True if added successfully, False if already exists
        """
        if name not in self.business_names:
            self.business_names.add(name)
            # Preserve order by appending to the existing list instead of converting set to list
            if "business_names" not in self.config:
                self.config["business_names"] = []
            if name not in self.config["business_names"]:
                self.config["business_names"].append(name)
            self._save_config()
            return True
        return False

    def remove_business_name(self, name: str) -> bool:
        """
        Remove a business name.

        Args:
            name: The business name to remove

        Returns:
            True if removed successfully, False if not found
        """
        if name in self.business_names:
            self.business_names.remove(name)
            # Remove from the list while preserving order
            if "business_names" in self.config and name in self.config["business_names"]:
                self.config["business_names"].remove(name)
            self._save_config()
            return True
        return False

    def update_business_name(self, old_name: str, new_name: str) -> bool:
        """
        Update a business name.

        Args:
            old_name: The current business name
            new_name: The new business name

        Returns:
            True if updated successfully, False if old name not found or new name already exists
        """
        if old_name not in self.business_names:
            return False
        if new_name in self.business_names and new_name != old_name:
            return False

        # Remove old name and add new name
        self.business_names.remove(old_name)
        self.business_names.add(new_name)
        # Update the list while preserving order
        if "business_names" in self.config and old_name in self.config["business_names"]:
            old_index = self.config["business_names"].index(old_name)
            self.config["business_names"][old_index] = new_name

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

    def is_business_name(self, name: str) -> bool:
        """Check if a name is in the business names list (case-insensitive)."""
        if not name:
            return False
        # Normalize both the input name and business names to lowercase for case-insensitive comparison
        name_normalized = name.lower()
        business_names_normalized = {
            business.lower() for business in self.business_names
        }
        return name_normalized in business_names_normalized

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

        def create_spaced_variants(s: str) -> List[str]:
            """Create variants of a string with different spacing patterns for OCR artifacts."""
            variants = [s]
            # Remove all spaces
            no_spaces = s.replace(" ", "")
            if no_spaces != s:
                variants.append(no_spaces)
            # Add spaces between each character (OCR artifact)
            spaced = " ".join(no_spaces)
            if spaced != s:
                variants.append(spaced)
            return variants

        for mapping, business_name in exact_matches.items():
            mapping_lower = mapping.lower()
            
            # Check direct match
            if mapping_lower in text_norm:
                confidence = self.config.get("confidence_weights", {}).get(
                    "exact_match", 1.0
                )
                return (business_name, "exact_match", confidence)
            
            # Check spaced variants for OCR artifacts
            mapping_variants = create_spaced_variants(mapping_lower)
            for variant in mapping_variants:
                if variant in text_norm:
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

        def create_spaced_variants(s: str) -> List[str]:
            """Create variants of a string with different spacing patterns for OCR artifacts."""
            variants = [s]
            # Remove all spaces
            no_spaces = s.replace(" ", "")
            if no_spaces != s:
                variants.append(no_spaces)
            # Add spaces between each character (OCR artifact)
            spaced = " ".join(no_spaces)
            if spaced != s:
                variants.append(spaced)
            return variants

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
            
            # Check direct match
            if mapping_norm in text_norm:
                print(
                    f"[DEBUG] BusinessMappingManager: Found partial match! '{mapping_norm}' is in text (norm)"
                )
                confidence = self.config.get("confidence_weights", {}).get(
                    "partial_match", 0.8
                )
                return (business_name, "partial_match", confidence)
            
            # Check spaced variants for OCR artifacts
            mapping_variants = create_spaced_variants(mapping_norm)
            for variant in mapping_variants:
                if variant in text_norm:
                    print(
                        f"[DEBUG] BusinessMappingManager: Found partial match with variant! '{variant}' (from '{mapping_norm}') is in text (norm)"
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
        # Reload canonical business names
        self.canonical_names = set(self.config.get("canonical_names", []))
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

    def get_all_dropdown_names(self) -> List[str]:
        """Get all names that should be available in dropdown (business names + keywords)."""
        dropdown_names = set()

        # Add business names
        dropdown_names.update(self.business_names)

        # Add all mapping keys (keywords)
        dropdown_names.update(self.config.get("exact_matches", {}).keys())
        dropdown_names.update(self.config.get("partial_matches", {}).keys())

        return sorted(list(dropdown_names))

    def get_stats(self) -> Dict[str, int]:
        """Get statistics about the mapping configuration."""
        return {
            "exact_matches": len(self.config.get("exact_matches", {})),
            "partial_matches": len(self.config.get("partial_matches", {})),
            "fuzzy_candidates": len(self.config.get("fuzzy_candidates", [])),
            "total_businesses": len(self.get_all_business_names()),
            "business_names": len(self.business_names),
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
