#!/usr/bin/env python3
"""
Command-line tool for managing business aliases and official business names
Usage: 
  python3 manage_business_cli.py <alias> <business_name> <match_type>
  python3 manage_business_cli.py --add-official <business_name>
"""

import sys
from business_alias_manager import BusinessAliasManager

def add_official_business_name(business_name):
    """Add a new official business name to the configuration."""
    alias_manager = BusinessAliasManager()

    # Enforce lowercase and dash format for official name
    business_name = business_name.strip().lower().replace(' ', '-')

    # Check if name already exists
    if alias_manager.is_official_name(business_name):
        print(f"❌ Error: '{business_name}' is already an official business name")
        return False
    
    try:
        # Get current official names
        current_official_names = alias_manager.get_official_names()
        
        # Add the new official name to the configuration
        alias_manager.config["official_names"].append(business_name)
        alias_manager.official_names.add(business_name)
        
        # Add exact match entry for the official name itself
        alias_manager.config["exact_matches"][business_name] = business_name
        
        # Save the configuration
        alias_manager._save_config()
        
        print(f"✅ Successfully added '{business_name}' as an official business name")
        print(f"✅ Created exact match: '{business_name}' -> '{business_name}'")
        print(f"📋 Total official business names: {len(alias_manager.get_official_names())}")
        
        # Show updated list
        print("\n📋 All Official Business Names:")
        print("-" * 30)
        official_names = alias_manager.get_official_names()
        for i, name in enumerate(official_names, 1):
            print(f"   {i}. {name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error adding official business name: {e}")
        return False

def main():
    # Check for --add-official option
    if len(sys.argv) == 3 and sys.argv[1] == "--add-official":
        business_name = sys.argv[2]
        if not business_name.strip():
            print("❌ Error: Business name cannot be empty")
            sys.exit(1)
        success = add_official_business_name(business_name.strip())
        sys.exit(0 if success else 1)
    
    # Original alias management functionality
    if len(sys.argv) != 4:
        print("Usage:")
        print("  python3 manage_business_cli.py <alias> <business_name> <match_type>")
        print("  python3 manage_business_cli.py --add-official <business_name>")
        print("")
        print("Commands:")
        print("  Add alias:     python3 manage_business_cli.py <alias> <business_name> <match_type>")
        print("  Add official:  python3 manage_business_cli.py --add-official <business_name>")
        print("")
        print("Arguments for alias:")
        print("  alias         - The text to match (e.g., 'ABC Corp')")
        print("  business_name - Official business name (must be one of the official names)")
        print("  match_type    - 'exact' or 'partial'")
        print("")
        print("Arguments for official business name:")
        print("  business_name - New official business name to add")
        print("")
        print("Examples:")
        print("  python3 manage_business_cli.py 'ABC Corp' 'BMR' 'exact'")
        print("  python3 manage_business_cli.py 'MyBank' 'Banque-TD' 'partial'")
        print("  python3 manage_business_cli.py --add-official 'New-Company'")
        print("")
        
        # Show available business names
        alias_manager = BusinessAliasManager()
        print("Available official business names:")
        official_names = alias_manager.get_official_names()
        for name in official_names:
            print(f"  - {name}")
        sys.exit(1)
    
    alias_text = sys.argv[1].strip().lower()
    business_name = sys.argv[2].strip().lower().replace(' ', '-')
    match_type = sys.argv[3].lower()
    
    # Validate match type
    if match_type not in ['exact', 'partial']:
        print("❌ Error: match_type must be 'exact' or 'partial'")
        sys.exit(1)
    
    # Convert match type to internal format
    match_type_internal = "exact_matches" if match_type == "exact" else "partial_matches"
    
    # Initialize alias manager
    alias_manager = BusinessAliasManager()
    
    # Validate business name
    if not alias_manager.is_official_name(business_name):
        print(f"❌ Error: '{business_name}' is not an official business name")
        print("Available official business names:")
        official_names = alias_manager.get_official_names()
        for name in official_names:
            print(f"  - {name}")
        print("")
        print("To add a new official business name, use:")
        print(f"  python3 manage_business_cli.py --add-official '{business_name}'")
        sys.exit(1)
    
    try:
        # Add the alias
        alias_manager.add_alias(alias_text, business_name, match_type_internal)
        print(f"✅ Successfully added: '{alias_text}' -> '{business_name}' ({match_type} match)")
        
        # Test the new alias
        result = alias_manager.find_business_match(alias_text)
        if result:
            matched_name, match_type_result, confidence = result
            print(f"✅ Test result: '{alias_text}' -> '{matched_name}' ({match_type_result}, confidence: {confidence:.2f})")
        else:
            print(f"❌ Test failed: '{alias_text}' -> No match")
            
    except Exception as e:
        print(f"❌ Error adding alias: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 