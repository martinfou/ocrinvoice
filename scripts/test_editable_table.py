#!/usr/bin/env python3
"""
Test script for editable table text visibility fix.
"""

import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def test_editable_table():
    """Test the editable table functionality."""
    try:
        from PyQt6.QtWidgets import QApplication
        from ocrinvoice.gui.widgets.data_panel import DataPanelWidget

        app = QApplication(sys.argv)

        # Create the data panel
        panel = DataPanelWidget()

        # Test data
        test_data = {
            "company": "Test Company",
            "total": 123.45,
            "date": "2025-01-15",
            "invoice_number": "INV-001",
            "parser_type": "invoice",
            "is_valid": True,
            "confidence": 0.85,
        }

        # Update with test data
        panel.update_data(test_data)

        print("✅ Editable table created successfully")
        print("✅ Test data loaded")
        print("✅ Table should be visible with editable values")
        print("✅ Double-click any value in the 'Value' column to test editing")
        print("✅ Text should remain visible during editing")

        panel.show()

        return app.exec()

    except Exception as e:
        print(f"❌ Error testing editable table: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(test_editable_table())
