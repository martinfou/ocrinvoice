#!/usr/bin/env python3
"""Test script to reproduce the alias editing bug."""

import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from src.ocrinvoice.gui.business_keyword_tab import BusinessKeywordTab

def test_alias_edit_bug():
    """Test to reproduce the alias editing bug where wrong data is loaded."""
    print("🔧 Testing alias editing bug...")
    
    # Create QApplication if it doesn't exist
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    # Create the business keyword tab
    tab = BusinessKeywordTab()
    
    # Create test aliases
    test_aliases = [
        {
            "company_name": "banque-td",
            "business_name": "TD Bank",
            "match_type": "Exact",
            "usage_count": 0,
            "last_used": "",
            "fuzzy_matching": True,
            "case_sensitive": False,
        },
        {
            "company_name": "gagnon",
            "business_name": "Gagnon & Associates",
            "match_type": "Exact",
            "usage_count": 0,
            "last_used": "",
            "fuzzy_matching": True,
            "case_sensitive": False,
        },
        {
            "company_name": "hydro-quebec",
            "business_name": "Hydro-Quebec",
            "match_type": "Exact",
            "usage_count": 0,
            "last_used": "",
            "fuzzy_matching": True,
            "case_sensitive": False,
        }
    ]
    
    # Load the aliases into the table
    tab.alias_table.load_aliases(test_aliases)
    
    print(f"✅ Loaded {len(test_aliases)} test aliases")
    print(f"   Table structure:")
    print(f"   - Column 0: Business Name (business_name)")
    print(f"   - Column 1: Keyword (company_name)")
    print(f"   - Column 2: Match Type")
    print(f"   - Column 3: Usage Count")
    print(f"   - Column 4: Last Used")
    
    # Test 1: Test without sorting
    print(f"\n🔍 Test 1: Test without sorting")
    
    # Select row 0 (should be banque-td)
    tab.alias_table.selectRow(0)
    selected_alias = tab.alias_table.get_selected_alias()
    if selected_alias:
        company_name = selected_alias.get("company_name", "")
        print(f"   Row 0 selected: {company_name}")
        if company_name == "banque-td":
            print(f"   ✅ Row 0 correctly shows banque-td")
        else:
            print(f"   ❌ Row 0 shows wrong alias: {company_name}")
            return False
    else:
        print(f"   ❌ No alias selected at row 0")
        return False
    
    # Test 2: Test with sorting by Business Name (column 0)
    print(f"\n🔍 Test 2: Test with sorting by Business Name")
    
    # Sort by Business Name column (column 0)
    tab.alias_table.sortItems(0, Qt.SortOrder.AscendingOrder)
    
    # Wait a moment for sorting to complete
    import time
    time.sleep(0.1)
    
    # Check what's now in row 0 after sorting
    tab.alias_table.selectRow(0)
    selected_alias = tab.alias_table.get_selected_alias()
    if selected_alias:
        company_name = selected_alias.get("company_name", "")
        business_name = selected_alias.get("business_name", "")
        print(f"   Row 0 after sorting by Business Name: {company_name} -> {business_name}")
        
        # After sorting by Business Name, the order should be:
        # 1. Gagnon & Associates (G)
        # 2. Hydro-Quebec (H) 
        # 3. TD Bank (T)
        if business_name == "Gagnon & Associates":
            print(f"   ✅ Row 0 correctly shows Gagnon & Associates after sorting")
        else:
            print(f"   ❌ Row 0 shows wrong business after sorting: {business_name}")
            return False
    else:
        print(f"   ❌ No alias selected at row 0 after sorting")
        return False
    
    # Test 3: Test with sorting by Keyword (column 1)
    print(f"\n🔍 Test 3: Test with sorting by Keyword")
    
    # Sort by Keyword column (column 1)
    tab.alias_table.sortItems(1, Qt.SortOrder.AscendingOrder)
    time.sleep(0.1)
    
    # Check what's now in row 0 after sorting by keyword
    tab.alias_table.selectRow(0)
    selected_alias = tab.alias_table.get_selected_alias()
    if selected_alias:
        company_name = selected_alias.get("company_name", "")
        print(f"   Row 0 after sorting by Keyword: {company_name}")
        
        # After sorting by Keyword, the order should be:
        # 1. banque-td (b)
        # 2. gagnon (g)
        # 3. hydro-quebec (h)
        if company_name == "banque-td":
            print(f"   ✅ Row 0 correctly shows banque-td after sorting by keyword")
        else:
            print(f"   ❌ Row 0 shows wrong keyword after sorting: {company_name}")
            return False
    else:
        print(f"   ❌ No alias selected at row 0 after sorting by keyword")
        return False
    
    # Test 4: Test double-click after sorting
    print(f"\n🔍 Test 4: Test double-click after sorting")
    
    # Double-click on the first row (should be banque-td after sorting by keyword)
    item_first_row = tab.alias_table.item(0, 1)  # Keyword column
    if item_first_row:
        tab.alias_table._on_item_double_clicked(item_first_row)
        print(f"   ✅ Double-clicked on first row keyword cell")
    else:
        print(f"   ❌ Could not find first row keyword cell")
        return False
    
    # Test 5: Test get_alias_at_row after sorting
    print(f"\n🔍 Test 5: Test get_alias_at_row after sorting")
    
    # Get alias at row 0
    alias_at_row_0 = tab.alias_table.get_alias_at_row(0)
    if alias_at_row_0:
        company_name = alias_at_row_0.get("company_name", "")
        print(f"   get_alias_at_row(0): {company_name}")
        if company_name == "banque-td":
            print(f"   ✅ get_alias_at_row(0) correctly returns banque-td")
        else:
            print(f"   ❌ get_alias_at_row(0) returns wrong alias: {company_name}")
            return False
    else:
        print(f"   ❌ No alias at row 0")
        return False
    
    # Get alias at row 1
    alias_at_row_1 = tab.alias_table.get_alias_at_row(1)
    if alias_at_row_1:
        company_name = alias_at_row_1.get("company_name", "")
        print(f"   get_alias_at_row(1): {company_name}")
        if company_name == "gagnon":
            print(f"   ✅ get_alias_at_row(1) correctly returns gagnon")
        else:
            print(f"   ❌ get_alias_at_row(1) returns wrong alias: {company_name}")
            return False
    else:
        print(f"   ❌ No alias at row 1")
        return False
    
    print(f"\n🎉 All alias selection tests passed!")
    return True

if __name__ == "__main__":
    success = test_alias_edit_bug()
    if success:
        print("🎉 Alias selection is working correctly!")
    else:
        print("❌ Alias selection has issues!")
        sys.exit(1) 
        sys.exit(1) 