#!/usr/bin/env python3
"""
Test script for Business Alias Manager functionality
"""

from business_alias_manager import BusinessAliasManager

def test_business_aliases():
    """Test the business alias matching functionality"""
    
    print("🧪 Testing Business Alias Manager")
    print("=" * 50)
    
    # Initialize the alias manager
    alias_manager = BusinessAliasManager()
    
    # Test cases
    test_cases = [
        # Exact matches
        ("BMR", "Should match BMR Building Materials"),
        ("TD", "Should match TD Bank"),
        ("compte de taxes scolaire", "Should match CONSEIL SCOLAIRE DE DISTRICT CATHOLIQUE"),
        
        # Partial matches
        ("Forfaiterie", "Should match La Forfaiterie"),
        ("grandes-seigneuries", "Should match CONSEIL SCOLAIRE DE DISTRICT CATHOLIQUE"),
        ("Hydro", "Should match Hydro-Québec"),
        
        # Fuzzy matches (with indicators)
        ("CDMPTE DE TAXES SCDLAIRE", "Should fuzzy match CONSEIL SCOLAIRE DE DISTRICT CATHOLIQUE"),
        ("BMR Matco", "Should fuzzy match BMR Building Materials"),
        
        # No matches
        ("Unknown Company", "Should return None"),
        ("Random Text", "Should return None"),
    ]
    
    print("Testing various input strings:")
    print("-" * 50)
    
    for test_input, description in test_cases:
        result = alias_manager.find_business_match(test_input)
        
        if result:
            business_name, match_type, confidence = result
            print(f"✅ '{test_input}' -> '{business_name}' ({match_type}, confidence: {confidence:.2f})")
            print(f"   {description}")
        else:
            print(f"❌ '{test_input}' -> No match")
            print(f"   {description}")
        print()
    
    # Test configuration stats
    print("📊 Configuration Statistics:")
    print("-" * 30)
    stats = alias_manager.get_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    # Test all business names
    print("\n📋 All Configured Business Names:")
    print("-" * 40)
    business_names = alias_manager.get_all_business_names()
    for i, name in enumerate(business_names, 1):
        print(f"   {i:2d}. {name}")
    
    print("\n✅ Business alias testing complete!")

def test_alias_operations():
    """Test adding and modifying aliases"""
    
    print("\n🔧 Testing Alias Operations")
    print("=" * 40)
    
    # Create a test alias manager with a temporary file
    alias_manager = BusinessAliasManager("test_aliases.json")
    
    # Test adding new aliases
    print("Adding test aliases...")
    alias_manager.add_alias("TEST123", "Test Company Inc", "exact_matches")
    alias_manager.add_alias("TEST456", "Test Company Inc", "partial_matches")
    
    # Test the new aliases
    test_result1 = alias_manager.find_business_match("TEST123")
    test_result2 = alias_manager.find_business_match("TEST456")
    
    if test_result1:
        print(f"✅ Added exact match: 'TEST123' -> '{test_result1[0]}'")
    else:
        print("❌ Failed to add exact match")
    
    if test_result2:
        print(f"✅ Added partial match: 'TEST456' -> '{test_result2[0]}'")
    else:
        print("❌ Failed to add partial match")
    
    # Clean up test file
    import os
    if os.path.exists("test_aliases.json"):
        os.remove("test_aliases.json")
        print("🧹 Cleaned up test file")

if __name__ == "__main__":
    test_business_aliases()
    test_alias_operations() 