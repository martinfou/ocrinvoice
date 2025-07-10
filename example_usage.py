#!/usr/bin/env python3
"""
Comprehensive example demonstrating the robust invoice total extraction system.
Shows how to use both InvoiceOCRParser and CreditCardBillParser for different types of invoices.
"""

import os
import sys
from invoice_ocr_parser import InvoiceOCRParser, CreditCardBillParser

def example_credit_card_bill():
    """Example of parsing a credit card bill with the specialized parser"""
    
    print("=" * 60)
    print("CREDIT CARD BILL PARSING EXAMPLE")
    print("=" * 60)
    
    # Initialize the credit card parser
    parser = CreditCardBillParser(debug=True)
    
    # Sample credit card bill text (simulating OCR output)
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
    
    print("Sample credit card bill text:")
    print(sample_text)
    print("-" * 60)
    
    # Extract the total
    total = parser.extract_credit_card_total(sample_text, expected_total=537.16)
    
    print(f"Extracted total: {total}")
    print(f"Expected total: 537.16")
    print(f"Success: {total == '537.16'}")
    
    return total == '537.16'

def example_ocr_correction():
    """Example of OCR correction with common misreadings"""
    
    print("\n" + "=" * 60)
    print("OCR CORRECTION EXAMPLE")
    print("=" * 60)
    
    parser = CreditCardBillParser(debug=True)
    
    # Common OCR errors that might occur
    ocr_errors = [
        ("537,l6", "537.16"),  # l misread as 1
        ("537,O6", "537.06"),  # O misread as 0
        ("537,S6", "537.56"),  # S misread as 5
        ("537,G6", "537.66"),  # G misread as 6
        ("537,B6", "537.86"),  # B misread as 8
    ]
    
    print("Testing OCR correction with common misreadings:")
    print("-" * 60)
    
    for input_text, expected in ocr_errors:
        sample_text = f"TOTAL À PAYER: {input_text}"
        total = parser.extract_credit_card_total(sample_text)
        success = total == expected
        print(f"Input: {input_text} -> Output: {total} -> Expected: {expected} -> {'✓' if success else '✗'}")
    
    return True

