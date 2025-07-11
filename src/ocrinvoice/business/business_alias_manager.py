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
        def fuzzy_match(target: str, candidates: List[str], threshold: float = 0.3):
            # Simple fallback implementation
            for candidate in candidates:
                if (
                    target.lower() in candidate.lower()
                    or candidate.lower() in target.lower()
                ):
                    return candidate
            return None


class BusinessAliasManager:
    """
    Manages business name aliases and mappings for invoice OCR extraction.
    Supports exact matches, partial matches, and fuzzy matching with indicators.
    All outputs resolve to one of the official business names.
    """

    def __init__(self, alias_file: Optional[str] = None):
        """
        Initialize the BusinessAliasManager with an alias configuration file.

        Args:
            alias_file: Path to the JSON configuration file containing business aliases.
                       If None, will try to find the file using the same logic as the config system.
        """
        self.alias_file = self._resolve_alias_file_path(alias_file)
        self.config = self._load_config()

        # Load official business names
        self.official_names = set(self.config.get("official_names", []))
        if not self.official_names:
            print("Warning: No official business names defined in configuration.")

        # Validate that all alias mappings resolve to an official name
        self._validate_alias_mappings()

    def _resolve_alias_file_path(self, alias_file: Optional[str]) -> str:
        """
        Resolve the alias file path using the same logic as the config system.

        Args:
            alias_file: Explicit path to alias file, or None to auto-detect

        Returns:
            Resolved path to the alias file
        """
        if alias_file:
            return alias_file

        # Try multiple locations in order of preference
        possible_paths = [
            # From current working directory
            Path.cwd() / "config" / "business_aliases.json",
            # From project root (when running from source)
            Path(__file__).parent.parent.parent.parent
            / "config"
            / "business_aliases.json",
            # From installed package
            Path(__file__).parent.parent.parent / "config" / "business_aliases.json",
            # From user's home directory
            Path.home() / ".ocrinvoice" / "business_aliases.json",
        ]

        for path in possible_paths:
            if path.exists():
                return str(path)

        # If no file found, return the first path as default
        return str(possible_paths[0])

    def _load_config(self) -> Dict:
        """Load the business alias configuration from JSON file."""
        if not os.path.exists(self.alias_file):
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
            with open(self.alias_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Could not load alias file {self.alias_file}: {e}")
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

    def _validate_alias_mappings(self):
        """Validate that all alias mappings resolve to an official business name."""

        def check_name(name):
            if name not in self.official_names:
                print(f"Warning: Alias mapping '{name}' is not in official_names list.")

        # Check exact_matches
        for alias, business_name in self.config.get("exact_matches", {}).items():
            check_name(business_name)
        # Check partial_matches
        for alias, business_name in self.config.get("partial_matches", {}).items():
            check_name(business_name)
        # Check fuzzy_candidates
        for business_name in self.config.get("fuzzy_candidates", []):
            check_name(business_name)

    def get_official_names(self):
        """Return the list of official business names."""
        return sorted(self.official_names)

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
        print(f"[DEBUG] BusinessAliasManager: Searching for business matches in text")
        print(f"[DEBUG] BusinessAliasManager: Text sample (first 200 chars): {text_normalized[:200]}")

        # 1. Exact matches (highest priority)
        exact_match = self._find_exact_match(text_normalized)
        if exact_match:
            business_name, match_type, confidence = exact_match
            print(f"[DEBUG] BusinessAliasManager: Found exact match: '{business_name}'")
            return (business_name, match_type, confidence)

        # 2. Partial matches (medium priority)
        partial_match = self._find_partial_match(text_normalized)
        if partial_match:
            business_name, match_type, confidence = partial_match
            print(f"[DEBUG] BusinessAliasManager: Found partial match: '{business_name}'")
            return (business_name, match_type, confidence)

        # 3. Fuzzy matches (lowest priority, requires indicators)
        fuzzy_match = self._find_fuzzy_match(text_normalized)
        if fuzzy_match:
            business_name, match_type, confidence = fuzzy_match
            print(f"[DEBUG] BusinessAliasManager: Found fuzzy match: '{business_name}'")
            return (business_name, match_type, confidence)

        print(f"[DEBUG] BusinessAliasManager: No matches found")
        return None

    def _find_exact_match(self, text: str) -> Optional[Tuple[str, str, float]]:
        """Find exact string matches (case-insensitive)."""
        exact_matches = self.config.get("exact_matches", {})

        for alias, business_name in exact_matches.items():
            # Compare both strings in lowercase for case-insensitive matching
            if text == alias.lower():
                confidence = self.config.get("confidence_weights", {}).get(
                    "exact_match", 1.0
                )
                return (business_name, "exact_match", confidence)

        return None

    def _find_partial_match(self, text: str) -> Optional[Tuple[str, str, float]]:
        """Find partial substring matches (case-insensitive, robust to whitespace and Unicode)."""
        import unicodedata
        def normalize(s):
            # Lowercase, strip, normalize unicode, collapse whitespace
            s = s.lower()
            s = unicodedata.normalize('NFKC', s)
            s = ' '.join(s.split())
            return s

        partial_matches = self.config.get("partial_matches", {})
        print(f"[DEBUG] BusinessAliasManager: Checking partial matches...")
        print(f"[DEBUG] BusinessAliasManager: Available partial matches: {list(partial_matches.keys())}")
        print(f"[DEBUG] BusinessAliasManager: Text repr: {repr(text)}")
        text_norm = normalize(text)
        print(f"[DEBUG] BusinessAliasManager: Normalized text: {repr(text_norm)}")

        for alias, business_name in partial_matches.items():
            alias_norm = normalize(alias)
            print(f"[DEBUG] BusinessAliasManager: Checking if alias '{alias}' (norm: '{alias_norm}') is in text (norm)...")
            if alias_norm in text_norm:
                print(f"[DEBUG] BusinessAliasManager: Found partial match! '{alias_norm}' is in text (norm)")
                confidence = self.config.get("confidence_weights", {}).get(
                    "partial_match", 0.8
                )
                return (business_name, "partial_match", confidence)

        print(f"[DEBUG] BusinessAliasManager: No partial matches found")
        return None

    def _find_fuzzy_match(self, text: str) -> Optional[Tuple[str, str, float]]:
        """Find fuzzy matches using indicators and similarity algorithms (case-insensitive)."""
        fuzzy_candidates = self.config.get("fuzzy_candidates", [])
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

    def add_alias(
        self, alias: str, business_name: str, match_type: str = "exact_matches"
    ):
        """
        Add a new alias to the configuration.

        Args:
            alias: The alias string to match
            business_name: The canonical business name
            match_type: Type of match ("exact_matches" or "partial_matches")
        """
        if match_type in self.config:
            self.config[match_type][alias] = business_name
            self._save_config()

    def _save_config(self):
        """Save the current configuration back to the JSON file."""
        try:
            with open(self.alias_file, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
        except IOError as e:
            print(f"Warning: Could not save alias file {self.alias_file}: {e}")

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

    def get_stats(self) -> Dict:
        """Get statistics about the alias configuration."""
        return {
            "exact_matches": len(self.config.get("exact_matches", {})),
            "partial_matches": len(self.config.get("partial_matches", {})),
            "fuzzy_candidates": len(self.config.get("fuzzy_candidates", [])),
            "total_businesses": len(self.get_all_business_names()),
            "official_names": len(self.official_names),
        }
