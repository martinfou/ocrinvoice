#!/usr/bin/env python3
"""
Test script for the robust credit card bill parser.
Demonstrates how to use the new CreditCardBillParser class to extract totals from credit card bills.
"""

import os
import sys
from invoice_ocr_parser import CreditCardBillParser, InvoiceOCRParser


def test_credit_card_parser():
    """Test the credit card parser with sample data"""

    # Initialize the credit card parser
    parser = CreditCardBillParser(debug=True)

    # Sample text that might come from a credit card bill
    sample_text = """
    CREDIT CARD STATEMENT

    Account Number: 1234-5678-9012-3456
    Statement Date: 2024-01-15

    Previous Balance: $1,234.56
    Payments: -$500.00
    Purchases: $802.60

    TOTAL À PAYER: 537,16

    Payment Due Date: 2024-02-15
    Minimum Payment: $25.00
    """

    print("Testing Credit Card Bill Parser")
    print("=" * 50)
    print("Sample text:")
    print(sample_text)
    print("-" * 50)

    # Test the total extraction
    total = parser.extract_credit_card_total(sample_text, expected_total=537.16)

    print(f"Extracted total: {total}")
    print(f"Expected total: 537.16")
    print(f"Match: {total == '537.16'}")

    return total == "537.16"


def test_ocr_correction():
    """Test OCR correction with common misreadings"""

    parser = CreditCardBillParser(debug=True)

    # Test cases with common OCR errors
    test_cases = [
        ("537,l6", "537.16"),  # l misread as 1
        ("537,O6", "537.06"),  # O misread as 0
        ("537,S6", "537.56"),  # S misread as 5
        ("537,G6", "537.66"),  # G misread as 6
        ("537,B6", "537.86"),  # B misread as 8
        ("537,Z6", "537.26"),  # Z misread as 2
        ("537,A6", "537.46"),  # A misread as 4
        ("537,E6", "537.36"),  # E misread as 3
        ("537,T6", "537.76"),  # T misread as 7
    ]

    print("\nTesting OCR Correction")
    print("=" * 50)

    for input_text, expected in test_cases:
        # Create sample text with the OCR error
        sample_text = f"TOTAL À PAYER: {input_text}"
        total = parser.extract_credit_card_total(sample_text)
        print(
            f"Input: {input_text} -> Output: {total} -> Expected: {expected} -> Match: {total == expected}"
        )

    return True


def test_different_formats():
    """Test different credit card bill formats"""

    parser = CreditCardBillParser(debug=True)

    test_cases = [
        # French format with comma decimal separator
        ("TOTAL À PAYER: 537,16", "537.16"),
        ("MONTANT À PAYER: 1,234,56", "1234.56"),
        ("Solde à recevoir: 2,500,00", "2500.00"),
        # English format with dot decimal separator
        ("PAYMENT DUE: $537.16", "537.16"),
        ("AMOUNT DUE: 1,234.56", "1234.56"),
        ("BALANCE DUE: 2,500.00", "2500.00"),
        # Mixed formats
        ("TOTAL: 537,16", "537.16"),
        ("MONTANT: 1,234.56", "1234.56"),
        ("BALANCE: 2,500,00", "2500.00"),
    ]

    print("\nTesting Different Formats")
    print("=" * 50)

    for input_text, expected in test_cases:
        total = parser.extract_credit_card_total(input_text)
        print(
            f"Input: {input_text} -> Output: {total} -> Expected: {expected} -> Match: {total == expected}"
        )

    return True


def test_priority_system():
    """Test the priority system for different patterns"""

    parser = CreditCardBillParser(debug=True)

    # Test text with multiple amounts to see which one gets selected
    test_text = """
    CREDIT CARD STATEMENT

    Previous Balance: $1,234.56
    Payments: -$500.00
    Purchases: $802.60

    TOTAL À PAYER: 537,16

    Payment Due Date: 2024-02-15
    Minimum Payment: $25.00
    Late Fee: $35.00
    """

    print("\nTesting Priority System")
    print("=" * 50)
    print("Test text with multiple amounts:")
    print(test_text)
    print("-" * 50)

    total = parser.extract_credit_card_total(test_text)
    print(f"Selected total: {total}")
    print(f"Expected: 537.16")
    print(f"Match: {total == '537.16'}")

    return total == "537.16"


def main():
    """Run all tests"""

    print("Credit Card Bill Parser Tests")
    print("=" * 60)

    tests = [
        ("Basic Credit Card Parser", test_credit_card_parser),
        ("OCR Correction", test_ocr_correction),
        ("Different Formats", test_different_formats),
        ("Priority System", test_priority_system),
    ]

    results = []

    for test_name, test_func in tests:
        print(f"\nRunning test: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
            print(f"✓ {test_name}: {'PASSED' if result else 'FAILED'}")
        except Exception as e:
            print(f"✗ {test_name}: ERROR - {e}")
            results.append((test_name, False))

    print("\n" + "=" * 60)
    print("Test Results Summary:")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "PASSED" if result else "FAILED"
        print(f"{test_name}: {status}")

    print(f"\nOverall: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed!")
    else:
        print("❌ Some tests failed.")

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
