#!/usr/bin/env python3
"""
Test script to verify that duplicate expense codes are allowed.
"""

import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_duplicate_cra_codes():
    """Test that duplicate expense codes are allowed."""
    print("🧪 Testing Duplicate Expense Codes...")
    
    try:
        from ocrinvoice.business.category_manager import CategoryManager
        
        # Create a temporary category manager
        manager = CategoryManager()
        
        # Add first category with expense code 8520
        category_id_1 = manager.add_category(
            "Office Supplies", 
            "General office supplies", 
            "8520"
        )
        print("✅ Added first category with expense code 8520")
        
        # Add second category with same expense code 8520
        category_id_2 = manager.add_category(
            "Meals and Entertainment", 
            "Business meals and entertainment", 
            "8520"
        )
        print("✅ Added second category with same expense code 8520")
        
        # Add third category with expense code 8960
        category_id_3 = manager.add_category(
            "Repairs and Maintenance", 
            "Building repairs and maintenance", 
            "8960"
        )
        print("✅ Added third category with expense code 8960")
        
        # Verify all categories exist
        categories = manager.get_all_categories()
        print(f"✅ Total categories: {len(categories)}")
        
        # Count categories by expense code
        cra_code_counts = {}
        for category in categories:
            cra_code = category.get("cra_code", "")
            cra_code_counts[cra_code] = cra_code_counts.get(cra_code, 0) + 1
        
        print("📊 Expense Code Distribution:")
        for code, count in cra_code_counts.items():
            print(f"   {code}: {count} categories")
        
        # Verify that expense code 8520 has multiple categories
        if cra_code_counts.get("8520", 0) >= 2:
            print("✅ Duplicate expense codes are working correctly")
            return True
        else:
            print("❌ Duplicate expense codes are not working")
            return False
        
    except Exception as e:
        print(f"❌ Duplicate expense code test failed: {e}")
        return False

def main():
    """Run the duplicate expense code test."""
    print("🚀 Testing Duplicate Expense Code Support...")
    print("=" * 50)
    
    success = test_duplicate_cra_codes()
    
    print("=" * 50)
    if success:
        print("🎉 Duplicate expense codes are now supported!")
        print("✅ Multiple categories can share the same expense code")
    else:
        print("⚠️  Duplicate expense code support failed!")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main()) 