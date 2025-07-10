#!/usr/bin/env python3
"""
Advanced usage example for Invoice OCR Parser.

This example demonstrates advanced features including batch processing,
custom configuration, and error handling.
"""

import sys
import json
import csv
from pathlib import Path
from typing import List, Dict, Any

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ocrinvoice import InvoiceParser, CreditCardBillParser
from ocrinvoice.core import OCREngine
from ocrinvoice.business import BusinessAliasManager


def batch_processing_example():
    """Demonstrate batch processing of multiple PDFs."""
    print("=== Batch Processing Example ===")

    # Initialize parser
    parser = InvoiceParser()

    # Directory containing PDF files
    pdf_directory = Path("path/to/pdf/directory")

    if not pdf_directory.exists():
        print(f"Directory not found: {pdf_directory}")
        print("Please update the pdf_directory variable with a valid directory.")
        return

    # Find all PDF files
    pdf_files = list(pdf_directory.glob("*.pdf"))

    if not pdf_files:
        print(f"No PDF files found in {pdf_directory}")
        return

    print(f"Found {len(pdf_files)} PDF files")

    results = []
    errors = []

    # Process each PDF
    for pdf_file in pdf_files:
        try:
            print(f"Processing: {pdf_file.name}")
            result = parser.parse(str(pdf_file))
            result["filename"] = pdf_file.name
            results.append(result)
            print(f"✓ Successfully processed {pdf_file.name}")

        except Exception as e:
            error_info = {"filename": pdf_file.name, "error": str(e)}
            errors.append(error_info)
            print(f"✗ Error processing {pdf_file.name}: {e}")

    # Save results
    if results:
        output_file = Path("batch_results.json")
        with open(output_file, "w") as f:
            json.dump(results, f, indent=2)
        print(f"\nResults saved to: {output_file}")

    if errors:
        error_file = Path("batch_errors.json")
        with open(error_file, "w") as f:
            json.dump(errors, f, indent=2)
        print(f"Errors saved to: {error_file}")

    # Summary
    print(f"\nBatch Processing Summary:")
    print(f"  Total files: {len(pdf_files)}")
    print(f"  Successful: {len(results)}")
    print(f"  Errors: {len(errors)}")


def custom_configuration_example():
    """Demonstrate custom configuration usage."""
    print("\n=== Custom Configuration Example ===")

    # Custom configuration
    config = {
        "ocr": {
            "tesseract_path": None,  # Auto-detect
            "language": "eng",
            "config": "--psm 6 --oem 3",
            "timeout": 60,
        },
        "parser": {"confidence_threshold": 0.8, "max_retries": 5, "debug_mode": True},
        "business": {
            "use_database": False,
            "alias_file": "custom_aliases.json",
            "auto_save_aliases": True,
        },
    }

    # Initialize parser with custom config
    parser = InvoiceParser(config=config)

    # Example PDF path
    pdf_path = "path/to/your/invoice.pdf"

    if not Path(pdf_path).exists():
        print(f"PDF file not found: {pdf_path}")
        return

    try:
        print(f"Parsing with custom configuration: {pdf_path}")
        result = parser.parse(pdf_path)

        print("\nParsing Results with Custom Config:")
        print(json.dumps(result, indent=2))

    except Exception as e:
        print(f"Error parsing with custom config: {e}")


def business_alias_management_example():
    """Demonstrate business alias management."""
    print("\n=== Business Alias Management Example ===")

    # Initialize alias manager
    alias_manager = BusinessAliasManager()

    # Add some aliases
    aliases = {
        "SCOTIA": "Scotiabank",
        "TD": "TD Bank",
        "RBC": "Royal Bank of Canada",
        "BMO": "Bank of Montreal",
        "CIBC": "Canadian Imperial Bank of Commerce",
    }

    for alias, full_name in aliases.items():
        alias_manager.add_alias(alias, full_name)
        print(f"Added alias: {alias} -> {full_name}")

    # Test alias resolution
    test_names = ["SCOTIA", "TD BANK", "RBC", "UNKNOWN"]

    print("\nAlias Resolution Test:")
    for name in test_names:
        resolved = alias_manager.resolve_alias(name)
        print(f"  {name} -> {resolved}")

    # Save aliases to file
    alias_file = Path("custom_aliases.json")
    alias_manager.save_aliases(alias_file)
    print(f"\nAliases saved to: {alias_file}")


def csv_export_example():
    """Demonstrate CSV export functionality."""
    print("\n=== CSV Export Example ===")

    # Sample data (in real usage, this would come from parsing)
    sample_data = [
        {
            "filename": "invoice1.pdf",
            "company": "ABC Company",
            "total": "$100.00",
            "date": "2024-01-15",
            "confidence": 0.95,
        },
        {
            "filename": "invoice2.pdf",
            "company": "XYZ Corp",
            "total": "$250.50",
            "date": "2024-01-16",
            "confidence": 0.87,
        },
        {
            "filename": "invoice3.pdf",
            "company": "DEF Industries",
            "total": "$75.25",
            "date": "2024-01-17",
            "confidence": 0.92,
        },
    ]

    # Export to CSV
    csv_file = Path("parsing_results.csv")

    if sample_data:
        fieldnames = sample_data[0].keys()

        with open(csv_file, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(sample_data)

        print(f"Results exported to CSV: {csv_file}")
        print(f"Exported {len(sample_data)} records")

    # Display sample data
    print("\nSample Data:")
    for record in sample_data:
        print(f"  {record['filename']}: {record['company']} - {record['total']}")


def error_handling_example():
    """Demonstrate comprehensive error handling."""
    print("\n=== Error Handling Example ===")

    parser = InvoiceParser()

    # Test cases with different error scenarios
    test_cases = [
        "nonexistent_file.pdf",
        "invalid_file.txt",
        "path/to/your/actual/invoice.pdf",  # Replace with real file
    ]

    for test_file in test_cases:
        print(f"\nTesting: {test_file}")

        try:
            result = parser.parse(test_file)
            print(f"✓ Success: {result.get('company', 'Unknown')}")

        except FileNotFoundError:
            print("✗ Error: File not found")

        except PermissionError:
            print("✗ Error: Permission denied")

        except ValueError as e:
            print(f"✗ Error: Invalid file format - {e}")

        except Exception as e:
            print(f"✗ Error: Unexpected error - {e}")


def main():
    """Main function to run all advanced examples."""
    print("Invoice OCR Parser - Advanced Usage Examples")
    print("=" * 60)

    # Run examples
    batch_processing_example()
    custom_configuration_example()
    business_alias_management_example()
    csv_export_example()
    error_handling_example()

    print("\n" + "=" * 60)
    print("Advanced examples completed!")
    print("=" * 60)
    print("To use these examples:")
    print("1. Update file paths with actual files/directories")
    print("2. Run: python examples/advanced_usage.py")
    print("3. Check generated output files")
    print("4. Review error handling and logging")


if __name__ == "__main__":
    main()
