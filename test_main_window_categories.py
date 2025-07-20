#!/usr/bin/env python3
"""
Test script to verify the main window includes the categories tab.
"""

import sys
import os
from PyQt6.QtWidgets import QApplication

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_main_window_categories():
    """Test that the main window includes the categories tab."""
    print("🧪 Testing Main Window Categories Integration...")
    
    try:
        from ocrinvoice.gui.ocr_main_window import OCRMainWindow
        
        # Create application
        app = QApplication(sys.argv)
        
        # Create main window
        main_window = OCRMainWindow()
        
        # Check if categories tab exists
        tab_widget = main_window.tab_widget
        tab_count = tab_widget.count()
        
        print(f"✅ Main window created with {tab_count} tabs")
        
        # Find categories tab
        categories_tab_index = -1
        for i in range(tab_count):
            tab_name = tab_widget.tabText(i)
            print(f"   Tab {i}: {tab_name}")
            if tab_name == "Categories":
                categories_tab_index = i
                break
        
        if categories_tab_index >= 0:
            print(f"✅ Categories tab found at index {categories_tab_index}")
            
            # Switch to categories tab
            tab_widget.setCurrentIndex(categories_tab_index)
            print("✅ Successfully switched to Categories tab")
            
            return True
        else:
            print("❌ Categories tab not found")
            return False
            
    except Exception as e:
        print(f"❌ Main window test failed: {e}")
        return False

def main():
    """Run the main window test."""
    print("🚀 Testing Main Window Categories Integration...")
    print("=" * 60)
    
    success = test_main_window_categories()
    
    print("=" * 60)
    if success:
        print("🎉 Main window categories integration test passed!")
        return 0
    else:
        print("⚠️  Main window categories integration test failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 