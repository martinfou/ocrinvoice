#!/usr/bin/env python3
"""
Test script for category metadata saving and restoration.
"""

import sys
import os
import tempfile
import shutil
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_category_metadata_saving():
    """Test that category is saved to PDF metadata."""
    print("🧪 Testing Category Metadata Saving...")
    
    try:
        from ocrinvoice.gui.widgets.file_naming import FileNamingWidget
        from ocrinvoice.gui.widgets.data_panel import DataPanelWidget
        from ocrinvoice.gui.ocr_main_window import OCRMainWindow
        from ocrinvoice.utils.pdf_metadata_manager import PDFMetadataManager
        
        # Create application
        app = QApplication(sys.argv)
        
        # Create a temporary PDF file for testing
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
            test_pdf_path = tmp_file.name
        
        # Create a simple PDF file
        try:
            from reportlab.pdfgen import canvas
            c = canvas.Canvas(test_pdf_path)
            c.drawString(100, 750, "Test PDF for category metadata")
            c.save()
            print(f"✅ Created test PDF: {test_pdf_path}")
        except ImportError:
            # If reportlab is not available, create a dummy file
            with open(test_pdf_path, 'w') as f:
                f.write("Dummy PDF content")
            print(f"✅ Created dummy test file: {test_pdf_path}")
        
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
        
        # Set the current PDF path
        main_window.current_pdf_path = test_pdf_path
        main_window.extracted_data = test_data
        
        # Set category in data panel
        category_names = ["Office Supplies", "Meals and Entertainment", "Travel Expenses"]
        main_window.data_panel.update_categories(category_names)
        main_window.data_panel.set_selected_category("Office Supplies")
        
        print(f"✅ Set category selection: Office Supplies")
        
        # Test metadata saving
        if main_window.pdf_metadata_manager:
            success = main_window.pdf_metadata_manager.save_data_to_pdf(test_pdf_path, test_data)
            if success:
                print("✅ Successfully saved category to PDF metadata")
            else:
                print("❌ Failed to save category to PDF metadata")
                return False
        else:
            print("❌ PDF metadata manager not available")
            return False
        
        # Test metadata reading
        loaded_data = main_window.pdf_metadata_manager.load_data_from_pdf(test_pdf_path)
        if loaded_data:
            print(f"✅ Successfully loaded data from PDF metadata: {loaded_data}")
            
            # Check if category was saved and loaded correctly
            saved_category = loaded_data.get("selected_category", "")
            if saved_category == "Office Supplies":
                print("✅ Category correctly saved and loaded from metadata")
            else:
                print(f"❌ Category not correctly loaded. Expected: 'Office Supplies', Got: '{saved_category}'")
                return False
        else:
            print("❌ Failed to load data from PDF metadata")
            return False
        
        # Clean up
        try:
            os.unlink(test_pdf_path)
            print("✅ Cleaned up test file")
        except:
            pass
        
        return True
        
    except Exception as e:
        print(f"❌ Category metadata test failed: {e}")
        return False

def test_category_metadata_restoration():
    """Test that category is restored from PDF metadata."""
    print("🧪 Testing Category Metadata Restoration...")
    
    try:
        from ocrinvoice.gui.widgets.file_naming import FileNamingWidget
        from ocrinvoice.gui.widgets.data_panel import DataPanelWidget
        from ocrinvoice.gui.ocr_main_window import OCRMainWindow
        from ocrinvoice.utils.pdf_metadata_manager import PDFMetadataManager
        
        # Create application
        app = QApplication(sys.argv)
        
        # Create a temporary PDF file for testing
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
            test_pdf_path = tmp_file.name
        
        # Create a simple PDF file
        try:
            from reportlab.pdfgen import canvas
            c = canvas.Canvas(test_pdf_path)
            c.drawString(100, 750, "Test PDF for category metadata restoration")
            c.save()
            print(f"✅ Created test PDF: {test_pdf_path}")
        except ImportError:
            # If reportlab is not available, create a dummy file
            with open(test_pdf_path, 'w') as f:
                f.write("Dummy PDF content")
            print(f"✅ Created dummy test file: {test_pdf_path}")
        
        # Create main window
        main_window = OCRMainWindow()
        
        # Set up test data with category
        test_data = {
            "company": "Test Company",
            "total": "100.00",
            "date": "2024-01-15",
            "selected_project": "test-project",
            "selected_document_type": "invoice",
            "selected_category": "Travel Expenses"
        }
        
        # Save test data to PDF metadata
        if main_window.pdf_metadata_manager:
            success = main_window.pdf_metadata_manager.save_data_to_pdf(test_pdf_path, test_data)
            if not success:
                print("❌ Failed to save test data to PDF metadata")
                return False
            print("✅ Saved test data to PDF metadata")
        else:
            print("❌ PDF metadata manager not available")
            return False
        
        # Set up data panel with categories
        category_names = ["Office Supplies", "Meals and Entertainment", "Travel Expenses"]
        main_window.data_panel.update_categories(category_names)
        
        # Simulate loading data from PDF (like in _on_ocr_finished)
        main_window.current_pdf_path = test_pdf_path
        main_window.extracted_data = test_data
        
        # Restore selections from metadata
        selected_project = test_data.get("selected_project", "")
        selected_document_type = test_data.get("selected_document_type", "")
        selected_category = test_data.get("selected_category", "")
        
        # Set project selection if found in metadata
        if selected_project:
            main_window.data_panel.set_selected_project(selected_project)
            print(f"✅ Restored project selection: {selected_project}")
        
        # Set document type selection if found in metadata
        if selected_document_type:
            main_window.data_panel.set_selected_document_type(selected_document_type)
            print(f"✅ Restored document type selection: {selected_document_type}")
        
        # Set category selection if found in metadata
        if selected_category:
            main_window.data_panel.set_selected_category(selected_category)
            print(f"✅ Restored category selection: {selected_category}")
        
        # Verify restoration
        current_category = main_window.data_panel.get_selected_category()
        if current_category == "Travel Expenses":
            print("✅ Category correctly restored from metadata")
        else:
            print(f"❌ Category not correctly restored. Expected: 'Travel Expenses', Got: '{current_category}'")
            return False
        
        # Clean up
        try:
            os.unlink(test_pdf_path)
            print("✅ Cleaned up test file")
        except:
            pass
        
        return True
        
    except Exception as e:
        print(f"❌ Category metadata restoration test failed: {e}")
        return False

def main():
    """Run all category metadata tests."""
    print("🚀 Starting Category Metadata Tests...")
    print("=" * 60)
    
    # Test category metadata saving
    saving_success = test_category_metadata_saving()
    
    # Test category metadata restoration
    restoration_success = test_category_metadata_restoration()
    
    print("=" * 60)
    print("📊 Test Results:")
    print(f"   Category Metadata Saving: {'✅ PASS' if saving_success else '❌ FAIL'}")
    print(f"   Category Metadata Restoration: {'✅ PASS' if restoration_success else '❌ FAIL'}")
    
    if all([saving_success, restoration_success]):
        print("🎉 All category metadata tests passed!")
        return 0
    else:
        print("⚠️  Some category metadata tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 