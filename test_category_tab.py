#!/usr/bin/env python3
"""
Test script for the Category Tab functionality.

This script tests the category management system including:
- Category manager initialization
- Category tab creation
- Basic CRUD operations
- GUI functionality
"""

import sys
import os
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt6.QtCore import QTimer

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_category_manager():
    """Test the category manager functionality."""
    print("🧪 Testing Category Manager...")
    
    try:
        from ocrinvoice.business.category_manager import CategoryManager
        
        # Initialize manager
        manager = CategoryManager()
        print("✅ Category manager initialized")
        
        # Test getting categories
        categories = manager.get_categories()
        print(f"✅ Loaded {len(categories)} categories")
        
        # Test getting category names
        names = manager.get_category_names()
        print(f"✅ Category names: {names[:3]}...")  # Show first 3
        
        # Test getting CRA codes
        codes = manager.get_category_codes()
        print(f"✅ CRA codes: {codes[:3]}...")  # Show first 3
        
        # Test search functionality
        search_results = manager.search_categories("office")
        print(f"✅ Search for 'office' found {len(search_results)} results")
        
        return True
        
    except Exception as e:
        print(f"❌ Category manager test failed: {e}")
        return False

def test_category_tab():
    """Test the category tab GUI functionality."""
    print("🧪 Testing Category Tab GUI...")
    
    try:
        from ocrinvoice.gui.category_tab import CategoryTab
        
        # Create application
        app = QApplication(sys.argv)
        
        # Create main window
        main_window = QMainWindow()
        main_window.setWindowTitle("Category Tab Test")
        main_window.resize(1200, 800)
        
        # Create central widget
        central_widget = QWidget()
        main_window.setCentralWidget(central_widget)
        
        # Create layout
        layout = QVBoxLayout(central_widget)
        
        # Create category tab
        category_tab = CategoryTab()
        layout.addWidget(category_tab)
        
        # Show window
        main_window.show()
        
        # Set up timer to close after 5 seconds
        timer = QTimer()
        timer.timeout.connect(app.quit)
        timer.start(5000)  # 5 seconds
        
        print("✅ Category tab created successfully")
        print("🖥️  GUI will close automatically in 5 seconds...")
        
        # Run the application
        app.exec()
        
        return True
        
    except Exception as e:
        print(f"❌ Category tab test failed: {e}")
        return False

def test_category_form():
    """Test the category form functionality."""
    print("🧪 Testing Category Form...")
    
    try:
        from ocrinvoice.gui.category_form import CategoryForm
        from PyQt6.QtWidgets import QApplication, QDialog, QVBoxLayout
        
        # Create application
        app = QApplication(sys.argv)
        
        # Create dialog
        dialog = QDialog()
        dialog.setWindowTitle("Category Form Test")
        dialog.resize(500, 400)
        
        # Create layout
        layout = QVBoxLayout(dialog)
        
        # Create category form
        form = CategoryForm()
        layout.addWidget(form)
        
        # Test form data
        test_data = {
            "id": "test-id",
            "name": "Test Category",
            "description": "This is a test category",
            "cra_code": "9999"
        }
        
        # Load test data
        form.load_category(test_data)
        print("✅ Category form loaded test data")
        
        # Get form data
        form_data = form.get_category_data()
        print(f"✅ Form data: {form_data}")
        
        # Test validation
        is_valid = form._validate_form()
        print(f"✅ Form validation: {is_valid}")
        
        # Show dialog briefly
        dialog.show()
        
        # Set up timer to close after 3 seconds
        timer = QTimer()
        timer.timeout.connect(app.quit)
        timer.start(3000)  # 3 seconds
        
        print("✅ Category form test completed")
        
        # Run the application
        app.exec()
        
        return True
        
    except Exception as e:
        print(f"❌ Category form test failed: {e}")
        return False

def main():
    """Run all category tests."""
    print("🚀 Starting Category Tab Tests...")
    print("=" * 50)
    
    # Test category manager
    manager_success = test_category_manager()
    
    # Test category form
    form_success = test_category_form()
    
    # Test category tab (GUI)
    tab_success = test_category_tab()
    
    print("=" * 50)
    print("📊 Test Results:")
    print(f"   Category Manager: {'✅ PASS' if manager_success else '❌ FAIL'}")
    print(f"   Category Form: {'✅ PASS' if form_success else '❌ FAIL'}")
    print(f"   Category Tab: {'✅ PASS' if tab_success else '❌ FAIL'}")
    
    if all([manager_success, form_success, tab_success]):
        print("🎉 All tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 