#!/usr/bin/env python3
"""
Test script for Invoice OCR Parser
"""

import os
import sys
from pathlib import Path
from invoice_ocr_parser import InvoiceOCRParser

# Add dotenv import for .env file support
try:
    from dotenv import load_dotenv
except ImportError:

    def load_dotenv():
        pass


def load_config():
    """Load configuration from .env file or use defaults."""
    load_dotenv()
    pdf_path = os.getenv("PDF_PATH", os.getcwd())
    return pdf_path


def test_single_invoice():
    """Test parsing a single invoice"""
    # Load path from .env file
    facture_folder = load_config()

    # Find a sample PDF
    pdf_files = list(Path(facture_folder).glob("*.pdf"))

    if not pdf_files:
        print("No PDF files found in the facture folder")
        return

    # Use the first PDF for testing
    test_pdf = str(pdf_files[0])
    print(f"Testing with: {test_pdf}")

    # Initialize parser
    parser = InvoiceOCRParser()

    # Parse the invoice
    result = parser.parse_invoice(test_pdf)

    # Print results
    print("\n" + "=" * 50)
    print("INVOICE PARSING RESULTS")
    print("=" * 50)
    print(f"File: {result['file_path']}")
    print(f"Company Name: {result['company_name']}")
    print(
        f"Invoice Total: {result['invoice_total']}"
        if result["invoice_total"]
        else "Invoice Total: None"
    )
    print(f"Extraction Method: {result['extraction_method']}")
    print(f"Confidence: {result['confidence']}")
    print(f"Processing Time: {result['processing_time']:.2f} seconds")

    if result["error"]:
        print(f"Error: {result['error']}")

    print("=" * 50)


def test_batch_processing():
    """Test batch processing of invoices"""
    facture_folder = load_config()

    print(f"Testing batch processing of invoices in: {facture_folder}")

    # Initialize parser
    parser = InvoiceOCRParser()

    # Parse all invoices
    results_df = parser.parse_invoices_batch(facture_folder, "test_results.csv")

    if not results_df.empty:
        print(f"\nBatch processing complete!")
        print(f"Total files processed: {len(results_df)}")
        print(f"Successful extractions: {len(results_df[results_df['error'].isna()])}")
        print(
            f"Company names found: {len(results_df[results_df['company_name'].notna()])}"
        )
        print(f"Totals found: {len(results_df[results_df['invoice_total'].notna()])}")

        # Show results with company names and totals
        successful_results = results_df[results_df["error"].isna()]
        if not successful_results.empty:
            print(f"\nSuccessful extractions:")
            for _, row in successful_results.head(5).iterrows():
                print(
                    f"  {Path(row['file_path']).name}: {row['company_name']} - {row['invoice_total']}"
                    if row["invoice_total"]
                    else f"  {Path(row['file_path']).name}: {row['company_name']} - No total found"
                )


if __name__ == "__main__":
    print("Invoice OCR Parser Test")
    print("=" * 30)

    # Test single invoice
    print("\n1. Testing single invoice parsing...")
    test_single_invoice()

    # Test batch processing
    print("\n2. Testing batch processing...")
    test_batch_processing()

    print("\nTest completed!")
