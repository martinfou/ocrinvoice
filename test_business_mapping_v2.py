#!/usr/bin/env python3
"""
Test script for Business Mapping Manager V2

Tests the new hierarchical business mappings structure and functionality.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from ocrinvoice.business.business_mapping_manager_v2 import BusinessMappingManagerV2


def test_basic_functionality():
    """Test basic functionality of the new business mapping manager."""
    print("🧪 Testing Business Mapping Manager V2...")
    
    # Initialize manager
    manager = BusinessMappingManagerV2()
    
    print(f"📊 Version: {manager.version}")
    print(f"📊 Total businesses: {len(manager.businesses)}")
    print(f"📊 Business names: {len(manager.get_business_names())}")
    
    # Get stats
    stats = manager.get_stats()
    print(f"📊 Statistics: {stats}")
    
    # Test business matching
    test_cases = [
        ("TD BANK INVOICE", "Should match banque-td"),
        ("TORONTO DOMINION BANK", "Should match banque-td"),
        ("HYDRO-QUÉBEC BILLING", "Should match hydro-québec"),
        ("BMR HARDWARE", "Should match bmr"),
        ("PHARMACY DISPENSING", "Should match pharmacie"),
        ("GAGN 0 N ASSOCIATES", "Should match gagnon"),
        ("UNKNOWN COMPANY", "Should not match anything"),
    ]
    
    print("\n🔍 Testing business matching:")
    for text, description in test_cases:
        match = manager.find_business_match(text)
        if match:
            business_name, match_type, confidence = match
            print(f"  ✅ '{text}' → {business_name} ({match_type}, {confidence:.2f})")
        else:
            print(f"  ❌ '{text}' → No match")
    
    # Test getting businesses
    print("\n🏢 Testing business retrieval:")
    businesses = manager.get_all_businesses()
    for business in businesses[:3]:  # Show first 3
        print(f"  • {business['business_name']} ({business['id']})")
        print(f"    - Keywords: {len(business['keywords'])}")
        print(f"    - Indicators: {len(business['indicators'])}")
    
    # Test getting canonical names
    print(f"\n📋 Business names: {manager.get_business_names()}")
    
    return True


def test_business_operations():
    """Test business operations (add, remove, update)."""
    print("\n🧪 Testing business operations...")
    
    # Create a temporary manager for testing
    test_file = "config/test_business_mappings.json"
    manager = BusinessMappingManagerV2(test_file)
    
    # Test adding a new business
    print("  ➕ Adding new business 'Test Company'...")
    success = manager.add_business_name("Test Company")
    print(f"    Result: {'✅ Success' if success else '❌ Failed'}")
    
    # Test adding an alias
    print("  ➕ Adding alias 'test' for Test Company...")
    business = manager.get_business_by_name("Test Company")
    if business:
        success = manager.add_keyword(business["id"], "test", "exact")
        print(f"    Result: {'✅ Success' if success else '❌ Failed'}")
    
    # Test matching the new business
    print("  🔍 Testing match for new business...")
    match = manager.find_business_match("TEST COMPANY INVOICE")
    if match:
        business_name, match_type, confidence = match
        print(f"    ✅ Match found: {business_name} ({match_type}, {confidence:.2f})")
    else:
        print("    ❌ No match found")
    
    # Clean up
    try:
        import os
        os.remove(test_file)
        print("  🧹 Cleaned up test file")
    except:
        pass
    
    return True


def test_migration_compatibility():
    """Test that the new manager can handle old format data."""
    print("\n🧪 Testing migration compatibility...")
    
    # Test with old format data
    old_format_data = {
        "exact_matches": {
            "test company": "test-company"
        },
        "partial_matches": {
            "test": "test-company"
        },
        "fuzzy_candidates": ["test-company"],
        "indicators": {
            "test-company": ["test", "company"]
        },
        "canonical_names": ["test-company"]
    }
    
    # Save old format data
    import json
    test_file = "config/test_old_format.json"
    with open(test_file, 'w') as f:
        json.dump(old_format_data, f, indent=4)
    
    # Test loading with new manager
    manager = BusinessMappingManagerV2(test_file)
    print(f"  📊 Loaded {len(manager.businesses)} businesses from old format")
    
    # Test matching
    match = manager.find_business_match("TEST COMPANY")
    if match:
        business_name, match_type, confidence = match
        print(f"  ✅ Old format match: {business_name} ({match_type}, {confidence:.2f})")
    else:
        print("  ❌ Old format match failed")
    
    # Clean up
    try:
        import os
        os.remove(test_file)
        print("  🧹 Cleaned up test file")
    except:
        pass
    
    return True


def main():
    """Run all tests."""
    print("🚀 Starting Business Mapping Manager V2 Tests\n")
    
    try:
        # Test basic functionality
        test_basic_functionality()
        
        # Test business operations
        test_business_operations()
        
        # Test migration compatibility
        test_migration_compatibility()
        
        print("\n🎉 All tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 