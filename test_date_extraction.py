#!/usr/bin/env python3
"""
Test script for the enhanced Invoice OCR Parser with date extraction
"""

import os
import sys
from invoice_ocr_parser import InvoiceOCRParser, DateExtractor


def test_date_extraction():
    """Test the date extraction functionality with sample text"""

    # Sample invoice text with various date formats
    sample_texts = [
        # French invoice with date
        """
        FACTURE
        Date: 15 janvier 2024
        Client: BMR
        Total à payer: 125.50$
        """,
        # English invoice with date
        """
        INVOICE
        Date: March 20, 2024
        Company: TD Bank
        Total: $89.99
        """,
        # Invoice with numeric date
        """
        RECEIPT
        Date: 2024-02-15
        Business: Hydro-Quebec
        Amount: $156.78
        """,
        # Invoice with DD/MM/YYYY format
        """
        BILL
        Date: 25/12/2023
        Vendor: Scotia Bank
        Total: $234.56
        """,
        # Invoice with OCR errors (common misreadings)
        """
        INVOICE
        Date: 3l/0l/2024  # OCR misread: 31/01/2024
        Company: RBC
        Amount: $67.89
        """,
    ]

    print("Testing Date Extraction Functionality")
    print("=" * 50)

    for i, text in enumerate(sample_texts, 1):
        print(f"\nTest {i}:")
        print("Input text:")
        print(text.strip())

        # Extract date
        extracted_date = DateExtractor.extract_date_from_text(text)

        print(f"Extracted date: {extracted_date}")
        print("-" * 30)


def test_file_renaming():
    """Test the file renaming functionality"""

    # Create a test parser
    parser = InvoiceOCRParser(debug=True)

    # Sample data for testing
    test_cases = [
        {
            "company": "BMR",
            "total": "125.50",
            "date": "2024-01-15",
            "expected": "20240115_BMR_12550.pdf",
        },
        {
            "company": "Hydro-Quebec",
            "total": "156.78",
            "date": "2024-02-20",
            "expected": "20240220_Hydro-Quebec_15678.pdf",
        },
        {
            "company": "TD Bank",
            "total": "89.99",
            "date": "2024-03-10",
            "expected": "20240310_TD_Bank_8999.pdf",
        },
    ]

    print("\nTesting File Renaming Functionality")
    print("=" * 50)

    for i, case in enumerate(test_cases, 1):
        print(f"\nTest {i}:")
        print(f"Company: {case['company']}")
        print(f"Total: {case['total']}")
        print(f"Date: {case['date']}")

        # Test the filename cleaning
        clean_company = parser._clean_filename(case["company"])
        clean_total = case["total"].replace(".", "")
        clean_date = case["date"].replace("-", "")

        new_name = f"{clean_date}_{clean_company}_{clean_total}.pdf"
        print(f"Generated filename: {new_name}")
        print(f"Expected filename: {case['expected']}")
        print("-" * 30)


def test_ocr_corrections():
    """Test OCR correction functionality"""

    print("\nTesting OCR Corrections")
    print("=" * 50)

    # Test cases with common OCR errors
    test_cases = [
        ("3l/0l/2024", "31/01/2024"),  # l -> 1, O -> 0
        ("2S/12/2023", "25/12/2023"),  # S -> 5
        ("1G/03/2024", "16/03/2024"),  # G -> 6
        ("2B/11/2023", "28/11/2023"),  # B -> 8
        ("15/0Z/2024", "15/02/2024"),  # Z -> 2
    ]

    for original, expected in test_cases:
        corrected = DateExtractor.ocr_correct_date(original)
        print(f"Original: {original} -> Corrected: {corrected} -> Expected: {expected}")
        print(f"Match: {'✓' if corrected == expected else '✗'}")


def main():
    """Main test function"""
    print("Invoice OCR Parser - Date Extraction Test Suite")
    print("=" * 60)

    # Test date extraction
    test_date_extraction()

    # Test OCR corrections
    test_ocr_corrections()

    # Test file renaming
    test_file_renaming()

    print("\n" + "=" * 60)
    print("Test suite completed!")
    print("\nTo use the enhanced parser:")
    print("1. Create an InvoiceOCRParser instance")
    print("2. Use parse_invoice() with auto_rename=True for single files")
    print("3. Use parse_and_rename_invoices() for batch processing")
    print("4. Files will be renamed to: date_business_total format")


if __name__ == "__main__":
    main()
