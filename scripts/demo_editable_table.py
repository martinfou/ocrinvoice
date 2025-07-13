#!/usr/bin/env python3
"""
Editable Table Demo Script

This script demonstrates the new editable table feature with real-time 
file naming updates.
"""

import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def print_header(title: str) -> None:
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(f" {title}")
    print("=" * 60)


def print_step(step: int, description: str) -> None:
    """Print a formatted step."""
    print(f"\n{step}. {description}")
    print("-" * 40)


def print_success(message: str) -> None:
    """Print a success message."""
    print(f"✅ {message}")


def print_info(message: str) -> None:
    """Print an info message."""
    print(f"ℹ️  {message}")


def print_warning(message: str) -> None:
    """Print a warning message."""
    print(f"⚠️  {message}")


def demo_editable_table_features() -> None:
    """Demonstrate the editable table features."""
    print_header("Editable Table Features")

    print_step(1, "Editable Data Table")
    print_info("The extracted data table is now fully editable:")
    print("  • Double-click any value in the 'Value' column to edit")
    print("  • Field names and confidence scores are read-only")
    print("  • Visual feedback shows which cells are editable")
    print("  • Smart formatting for currency and percentage values")

    print_step(2, "Real-time File Naming Updates")
    print_info("Changes to data immediately update file name preview:")
    print("  • Edit company name → see file name change instantly")
    print("  • Edit total amount → file name updates with new amount")
    print("  • Edit invoice date → date in file name updates")
    print("  • Edit invoice number → number in file name updates")

    print_step(3, "Smart Data Processing")
    print_info("The system intelligently processes edited values:")
    print("  • Currency amounts: Accepts '123.45' or '$123.45'")
    print("  • Percentages: Accepts '85' or '85%'")
    print("  • Boolean values: Accepts 'Yes', 'True', '1' for true")
    print("  • Text fields: Preserves original formatting")

    print_step(4, "User Experience Features")
    print_info("Enhanced user experience with visual feedback:")
    print("  • Status bar shows when data is updated")
    print("  • Tooltips explain editing capabilities")
    print("  • Visual indicators for editable vs read-only cells")
    print("  • Automatic file name preview refresh")


def demo_workflow() -> None:
    """Demonstrate the complete editable workflow."""
    print_header("Complete Editable Workflow")

    print_step(1, "Load PDF and Extract Data")
    print_info("Start with OCR extraction as usual")
    print("  • Select a PDF file for processing")
    print("  • OCR extracts data and displays in table")
    print("  • Initial file name preview is generated")

    print_step(2, "Review and Edit Data")
    print_info("Examine and correct extracted data")
    print("  • Review all extracted fields")
    print("  • Check confidence scores")
    print("  • Identify any OCR errors")

    print_step(3, "Make Edits")
    print_info("Edit values directly in the table")
    print("  • Double-click any value to edit")
    print("  • Type new value and press Enter")
    print("  • See immediate file name preview update")
    print("  • Status bar confirms data update")

    print_step(4, "Verify File Name")
    print_info("Check the updated file name preview")
    print("  • Switch to File Naming tab")
    print("  • See updated file name with your changes")
    print("  • Adjust template if needed")
    print("  • Rename file when satisfied")


def demo_use_cases() -> None:
    """Demonstrate common use cases for editing."""
    print_header("Common Editing Use Cases")

    print_step(1, "Correct OCR Errors")
    print_info("Fix common OCR mistakes:")
    print("  • Company name: 'R0na' → 'Rona'")
    print("  • Amount: '$1,234.56' → '$1,234.56' (fix formatting)")
    print("  • Date: '2025-01-15' → '2025-01-15' (correct format)")
    print("  • Invoice number: 'INV-00l' → 'INV-001' (fix OCR 'l' vs '1')")

    print_step(2, "Improve Data Quality")
    print_info("Enhance extracted data for better organization:")
    print("  • Standardize company names")
    print("  • Format amounts consistently")
    print("  • Ensure proper date formats")
    print("  • Add missing invoice numbers")

    print_step(3, "Customize for File Naming")
    print_info("Optimize data for your naming preferences:")
    print("  • Shorten long company names")
    print("  • Add prefixes or suffixes")
    print("  • Standardize abbreviations")
    print("  • Ensure unique identifiers")


def demo_technical_details() -> None:
    """Show technical implementation details."""
    print_header("Technical Implementation")

    print_info("The editable table feature includes:")
    print("  • Real-time signal/slot connections")
    print("  • Smart data type conversion")
    print("  • Automatic file naming widget updates")
    print("  • Status bar feedback")
    print("  • Visual editing indicators")

    print_info("Data flow:")
    print("  1. User edits table cell")
    print("  2. Data panel processes change")
    print("  3. Signal emitted with updated data")
    print("  4. Main window receives update")
    print("  5. File naming widget refreshed")
    print("  6. Status bar shows confirmation")


def main() -> None:
    """Main demo function."""
    print_header("Editable Table with Real-time File Naming Demo")
    print_info("This demo showcases the new editable table feature")

    demo_editable_table_features()
    demo_workflow()
    demo_use_cases()
    demo_technical_details()

    print_header("Getting Started")
    print_info("To try the editable table feature:")
    print("  1. Launch the GUI: python run_ocr_gui.py")
    print("  2. Load a PDF file for processing")
    print("  3. Double-click any value in the data table")
    print("  4. Edit the value and press Enter")
    print("  5. Watch the file name preview update instantly!")
    print("  6. Switch to File Naming tab to see the full preview")


if __name__ == "__main__":
    main()
