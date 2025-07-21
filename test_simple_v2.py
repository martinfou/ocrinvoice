#!/usr/bin/env python3
"""
Simple test for Business Mapping Manager V2
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from ocrinvoice.business.business_mapping_manager_v2 import BusinessMappingManagerV2


def main():
    """Test the business mapping manager."""
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
    
    print("\n🎉 Test completed successfully!")
    return True


if __name__ == "__main__":
    main() 