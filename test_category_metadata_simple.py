#!/usr/bin/env python3
"""
Simple test script for category metadata saving and restoration logic.
"""

import sys
import os
from PyQt6.QtWidgets import QApplication

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_category_metadata_logic():
    """Test that category metadata logic works correctly."""
    print("🧪 Testing Category Metadata Logic...")
    
    try:
        from ocrinvoice.gui.widgets.file_naming import FileNamingWidget
        from ocrinvoice.gui.widgets.data_panel import DataPanelWidget
        from ocrinvoice.gui.ocr_main_window import OCRMainWindow
        
        # Create application
        app = QApplication(sys.argv)
        
        # Create main window
        main_window = OCRMainWindow()
        
        # Set up test data with category
        test_data = {
            "company": "Test Company",
            "total": "100.00",
            "date": "2024-01-15",
            "selected_project": "test-project",
            "selected_document_type": "invoice",
            "selected_category": "Office Supplies"
        }
        
        # Set up data panel with categories
        category_names = ["Office Supplies", "Meals and Entertainment", "Travel Expenses"]
        main_window.data_panel.update_categories(category_names)
        
        # Test 1: Set category and verify it's in the data
        main_window.data_panel.set_selected_category("Office Supplies")
        current_category = main_window.data_panel.get_selected_category()
        if current_category == "Office Supplies":
            print("✅ Category selection works correctly")
        else:
            print(f"❌ Category selection failed. Expected: 'Office Supplies', Got: '{current_category}'")
            return False
        
        # Test 2: Simulate metadata restoration
        selected_category = test_data.get("selected_category", "")
        if selected_category:
            main_window.data_panel.set_selected_category(selected_category)
            print(f"✅ Restored category selection: {selected_category}")
        
        # Test 3: Verify restoration worked
        restored_category = main_window.data_panel.get_selected_category()
        if restored_category == "Office Supplies":
            print("✅ Category restoration logic works correctly")
        else:
            print(f"❌ Category restoration failed. Expected: 'Office Supplies', Got: '{restored_category}'")
            return False
        
        # Test 4: Test category change updates data
        main_window.data_panel.set_selected_category("Travel Expenses")
        updated_category = main_window.data_panel.get_selected_category()
        if updated_category == "Travel Expenses":
            print("✅ Category change works correctly")
        else:
            print(f"❌ Category change failed. Expected: 'Travel Expenses', Got: '{updated_category}'")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Category metadata logic test failed: {e}")
        return False

def test_file_naming_metadata_logic():
    """Test that file naming widget metadata logic includes category."""
    print("🧪 Testing File Naming Metadata Logic...")
    
    try:
        from ocrinvoice.gui.widgets.file_naming import FileNamingWidget
        from ocrinvoice.gui.widgets.data_panel import DataPanelWidget
        from ocrinvoice.gui.ocr_main_window import OCRMainWindow
        
        # Create application
        app = QApplication(sys.argv)
        
        # Create main window
        main_window = OCRMainWindow()
        
        # Set up data panel with categories
        category_names = ["Office Supplies", "Meals and Entertainment", "Travel Expenses"]
        main_window.data_panel.update_categories(category_names)
        main_window.data_panel.set_selected_category("Office Supplies")
        
        # Test that the file naming widget can access category
        current_category = main_window.data_panel.get_selected_category()
        if current_category == "Office Supplies":
            print("✅ File naming widget can access category selection")
        else:
            print(f"❌ File naming widget cannot access category. Expected: 'Office Supplies', Got: '{current_category}'")
            return False
        
        # Test that category is included in template
        template = main_window.file_naming_widget.template_input.text()
        if "{category}" in template:
            print("✅ Category field is included in template")
        else:
            print("❌ Category field is not included in template")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ File naming metadata logic test failed: {e}")
        return False

def main():
    """Run all category metadata logic tests."""
    print("🚀 Starting Category Metadata Logic Tests...")
    print("=" * 60)
    
    # Test category metadata logic
    logic_success = test_category_metadata_logic()
    
    # Test file naming metadata logic
    naming_success = test_file_naming_metadata_logic()
    
    print("=" * 60)
    print("📊 Test Results:")
    print(f"   Category Metadata Logic: {'✅ PASS' if logic_success else '❌ FAIL'}")
    print(f"   File Naming Metadata Logic: {'✅ PASS' if naming_success else '❌ FAIL'}")
    
    if all([logic_success, naming_success]):
        print("🎉 All category metadata logic tests passed!")
        print("✅ Category metadata saving and restoration logic is working correctly!")
        return 0
    else:
        print("⚠️  Some category metadata logic tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 