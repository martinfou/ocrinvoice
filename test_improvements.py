#!/usr/bin/env python3
"""
Test script to validate OCR parser improvements
"""

import os
import sys
from pathlib import Path
from invoice_ocr_parser import InvoiceOCRParser
import pandas as pd


def test_improvements():
    """Test the improved OCR parser on sample PDFs"""

    # Initialize parser with debug mode
    parser = InvoiceOCRParser(debug=True)

    # Test folder
    test_folder = "/Volumes/T7/Dropbox/scan-snap/facture/ocr-test-data"

    if not os.path.exists(test_folder):
        print(f"Test folder not found: {test_folder}")
        return

    # Get sample PDFs (first 5)
    pdf_files = list(Path(test_folder).glob("*.pdf"))[:5]

    if not pdf_files:
        print("No PDF files found for testing")
        return

    print(f"Testing improvements on {len(pdf_files)} sample PDFs...")
    print("=" * 60)

    results = []

    for pdf_file in pdf_files:
        print(f"\nProcessing: {pdf_file.name}")
        print("-" * 40)

        try:
            result = parser.parse_invoice(str(pdf_file))

            print(f"  Company: '{result['company_name']}'")
            print(f"  Total: ${result['invoice_total']}")
            print(f"  Method: {result['extraction_method']}")
            print(f"  Confidence: {result['confidence']}")
            print(f"  Time: {result['processing_time']:.3f}s")

            if result["error"]:
                print(f"  Error: {result['error']}")

            results.append(result)

        except Exception as e:
            print(f"  Error processing {pdf_file.name}: {e}")

    # Summary
    print("\n" + "=" * 60)
    print("IMPROVEMENT TEST SUMMARY")
    print("=" * 60)

    if results:
        df = pd.DataFrame(results)

        print(f"Total files processed: {len(df)}")
        print(f"Successful extractions: {len(df[df['error'].isna()])}")
        print(
            f"Company names found: {len(df[df['company_name'].notna() & (df['company_name'] != '')])}"
        )
        print(f"Totals found: {len(df[df['invoice_total'].notna()])}")

        # Confidence breakdown
        confidence_counts = df["confidence"].value_counts()
        print(f"\nConfidence levels:")
        for level, count in confidence_counts.items():
            print(f"  {level}: {count}")

        # Method breakdown
        method_counts = df["extraction_method"].value_counts()
        print(f"\nExtraction methods:")
        for method, count in method_counts.items():
            print(f"  {method}: {count}")

        # Average processing time
        avg_time = df["processing_time"].mean()
        print(f"\nAverage processing time: {avg_time:.3f}s")

        # Show detailed results
        print(f"\nDetailed results:")
        for result in results:
            print(f"  {Path(result['file_path']).name}:")
            print(f"    Company: '{result['company_name']}'")
            print(f"    Total: ${result['invoice_total']}")
            print(f"    Confidence: {result['confidence']}")
            print(f"    Method: {result['extraction_method']}")


def test_single_file(pdf_path: str):
    """Test a single PDF file with detailed output"""
    parser = InvoiceOCRParser(debug=True)

    print(f"Testing single file: {pdf_path}")
    print("=" * 60)

    result = parser.parse_invoice(pdf_path)

    print(f"Company: '{result['company_name']}'")
    print(f"Total: ${result['invoice_total']}")
    print(f"Method: {result['extraction_method']}")
    print(f"Confidence: {result['confidence']}")
    print(f"Time: {result['processing_time']:.3f}s")

    if result["error"]:
        print(f"Error: {result['error']}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Test specific file
        test_single_file(sys.argv[1])
    else:
        # Test all files
        test_improvements()
