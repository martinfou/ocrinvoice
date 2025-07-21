#!/usr/bin/env python3
"""
Convert business mappings to new format.

This script converts all business mappings from the old format
(canonical_name + aliases) to the new format (business_name + keywords).
"""

import json
import sys
from pathlib import Path
from datetime import datetime

def convert_business_mappings(input_file: str, output_file: str) -> bool:
    """Convert business mappings to new format."""
    try:
        # Read the current file
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Convert businesses to new format
        converted_businesses = []
        
        for business in data.get('businesses', []):
            # Determine the business name
            business_name = business.get('business_name') or business.get('canonical_name', '')
            
            # Determine the keywords
            keywords = business.get('keywords', [])
            if not keywords and 'aliases' in business:
                # Convert aliases to keywords
                keywords = business['aliases']
            
            # Create new format entry
            new_business = {
                "id": business.get('id', ''),
                "business_name": business_name,
                "keywords": keywords,
                "indicators": business.get('indicators', []),
                "metadata": business.get('metadata', {})
            }
            
            # Update metadata to indicate conversion
            if 'metadata' not in new_business:
                new_business['metadata'] = {}
            
            new_business['metadata']['converted_to_new_format'] = True
            new_business['metadata']['conversion_date'] = datetime.now().isoformat()
            
            converted_businesses.append(new_business)
        
        # Create new data structure
        new_data = {
            "version": "2.0",
            "updated": datetime.now().isoformat(),
            "businesses": converted_businesses,
            "confidence_weights": data.get('confidence_weights', {
                "exact_match": 1.0,
                "partial_match": 0.8,
                "fuzzy_match": 0.6
            }),
            "backup": data.get('backup', {
                "max_backups_to_keep": 10,
                "auto_cleanup": True,
                "cleanup_on_startup": True,
                "cleanup_on_shutdown": True
            })
        }
        
        # Write the converted data
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(new_data, f, indent=4, ensure_ascii=False)
        
        print(f"✅ Successfully converted {len(converted_businesses)} businesses to new format")
        print(f"📁 Output saved to: {output_file}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error converting business mappings: {e}")
        return False

def main():
    """Main function."""
    config_dir = Path(__file__).parent.parent / "config"
    input_file = config_dir / "business_mappings_v2.json"
    
    if not input_file.exists():
        print(f"❌ Input file not found: {input_file}")
        return False
    
    # Create backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = config_dir / f"business_mappings_v2_backup_{timestamp}.json"
    
    print(f"📁 Creating backup: {backup_file}")
    with open(input_file, 'r', encoding='utf-8') as f:
        backup_data = f.read()
    with open(backup_file, 'w', encoding='utf-8') as f:
        f.write(backup_data)
    
    # Convert the file
    print(f"🔄 Converting {input_file} to new format...")
    success = convert_business_mappings(str(input_file), str(input_file))
    
    if success:
        print("✅ Conversion completed successfully!")
        print(f"💾 Backup saved to: {backup_file}")
    else:
        print("❌ Conversion failed!")
        print(f"🔄 Restoring from backup: {backup_file}")
        with open(backup_file, 'r', encoding='utf-8') as f:
            backup_data = f.read()
        with open(input_file, 'w', encoding='utf-8') as f:
            f.write(backup_data)
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 