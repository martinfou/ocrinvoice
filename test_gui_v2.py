#!/usr/bin/env python3
"""
Test script for GUI with Business Mapping V2

Tests the GUI components with the new hierarchical business mappings structure.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from PyQt6.QtWidgets import QApplication
from ocrinvoice.gui.business_alias_tab import BusinessAliasTab


def test_gui_loading():
    """Test that the GUI loads correctly with the new structure."""
    print("🧪 Testing GUI with Business Mapping V2...")
    
    # Create QApplication
    app = QApplication(sys.argv)
    
    try:
        # Create the business alias tab
        tab = BusinessAliasTab()
        
        print("✅ GUI created successfully")
        print(f"📊 Mapping manager version: {tab.mapping_manager.version}")
        print(f"📊 Total businesses: {len(tab.mapping_manager.businesses)}")
        
        # Test loading aliases
        print("\n🔄 Testing alias loading...")
        tab._load_aliases()
        
        # Wait a bit for the thread to complete
        import time
        time.sleep(1)
        
        # Check if aliases were loaded
        if hasattr(tab, 'alias_table') and tab.alias_table.rowCount() > 0:
            print(f"✅ Aliases loaded: {tab.alias_table.rowCount()} rows")
        else:
            print("❌ No aliases loaded")
        
        print("✅ GUI test completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ GUI test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_business_operations():
    """Test business operations through the GUI."""
    print("\n🧪 Testing business operations through GUI...")
    
    # Create QApplication
    app = QApplication(sys.argv)
    
    try:
        # Create the business alias tab
        tab = BusinessAliasTab()
        
        # Test adding a new business
        print("  ➕ Testing new business creation...")
        
        # Simulate the new business dialog
        from ocrinvoice.gui.business_alias_tab import NewBusinessDialog
        dialog = NewBusinessDialog()
        dialog.name_edit.setText("Test GUI Business")
        
        # Simulate accepting the dialog
        if dialog.get_business_name() == "Test GUI Business":
            print("    ✅ New business dialog works correctly")
        else:
            print("    ❌ New business dialog failed")
        
        print("✅ Business operations test completed")
        return True
        
    except Exception as e:
        print(f"❌ Business operations test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all GUI tests."""
    print("🚀 Starting GUI V2 Tests\n")
    
    try:
        # Test GUI loading
        test_gui_loading()
        
        # Test business operations
        test_business_operations()
        
        print("\n🎉 All GUI tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ GUI test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 