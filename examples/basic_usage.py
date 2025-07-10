#!/usr/bin/env python3
"""
Basic usage example for Invoice OCR Parser.

This example demonstrates how to use the Invoice OCR Parser
to extract data from a single PDF invoice.
"""

import sys
import json
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ocrinvoice import InvoiceParser, CreditCardBillParser
from ocrinvoice.core import OCREngine


def basic_invoice_parsing():
    """Demonstrate basic invoice parsing."""
    print("=== Basic Invoice Parsing Example ===")

    # Initialize the parser
    parser = InvoiceParser()

    # Example PDF path (replace with your actual PDF)
    pdf_path = "path/to/your/invoice.pdf"

    if not Path(pdf_path).exists():
        print(f"PDF file not found: {pdf_path}")
        print("Please update the pdf_path variable with a valid PDF file.")
        return

    try:
        # Parse the invoice
        print(f"Parsing invoice: {pdf_path}")
        result = parser.parse(pdf_path)

        # Display results
        print("\nParsing Results:")
        print(json.dumps(result, indent=2))

        # Access specific fields
        print(f"\nCompany: {result.get('company', 'Not found')}")
        print(f"Total Amount: {result.get('total', 'Not found')}")
        print(f"Date: {result.get('date', 'Not found')}")

    except Exception as e:
        print(f"Error parsing invoice: {e}")


def basic_credit_card_parsing():
    """Demonstrate basic credit card bill parsing."""
    print("\n=== Basic Credit Card Bill Parsing Example ===")

    # Initialize the parser
    parser = CreditCardBillParser()

    # Example PDF path (replace with your actual PDF)
    pdf_path = "path/to/your/credit_card_bill.pdf"

    if not Path(pdf_path).exists():
        print(f"PDF file not found: {pdf_path}")
        print("Please update the pdf_path variable with a valid PDF file.")
        return

    try:
        # Parse the credit card bill
        print(f"Parsing credit card bill: {pdf_path}")
        result = parser.parse(pdf_path)

        # Display results
        print("\nParsing Results:")
        print(json.dumps(result, indent=2))

        # Access specific fields
        print(f"\nCard Issuer: {result.get('card_issuer', 'Not found')}")
        print(f"Statement Date: {result.get('statement_date', 'Not found')}")
        print(f"Due Date: {result.get('due_date', 'Not found')}")
        print(f"Total Amount: {result.get('total_amount', 'Not found')}")

    except Exception as e:
        print(f"Error parsing credit card bill: {e}")


def ocr_engine_demo():
    """Demonstrate direct OCR engine usage."""
    print("\n=== OCR Engine Demo ===")

    # Initialize OCR engine
    ocr_engine = OCREngine()

    # Example PDF path (replace with your actual PDF)
    pdf_path = "path/to/your/document.pdf"

    if not Path(pdf_path).exists():
        print(f"PDF file not found: {pdf_path}")
        print("Please update the pdf_path variable with a valid PDF file.")
        return

    try:
        # Extract text from PDF
        print(f"Extracting text from: {pdf_path}")
        text = ocr_engine.extract_text_from_pdf(pdf_path)

        # Display first 500 characters
        print("\nExtracted Text (first 500 characters):")
        print(text[:500] + "..." if len(text) > 500 else text)

        print(f"\nTotal characters extracted: {len(text)}")

    except Exception as e:
        print(f"Error extracting text: {e}")


def main():
    """Main function to run all examples."""
    print("Invoice OCR Parser - Basic Usage Examples")
    print("=" * 50)

    # Run examples
    basic_invoice_parsing()
    basic_credit_card_parsing()
    ocr_engine_demo()

    print("\n" + "=" * 50)
    print("Examples completed!")
    print("=" * 50)
    print("To use these examples:")
    print("1. Update the pdf_path variables with actual PDF files")
    print("2. Run: python examples/basic_usage.py")
    print("3. Check the output for parsing results")


if __name__ == "__main__":
    main()