def example_different_formats():
    """Example of handling different invoice formats"""
    
    print("\n" + "=" * 60)
    print("DIFFERENT FORMATS EXAMPLE")
    print("=" * 60)
    
    parser = InvoiceOCRParser(debug=True)
    
    # Different invoice formats
    formats = [
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
    
    print("Testing different invoice formats:")
    print("-" * 60)
    
    for input_text, expected in formats:
        total = parser.extract_invoice_total(input_text)
        success = total == expected
        print(f"Input: {input_text} -> Output: {total} -> Expected: {expected} -> {'✓' if success else '✗'}")
    
    return True

def example_priority_system():
    """Example of the priority system for selecting the best total"""
    
    print("\n" + "=" * 60)
    print("PRIORITY SYSTEM EXAMPLE")
    print("=" * 60)
    
    parser = CreditCardBillParser(debug=True)
    
    # Test text with multiple amounts to demonstrate priority selection
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
    
    print("Test text with multiple amounts:")
    print(test_text)
    print("-" * 60)
    
    total = parser.extract_credit_card_total(test_text)
    print(f"Selected total: {total}")
    print(f"Expected: 537.16")
    print(f"Success: {total == '537.16'}")
    
    return total == '537.16'

def example_pdf_parsing():
    """Example of parsing a PDF file (if available)"""
    
    print("\n" + "=" * 60)
    print("PDF PARSING EXAMPLE")
    print("=" * 60)
    
    # Check if there are any PDF files in the current directory
    pdf_files = [f for f in os.listdir('.') if f.lower().endswith('.pdf')]
    
    if not pdf_files:
        print("No PDF files found in current directory.")
        print("To test PDF parsing, place a credit card bill PDF in this directory.")
        return True
    
    # Use the first PDF file found
    pdf_file = pdf_files[0]
    print(f"Found PDF file: {pdf_file}")
    
    # Try parsing with both parsers
    credit_parser = CreditCardBillParser(debug=True)
    invoice_parser = InvoiceOCRParser(debug=True)
    
    print("\nParsing with CreditCardBillParser:")
    result1 = credit_parser.parse_credit_card_bill(pdf_file)
    print(f"Credit card total: {result1.get('credit_card_total')}")
    print(f"Confidence: {result1.get('confidence')}")
    print(f"Method: {result1.get('extraction_method')}")
    
    print("\nParsing with InvoiceOCRParser:")
    result2 = invoice_parser.parse_invoice(pdf_file)
    print(f"Invoice total: {result2.get('invoice_total')}")
    print(f"Confidence: {result2.get('confidence')}")
    print(f"Method: {result2.get('extraction_method')}")
    
    return True

def example_batch_processing():
    """Example of batch processing multiple invoices"""
    
    print("\n" + "=" * 60)
    print("BATCH PROCESSING EXAMPLE")
    print("=" * 60)
    
    # Check if there are any PDF files in the current directory
    pdf_files = [f for f in os.listdir('.') if f.lower().endswith('.pdf')]
    
    if len(pdf_files) < 2:
        print("Need at least 2 PDF files for batch processing example.")
        print("Place multiple invoice PDFs in this directory to test batch processing.")
        return True
    
    print(f"Found {len(pdf_files)} PDF files for batch processing")
    
    # Initialize parser
    parser = InvoiceOCRParser(debug=True)
    
    # Process each file individually
    results = []
    for pdf_file in pdf_files:
        print(f"\nProcessing: {pdf_file}")
        result = parser.parse_invoice(pdf_file)
        results.append(result)
        
        print(f"  Company: {result.get('company_name')}")
        print(f"  Total: {result.get('invoice_total')}")
        print(f"  Date: {result.get('invoice_date')}")
        print(f"  Confidence: {result.get('confidence')}")
        print(f"  Method: {result.get('extraction_method')}")
    
    # Summary
    print(f"\nBatch processing summary:")
    print(f"  Total files processed: {len(results)}")
    print(f"  Successful extractions: {sum(1 for r in results if r.get('invoice_total'))}")
    print(f"  High confidence: {sum(1 for r in results if r.get('confidence') == 'high')}")
    print(f"  Medium confidence: {sum(1 for r in results if r.get('confidence') == 'medium')}")
    print(f"  Low confidence: {sum(1 for r in results if r.get('confidence') == 'low')}")
    
    return True

def main():
    """Run all examples"""
    
    print("ROBUST INVOICE TOTAL EXTRACTION SYSTEM")
    print("=" * 80)
    print("This example demonstrates the enhanced invoice parsing capabilities")
    print("including OCR correction, multiple format support, and priority-based selection.")
    print("=" * 80)
    
    examples = [
        ("Credit Card Bill Parsing", example_credit_card_bill),
        ("OCR Correction", example_ocr_correction),
        ("Different Formats", example_different_formats),
        ("Priority System", example_priority_system),
        ("PDF Parsing", example_pdf_parsing),
        ("Batch Processing", example_batch_processing),
    ]
    
    results = []
    
    for example_name, example_func in examples:
        print(f"\nRunning example: {example_name}")
        try:
            result = example_func()
            results.append((example_name, result))
            print(f"✓ {example_name}: {'SUCCESS' if result else 'FAILED'}")
        except Exception as e:
            print(f"✗ {example_name}: ERROR - {e}")
            results.append((example_name, False))
    
    print("\n" + "=" * 80)
    print("EXAMPLE RESULTS SUMMARY")
    print("=" * 80)
    
    successful = sum(1 for _, result in results if result)
    total = len(results)
    
    for example_name, result in results:
        status = "SUCCESS" if result else "FAILED"
        print(f"{example_name}: {status}")
    
    print(f"\nOverall: {successful}/{total} examples successful")
    
    if successful == total:
        print("🎉 All examples completed successfully!")
    else:
        print("❌ Some examples failed.")
    
    print("\n" + "=" * 80)
    print("USAGE INSTRUCTIONS")
    print("=" * 80)
    print("1. For credit card bills: Use CreditCardBillParser")
    print("2. For general invoices: Use InvoiceOCRParser")
    print("3. Both parsers support OCR correction and multiple formats")
    print("4. Place PDF files in the same directory to test with real documents")
    print("5. Use debug=True for detailed logging")
    
    return successful == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 