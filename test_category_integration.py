#!/usr/bin/env python3
"""
Test script for category integration in template and data panel.
"""

import sys
import os
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt6.QtCore import QTimer

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_category_template():
    """Test that category is included in the template."""
    print("🧪 Testing Category Template Integration...")
    
    try:
        from ocrinvoice.gui.widgets.file_naming import FileNamingWidget
        
        # Create application
        app = QApplication(sys.argv)
        
        # Create file naming widget
        file_naming_widget = FileNamingWidget()
        
        # Check if category is in the template
        template = file_naming_widget.template_input.text()
        print(f"✅ Template: {template}")
        
        if "{category}" in template:
            print("✅ Category field found in template")
        else:
            print("❌ Category field not found in template")
            return False
        
        # Check if category is in field combo
        field_combo = file_naming_widget.field_combo
        category_found = False
        for i in range(field_combo.count()):
            if field_combo.itemText(i) == "Category":
                category_found = True
                break
        
        if category_found:
            print("✅ Category found in field combo")
        else:
            print("❌ Category not found in field combo")
            return False
        
        # Check if category is in presets
        preset_combo = file_naming_widget.preset_combo
        category_in_presets = False
        for i in range(preset_combo.count()):
            preset_text = preset_combo.itemText(i)
            if "{category}" in preset_text:
                category_in_presets = True
                print(f"✅ Category found in preset: {preset_text}")
        
        if category_in_presets:
            print("✅ Category found in presets")
        else:
            print("❌ Category not found in presets")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Category template test failed: {e}")
        return False

def test_category_data_panel():
    """Test that category dropdown is in the data panel."""
    print("🧪 Testing Category Data Panel Integration...")
    
    try:
        from ocrinvoice.gui.widgets.data_panel import DataPanelWidget
        
        # Create application
        app = QApplication(sys.argv)
        
        # Create data panel with category names
        category_names = ["Office Supplies", "Meals and Entertainment", "Travel Expenses"]
        data_panel = DataPanelWidget(category_names=category_names)
        
        # Check if category combo exists
        if hasattr(data_panel, 'category_combo'):
            print("✅ Category combo found in data panel")
            
            # Check if categories are loaded
            combo_count = data_panel.category_combo.count()
            print(f"✅ Category combo has {combo_count} items (including empty option)")
            
            if combo_count > 1:  # Should have empty option + categories
                print("✅ Categories loaded in combo")
            else:
                print("❌ Categories not loaded in combo")
                return False
        else:
            print("❌ Category combo not found in data panel")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Category data panel test failed: {e}")
        return False

def test_category_file_manager():
    """Test that file manager handles category field."""
    print("🧪 Testing Category File Manager Integration...")
    
    try:
        from ocrinvoice.utils.file_manager import FileManager
        
        # Create file manager
        config = {
            "file_management": {
                "rename_format": "{project}_{documentType}_{category}_{company}_{date}_{total}.pdf"
            }
        }
        file_manager = FileManager(config)
        
        # Test with sample data including category
        test_data = {
            "project": "test-project",
            "documentType": "invoice",
            "category": "Office Supplies",
            "company": "Test Company",
            "date": "2024-01-15",
            "total": "100.00"
        }
        
        # Format filename
        filename = file_manager.format_filename(test_data)
        print(f"✅ Formatted filename: {filename}")
        
        if "Office_Supplies" in filename:
            print("✅ Category included in filename")
        else:
            print("❌ Category not included in filename")
            return False
        
        # Test with missing category
        test_data_no_category = {
            "project": "test-project",
            "documentType": "invoice",
            "company": "Test Company",
            "date": "2024-01-15",
            "total": "100.00"
        }
        
        filename_no_category = file_manager.format_filename(test_data_no_category)
        print(f"✅ Filename without category: {filename_no_category}")
        
        if "unknown-category" in filename_no_category:
            print("✅ Default category used when missing")
        else:
            print("❌ Default category not used when missing")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Category file manager test failed: {e}")
        return False

def main():
    """Run all category integration tests."""
    print("🚀 Starting Category Integration Tests...")
    print("=" * 60)
    
    # Test category template
    template_success = test_category_template()
    
    # Test category data panel
    panel_success = test_category_data_panel()
    
    # Test category file manager
    manager_success = test_category_file_manager()
    
    print("=" * 60)
    print("📊 Test Results:")
    print(f"   Category Template: {'✅ PASS' if template_success else '❌ FAIL'}")
    print(f"   Category Data Panel: {'✅ PASS' if panel_success else '❌ FAIL'}")
    print(f"   Category File Manager: {'✅ PASS' if manager_success else '❌ FAIL'}")
    
    if all([template_success, panel_success, manager_success]):
        print("🎉 All category integration tests passed!")
        return 0
    else:
        print("⚠️  Some category integration tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 