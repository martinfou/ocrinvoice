#!/usr/bin/env python3
"""
Business Mappings Migration Script

Converts the current business_mappings.json structure to the new hierarchical format.
This script handles the migration from the old flat structure to the new business-centric structure.
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ocrinvoice.business.business_mapping_manager import BusinessMappingManager


class BusinessMappingsMigrator:
    """Handles migration from old to new business mappings structure."""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.old_file = self.config_dir / "business_mappings.json"
        self.new_file = self.config_dir / "business_mappings_v2.json"
        self.backup_file = self.config_dir / f"business_mappings_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
    def load_old_structure(self) -> Dict[str, Any]:
        """Load the old business mappings structure."""
        if not self.old_file.exists():
            raise FileNotFoundError(f"Old business mappings file not found: {self.old_file}")
            
        with open(self.old_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def create_backup(self, data: Dict[str, Any]) -> str:
        """Create a backup of the current data."""
        with open(self.backup_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        return str(self.backup_file)
    
    def migrate_to_new_structure(self, old_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert old structure to new hierarchical structure."""
        
        # Extract data from old structure
        exact_matches = old_data.get("exact_matches", {})
        partial_matches = old_data.get("partial_matches", {})
        fuzzy_candidates = old_data.get("fuzzy_candidates", [])
        indicators = old_data.get("indicators", {})
        canonical_names = old_data.get("canonical_names", [])
        confidence_weights = old_data.get("confidence_weights", {})
        
        # Create new structure
        new_structure = {
            "version": "2.0",
            "created": datetime.now().isoformat(),
            "migrated_from": "1.0",
            "businesses": [],
            "confidence_weights": confidence_weights
        }
        
        # Get all unique business names
        all_businesses = set()
        all_businesses.update(exact_matches.values())
        all_businesses.update(partial_matches.values())
        all_businesses.update(fuzzy_candidates)
        all_businesses.update(canonical_names)
        
        # Create business entries
        for business_name in sorted(all_businesses):
            business_entry = self._create_business_entry(
                business_name, exact_matches, partial_matches, 
                fuzzy_candidates, indicators
            )
            new_structure["businesses"].append(business_entry)
        
        return new_structure
    
    def _create_business_entry(self, business_name: str, exact_matches: Dict, 
                              partial_matches: Dict, fuzzy_candidates: List, 
                              indicators: Dict) -> Dict[str, Any]:
        """Create a business entry in the new structure."""
        
        # Generate business ID
        business_id = self._generate_business_id(business_name)
        
        # Collect aliases
        aliases = []
        
        # Add exact matches
        for keyword, canonical in exact_matches.items():
            if canonical == business_name:
                aliases.append({
                    "keyword": keyword,
                    "match_type": "exact",
                    "case_sensitive": False,
                    "fuzzy_matching": True
                })
        
        # Add variant matches (converted from partial)
        for keyword, canonical in partial_matches.items():
            if canonical == business_name:
                aliases.append({
                    "keyword": keyword,
                    "match_type": "variant",
                    "case_sensitive": False,
                    "fuzzy_matching": True
                })
        
        # Add fuzzy candidates
        if business_name in fuzzy_candidates:
            aliases.append({
                "keyword": business_name,
                "match_type": "fuzzy",
                "case_sensitive": False,
                "fuzzy_matching": True
            })
        
        # Get indicators
        business_indicators = indicators.get(business_name, [])
        
        # Create business entry
        business_entry = {
            "id": business_id,
            "canonical_name": business_name,
            "aliases": aliases,
            "indicators": business_indicators,
            "metadata": {
                "created": datetime.now().isoformat(),
                "migrated": True,
                "original_aliases_count": len(aliases),
                "original_indicators_count": len(business_indicators)
            }
        }
        
        return business_entry
    
    def _generate_business_id(self, business_name: str) -> str:
        """Generate a business ID from the business name."""
        # Convert to lowercase, replace spaces with hyphens, remove special chars
        import re
        id_base = re.sub(r'[^a-zA-Z0-9\s-]', '', business_name.lower())
        id_base = re.sub(r'\s+', '-', id_base.strip())
        return id_base
    
    def save_new_structure(self, new_data: Dict[str, Any]) -> str:
        """Save the new structure to file."""
        with open(self.new_file, 'w', encoding='utf-8') as f:
            json.dump(new_data, f, indent=4, ensure_ascii=False)
        return str(self.new_file)
    
    def validate_migration(self, old_data: Dict[str, Any], new_data: Dict[str, Any]) -> bool:
        """Validate that the migration preserved all data."""
        
        # Count businesses
        old_businesses = set()
        old_businesses.update(old_data.get("exact_matches", {}).values())
        old_businesses.update(old_data.get("partial_matches", {}).values())
        old_businesses.update(old_data.get("fuzzy_candidates", []))
        old_businesses.update(old_data.get("canonical_names", []))
        
        new_businesses = {b["canonical_name"] for b in new_data.get("businesses", [])}
        
        if old_businesses != new_businesses:
            print(f"❌ Business count mismatch: {len(old_businesses)} vs {len(new_businesses)}")
            print(f"  Missing: {old_businesses - new_businesses}")
            print(f"  Extra: {new_businesses - old_businesses}")
            return False
        
        # Count total mappings (exact + partial)
        old_mappings = len(old_data.get("exact_matches", {})) + len(old_data.get("partial_matches", {}))
        new_mappings = sum(len(b["aliases"]) for b in new_data.get("businesses", []))
        
        # Add fuzzy candidates count
        old_fuzzy_count = len(old_data.get("fuzzy_candidates", []))
        new_fuzzy_count = sum(1 for b in new_data.get("businesses", []) 
                             for a in b["aliases"] if a["match_type"] == "fuzzy")
        
        total_old = old_mappings + old_fuzzy_count
        total_new = new_mappings
        
        if total_old != total_new:
            print(f"❌ Total mappings mismatch: {total_old} vs {total_new}")
            print(f"  Old: {old_mappings} exact/partial + {old_fuzzy_count} fuzzy = {total_old}")
            print(f"  New: {new_mappings} total")
            return False
        
        # Count indicators
        old_indicators = sum(len(indicators) for indicators in old_data.get("indicators", {}).values())
        new_indicators = sum(len(b["indicators"]) for b in new_data.get("businesses", []))
        
        if old_indicators != new_indicators:
            print(f"❌ Indicator count mismatch: {old_indicators} vs {new_indicators}")
            return False
        
        print("✅ Migration validation passed!")
        return True
    
    def run_migration(self, dry_run: bool = False) -> bool:
        """Run the complete migration process."""
        
        print("🔄 Starting business mappings migration...")
        
        try:
            # Load old structure
            print("📖 Loading old business mappings...")
            old_data = self.load_old_structure()
            print(f"✅ Loaded {len(old_data.get('canonical_names', []))} businesses")
            
            # Create backup
            print("💾 Creating backup...")
            backup_path = self.create_backup(old_data)
            print(f"✅ Backup created: {backup_path}")
            
            # Migrate to new structure
            print("🔄 Converting to new structure...")
            new_data = self.migrate_to_new_structure(old_data)
            print(f"✅ Converted {len(new_data['businesses'])} businesses")
            
            # Validate migration
            print("🔍 Validating migration...")
            if not self.validate_migration(old_data, new_data):
                print("❌ Migration validation failed!")
                return False
            
            if dry_run:
                print("🔍 DRY RUN: Would save new structure to:", self.new_file)
                print("📊 Migration summary:")
                self._print_migration_summary(old_data, new_data)
                return True
            
            # Save new structure
            print("💾 Saving new structure...")
            new_file_path = self.save_new_structure(new_data)
            print(f"✅ New structure saved: {new_file_path}")
            
            # Print summary
            print("📊 Migration completed successfully!")
            self._print_migration_summary(old_data, new_data)
            
            return True
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            return False
    
    def _print_migration_summary(self, old_data: Dict[str, Any], new_data: Dict[str, Any]):
        """Print a summary of the migration."""
        
        print("\n📋 Migration Summary:")
        print(f"  • Businesses: {len(new_data['businesses'])}")
        print(f"  • Total aliases: {sum(len(b['aliases']) for b in new_data['businesses'])}")
        print(f"  • Total indicators: {sum(len(b['indicators']) for b in new_data['businesses'])}")
        
        print("\n🏢 Business breakdown:")
        for business in new_data['businesses']:
            exact_count = len([a for a in business['aliases'] if a['match_type'] == 'exact'])
            partial_count = len([a for a in business['aliases'] if a['match_type'] == 'variant'])
            fuzzy_count = len([a for a in business['aliases'] if a['match_type'] == 'fuzzy'])
            
            print(f"  • {business['canonical_name']} ({business['id']})")
            print(f"    - Aliases: {exact_count} exact, {partial_count} variant, {fuzzy_count} fuzzy")
            print(f"    - Indicators: {len(business['indicators'])}")


def main():
    """Main migration function."""
    
    import argparse
    
    parser = argparse.ArgumentParser(description="Migrate business mappings to new structure")
    parser.add_argument("--config-dir", default="config", help="Configuration directory")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without saving")
    parser.add_argument("--backup-only", action="store_true", help="Only create backup, don't migrate")
    
    args = parser.parse_args()
    
    migrator = BusinessMappingsMigrator(args.config_dir)
    
    if args.backup_only:
        print("💾 Creating backup only...")
        old_data = migrator.load_old_structure()
        backup_path = migrator.create_backup(old_data)
        print(f"✅ Backup created: {backup_path}")
        return
    
    success = migrator.run_migration(dry_run=args.dry_run)
    
    if success:
        print("\n🎉 Migration completed successfully!")
        if not args.dry_run:
            print("📝 Next steps:")
            print("  1. Test the new structure with the updated business mapping manager")
            print("  2. Update the GUI to work with the new structure")
            print("  3. Remove the old business_mappings.json when ready")
    else:
        print("\n❌ Migration failed!")
        sys.exit(1)


if __name__ == "__main__":
    main() 