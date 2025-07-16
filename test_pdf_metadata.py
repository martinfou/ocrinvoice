#!/usr/bin/env python3
"""
Test script for PDF metadata functionality.

This script tests the PDFMetadataManager to ensure it can save and load data
from PDF metadata correctly.
"""

import json
import tempfile
import os
from pathlib import Path

# Add the src directory to the Python path
import sys
sys.path.insert(0, str(Path(__file__).parent / "src"))

from ocrinvoice.utils.pdf_metadata_manager import PDFMetadataManager


def create_test_pdf():
    """Create a simple test PDF file."""
    try:
        from PyPDF2 import PdfWriter
        
        # Create a simple PDF
        writer = PdfWriter()
        
        # Create a temporary PDF file
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
            temp_pdf_path = temp_file.name
        
        # Write empty PDF
        with open(temp_pdf_path, 'wb') as output_file:
            writer.write(output_file)
        
        return temp_pdf_path
    except ImportError:
        print("PyPDF2 not available, creating a dummy file")
        # Create a dummy file for testing
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
            temp_file.write(b'%PDF-1.4\n%EOF\n')
            return temp_file.name


def test_pdf_metadata():
    """Test the PDF metadata functionality."""
    print("🧪 Testing PDF Metadata Manager...")
    
    # Create metadata manager
    metadata_manager = PDFMetadataManager()
    
    # Create test PDF
    test_pdf_path = create_test_pdf()
    print(f"📄 Created test PDF: {test_pdf_path}")
    
    try:
        # Test data
        test_data = {
            "company": "Test Company Inc.",
            "total": 123.45,
            "date": "2024-01-15",
            "invoice_number": "INV-2024-001",
            "confidence": 0.85,
            "parser_type": "invoice",
            "is_valid": True
        }
        
        print(f"📝 Test data: {json.dumps(test_data, indent=2)}")
        
        # Test 1: Check if PDF has metadata (should be False initially)
        print("\n🔍 Test 1: Checking for existing metadata...")
        has_data = metadata_manager.has_saved_data(test_pdf_path)
        print(f"   Has saved data: {has_data}")
        assert not has_data, "PDF should not have metadata initially"
        
        # Test 2: Save data to PDF
        print("\n💾 Test 2: Saving data to PDF...")
        print(f"   PDF path: {test_pdf_path}")
        print(f"   PDF exists: {os.path.exists(test_pdf_path)}")
        print(f"   PDF size: {os.path.getsize(test_pdf_path)} bytes")
        
        success = metadata_manager.save_data_to_pdf(test_pdf_path, test_data)
        print(f"   Save successful: {success}")
        
        if not success:
            print("   ❌ Save failed - checking PDF file...")
            print(f"   PDF still exists: {os.path.exists(test_pdf_path)}")
            if os.path.exists(test_pdf_path):
                print(f"   PDF size after save attempt: {os.path.getsize(test_pdf_path)} bytes")
        
        assert success, "Failed to save data to PDF"
        
        # Test 3: Check if PDF has metadata (should be True now)
        print("\n🔍 Test 3: Checking for metadata after save...")
        has_data = metadata_manager.has_saved_data(test_pdf_path)
        print(f"   Has saved data: {has_data}")
        assert has_data, "PDF should have metadata after save"
        
        # Test 4: Load data from PDF
        print("\n📖 Test 4: Loading data from PDF...")
        loaded_data = metadata_manager.load_data_from_pdf(test_pdf_path)
        print(f"   Loaded data: {json.dumps(loaded_data, indent=2)}")
        assert loaded_data is not None, "Failed to load data from PDF"
        
        # Test 5: Verify data integrity
        print("\n✅ Test 5: Verifying data integrity...")
        for key, value in test_data.items():
            assert loaded_data.get(key) == value, f"Data mismatch for {key}: expected {value}, got {loaded_data.get(key)}"
        print("   All data matches!")
        
        # Test 6: Update data
        print("\n🔄 Test 6: Updating data...")
        updated_data = test_data.copy()
        updated_data["total"] = 999.99
        updated_data["company"] = "Updated Company LLC"
        
        success = metadata_manager.save_data_to_pdf(test_pdf_path, updated_data)
        print(f"   Update successful: {success}")
        assert success, "Failed to update data in PDF"
        
        # Test 7: Load updated data
        print("\n📖 Test 7: Loading updated data...")
        final_data = metadata_manager.load_data_from_pdf(test_pdf_path)
        print(f"   Final data: {json.dumps(final_data, indent=2)}")
        assert final_data["total"] == 999.99, "Updated total not saved correctly"
        assert final_data["company"] == "Updated Company LLC", "Updated company not saved correctly"
        
        # Test 8: Remove data
        print("\n🗑️ Test 8: Removing data...")
        success = metadata_manager.remove_data_from_pdf(test_pdf_path)
        print(f"   Remove successful: {success}")
        assert success, "Failed to remove data from PDF"
        
        # Test 9: Verify data is removed
        print("\n🔍 Test 9: Verifying data removal...")
        has_data = metadata_manager.has_saved_data(test_pdf_path)
        print(f"   Has saved data: {has_data}")
        assert not has_data, "PDF should not have metadata after removal"
        
        print("\n🎉 All tests passed! PDF metadata functionality is working correctly.")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        # Clean up
        try:
            os.unlink(test_pdf_path)
            print(f"🧹 Cleaned up test file: {test_pdf_path}")
        except Exception as e:
            print(f"⚠️ Could not clean up test file: {e}")


if __name__ == "__main__":
    test_pdf_metadata() 