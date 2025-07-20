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
        self.config = self._load_config()
        self.version = self.config.get("version", "1.0")
        
        # Initialize data structures
        self.businesses = {}  # business_id -> business_data
        self.canonical_names = set()
        self._load_businesses()
        
        # Validate mappings
        self._validate_mappings()

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
        return {
            "version": "2.0",
            "created": datetime.now().isoformat(),
            "businesses": [],
                    "confidence_weights": {
            "exact_match": 1.0,
            "variant_match": 0.8,
            "fuzzy_match": 0.6
        }
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
            canonical_name = business["canonical_name"]
            
            self.businesses[business_id] = business
            self.canonical_names.add(canonical_name)

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
                "canonical_name": canonical_name,
                "aliases": aliases,
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
        """Validate the business mappings."""
        if not self.businesses:
            print("Warning: No businesses found in configuration")
            return
        
        # Check for duplicate business IDs
        business_ids = [b["id"] for b in self.businesses.values()]
        if len(business_ids) != len(set(business_ids)):
            print("Warning: Duplicate business IDs found")
        
        # Check for duplicate canonical names
        canonical_names = [b["canonical_name"] for b in self.businesses.values()]
        if len(canonical_names) != len(set(canonical_names)):
            print("Warning: Duplicate canonical names found")

    def get_canonical_names(self) -> List[str]:
        """Get all canonical business names."""
        return sorted(list(self.canonical_names))

    def add_canonical_name(self, name: str) -> bool:
        """Add a new canonical business name."""
        if name in self.canonical_names:
            return False
        
        business_id = self._generate_business_id(name)
        
        # Check if ID already exists
        if business_id in self.businesses:
            # Make ID unique
            counter = 1
            while f"{business_id}-{counter}" in self.businesses:
                counter += 1
            business_id = f"{business_id}-{counter}"
        
        business_entry = {
            "id": business_id,
            "canonical_name": name,
            "aliases": [],
            "indicators": [],
            "metadata": {
                "created": datetime.now().isoformat(),
                "added_via_gui": True
            }
        }
        
        self.businesses[business_id] = business_entry
        self.canonical_names.add(name)
        
        self._save_config()
        return True

    def remove_canonical_name(self, name: str) -> bool:
        """Remove a canonical business name."""
        if name not in self.canonical_names:
            return False
        
        # Find and remove the business
        business_id = None
        for bid, business in self.businesses.items():
            if business["canonical_name"] == name:
                business_id = bid
                break
        
        if business_id:
            del self.businesses[business_id]
            self.canonical_names.remove(name)
            self._save_config()
            return True
        
        return False

    def update_canonical_name(self, old_name: str, new_name: str) -> bool:
        """Update a canonical business name."""
        if old_name not in self.canonical_names:
            return False
        
        if new_name in self.canonical_names and new_name != old_name:
            return False
        
        # Find and update the business
        for business in self.businesses.values():
            if business["canonical_name"] == old_name:
                business["canonical_name"] = new_name
                business["id"] = self._generate_business_id(new_name)
                business["metadata"]["updated"] = datetime.now().isoformat()
                
                self.canonical_names.remove(old_name)
                self.canonical_names.add(new_name)
                
                self._save_config()
                return True
        
        return False

    def is_canonical_name(self, name: str) -> bool:
        """Check if a name is a canonical business name."""
        return name in self.canonical_names

    def find_business_match(self, text: str) -> Optional[Tuple[str, str, float]]:
        """
        Find a business match for the given text.
        
        Returns:
            Tuple of (business_name, match_type, confidence) or None if no match
        """
        if not text or not text.strip():
            return None
        
        # Try exact match first
        match = self._find_exact_match(text)
        if match:
            return match
        
        # Try variant match
        match = self._find_variant_match(text)
        if match:
            return match
        
        # Try fuzzy match
        match = self._find_fuzzy_match(text)
        if match:
            return match
        
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
            for alias in business["aliases"]:
                if alias["match_type"] == "exact":
                    keyword = alias["keyword"]
                    keyword_norm = normalize(keyword)
                    
                    # Check direct match
                    if keyword_norm == text_norm:
                        confidence = self.config.get("confidence_weights", {}).get("exact_match", 1.0)
                        return (business["canonical_name"], "exact_match", confidence)
                    
                    # Check spaced variants
                    keyword_variants = create_spaced_variants(keyword_norm)
                    for variant in keyword_variants:
                        if variant == text_norm:
                            confidence = self.config.get("confidence_weights", {}).get("exact_match", 1.0)
                            return (business["canonical_name"], "exact_match", confidence)
        
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
            for alias in business["aliases"]:
                if alias["match_type"] == "variant":
                    keyword = alias["keyword"]
                    keyword_norm = normalize(keyword)
                    
                    # Check direct substring match
                    if keyword_norm in text_norm:
                        confidence = self.config.get("confidence_weights", {}).get("variant_match", 0.8)
                        return (business["canonical_name"], "variant_match", confidence)
                    
                    # Check spaced variants
                    keyword_variants = create_spaced_variants(keyword_norm)
                    for variant in keyword_variants:
                        if variant in text_norm:
                            confidence = self.config.get("confidence_weights", {}).get("variant_match", 0.8)
                            return (business["canonical_name"], "variant_match", confidence)
        
        return None

    def _find_fuzzy_match(self, text: str) -> Optional[Tuple[str, str, float]]:
        """Find fuzzy matches using indicators."""
        text_lower = text.lower()
        
        for business in self.businesses.values():
            indicators = business["indicators"]
            
            # Check if text contains any indicators
            if any(indicator.lower() in text_lower for indicator in indicators):
                # Try fuzzy matching against the canonical name
                match = FuzzyMatcher.fuzzy_match(
                    target=text, 
                    candidates=[business["canonical_name"]], 
                    threshold=0.8
                )
                if match:
                    confidence = self.config.get("confidence_weights", {}).get("fuzzy_match", 0.6)
                    return (business["canonical_name"], "fuzzy_match", confidence)
        
        return None

    def add_alias(self, business_id: str, keyword: str, match_type: str = "exact") -> bool:
        """Add an alias to a business."""
        if business_id not in self.businesses:
            return False
        
        business = self.businesses[business_id]
        
        # Check if alias already exists
        for alias in business["aliases"]:
            if alias["keyword"] == keyword and alias["match_type"] == match_type:
                return False
        
        # Add new alias
        new_alias = {
            "keyword": keyword,
            "match_type": match_type,
            "case_sensitive": False,
            "fuzzy_matching": True
        }
        
        business["aliases"].append(new_alias)
        business["metadata"]["updated"] = datetime.now().isoformat()
        
        self._save_config()
        return True

    def remove_alias(self, business_id: str, keyword: str, match_type: str) -> bool:
        """Remove an alias from a business."""
        if business_id not in self.businesses:
            return False
        
        business = self.businesses[business_id]
        
        # Find and remove the alias
        for i, alias in enumerate(business["aliases"]):
            if alias["keyword"] == keyword and alias["match_type"] == match_type:
                del business["aliases"][i]
                business["metadata"]["updated"] = datetime.now().isoformat()
                self._save_config()
                return True
        
        return False

    def get_business_aliases(self, business_id: str) -> List[Dict[str, Any]]:
        """Get all aliases for a business."""
        if business_id not in self.businesses:
            return []
        
        return self.businesses[business_id]["aliases"]

    def get_all_businesses(self) -> List[Dict[str, Any]]:
        """Get all businesses."""
        return list(self.businesses.values())

    def get_business_by_id(self, business_id: str) -> Optional[Dict[str, Any]]:
        """Get a business by ID."""
        return self.businesses.get(business_id)

    def get_business_by_name(self, canonical_name: str) -> Optional[Dict[str, Any]]:
        """Get a business by canonical name."""
        for business in self.businesses.values():
            if business["canonical_name"] == canonical_name:
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
                })
            }
            
            with open(self.mapping_file, "w", encoding="utf-8") as f:
                json.dump(config_v2, f, indent=4, ensure_ascii=False)
                
        except Exception as e:
            print(f"Warning: Could not save mapping file {self.mapping_file}: {e}")

    def get_stats(self) -> Dict[str, int]:
        """Get statistics about the business mappings."""
        total_aliases = sum(len(b["aliases"]) for b in self.businesses.values())
        exact_aliases = sum(
            len([a for a in b["aliases"] if a["match_type"] == "exact"]) 
            for b in self.businesses.values()
        )
        variant_aliases = sum(
            len([a for a in b["aliases"] if a["match_type"] == "variant"])
            for b in self.businesses.values()
        )
        fuzzy_aliases = sum(
            len([a for a in b["aliases"] if a["match_type"] == "fuzzy"]) 
            for b in self.businesses.values()
        )
        total_indicators = sum(len(b["indicators"]) for b in self.businesses.values())
        
        return {
            "total_businesses": len(self.businesses),
            "total_aliases": total_aliases,
            "exact_aliases": exact_aliases,
            "variant_aliases": variant_aliases,
            "fuzzy_aliases": fuzzy_aliases,
            "total_indicators": total_indicators,
            "canonical_names": len(self.canonical_names)
        } 