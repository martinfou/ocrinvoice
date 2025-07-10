#!/usr/bin/env python3
"""
Simple example of parsing a single PDF invoice
"""

import sys
import os
from pathlib import Path

# Add dotenv import for .env file support
try:
    from dotenv import load_dotenv
except ImportError:

    def load_dotenv():
        pass


def parse_single_pdf(pdf_path):
    """Parse a single PDF file and display results"""

    try:
        # Import the parser (this will work even without all dependencies)
        from invoice_ocr_parser import InvoiceOCRParser

        print(f"🔍 Parsing invoice: {pdf_path}")

        # Initialize the parser
        parser = InvoiceOCRParser(debug=True)

        # Parse the single invoice
        result = parser.parse_invoice(pdf_path)

        # Display results
        print("\n" + "=" * 60)
        print("INVOICE PARSING RESULTS")
        print("=" * 60)
        print(f"📄 File: {os.path.basename(result['file_path'])}")
        print(f"🏢 Company: {result['company_name']}")
        print(
            f"💰 Total: ${result['invoice_total']}"
            if result["invoice_total"]
            else "💰 Total: Not found"
        )
        print(f"🔧 Method: {result['extraction_method']}")
        print(f"📊 Confidence: {result['confidence']}")
        print(f"⏱️  Time: {result['processing_time']:.2f} seconds")

        if result["error"]:
            print(f"❌ Error: {result['error']}")
        else:
            print("✅ Success!")

        print("=" * 60)

        return result

    except ImportError as e:
        print(f"❌ Missing dependencies: {e}")
        print(
            "💡 Install required packages: pip install opencv-python numpy pandas pillow pytesseract pdf2image pdfplumber PyPDF2"
        )
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def load_config():
    """Load configuration from .env file or use defaults."""
    # Load the configuration
    load_dotenv()
    pdf_path = os.getenv("PDF_PATH", os.getcwd())
    return pdf_path


if __name__ == "__main__":
    if len(sys.argv) == 2:
        pdf_path = sys.argv[1]
    else:
        # Use .env file or current directory and find the first PDF file
        config_path = load_config()
        print(f"📁 Using path from .env: {config_path}")

        import glob

        # Look for PDFs in the configured path
        if os.path.isdir(config_path):
            pdf_files = glob.glob(os.path.join(config_path, "*.pdf"))
        else:
            pdf_files = []

        if not pdf_files:
            print("❌ No PDF files found in configured path")
            print("Usage: python3 single_pdf_example.py <path_to_pdf>")
            print("Example: python3 single_pdf_example.py invoice.pdf")
            print(
                "Or update PDF_PATH in .env file or place a PDF file in the current directory"
            )
            sys.exit(1)

        pdf_path = pdf_files[0]
        print(f"📁 Using first PDF found: {os.path.basename(pdf_path)}")

    if not os.path.exists(pdf_path):
        print(f"❌ File not found: {pdf_path}")
        sys.exit(1)

    if not pdf_path.lower().endswith(".pdf"):
        print(f"❌ Not a PDF file: {pdf_path}")
        sys.exit(1)

    result = parse_single_pdf(pdf_path)

    if result and not result["error"]:
        print("\n🎉 Parsing completed successfully!")
    else:
        print("\n💥 Parsing failed!")
        sys.exit(1)
