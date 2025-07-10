#!/usr/bin/env python3
"""
PDF Text Extractor Tool
Extracts text from all PDFs in a directory and saves to Excel for keyword review.

Usage:
  python3 pdf_text_extractor.py [path]
  python3 pdf_text_extractor.py --help

If no path is provided, reads from .env file or uses default.
"""

import os
import sys
import glob
import re
from pathlib import Path
import pandas as pd
from dotenv import load_dotenv
import argparse
from datetime import datetime

try:
    import PyPDF2

    PDF_LIBRARY = "PyPDF2"
except ImportError:
    try:
        import pdfplumber

        PDF_LIBRARY = "pdfplumber"
    except ImportError:
        print("❌ Error: Neither PyPDF2 nor pdfplumber is installed.")
        print("Install one of them:")
        print("  pip install PyPDF2")
        print("  pip install pdfplumber")
        sys.exit(1)


def clean_text_for_excel(text):
    """Clean text of characters that cause issues in Excel."""
    if not text:
        return ""

    # Replace problematic characters
    replacements = {
        "\u2013": "-",  # en dash
        "\u2014": "-",  # em dash
        "\u2018": "'",  # left single quotation mark
        "\u2019": "'",  # right single quotation mark
        "\u201C": '"',  # left double quotation mark
        "\u201D": '"',  # right double quotation mark
        "\u2022": "•",  # bullet
        "\u2026": "...",  # ellipsis
        "\u00A0": " ",  # non-breaking space
        "\u00AD": "",  # soft hyphen
        "\u200B": "",  # zero-width space
        "\u200C": "",  # zero-width non-joiner
        "\u200D": "",  # zero-width joiner
        "\u2060": "",  # word joiner
        "\uFEFF": "",  # zero-width no-break space
    }

    # Apply replacements
    for old_char, new_char in replacements.items():
        text = text.replace(old_char, new_char)

    # Remove control characters (except newlines and tabs)
    text = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]", "", text)

    # Limit text length to avoid Excel cell size limits (32,767 characters)
    if len(text) > 32000:
        text = text[:32000] + "\n\n[Text truncated due to length limit]"

    return text


def load_config():
    """Load configuration from .env file or use defaults."""
    load_dotenv()

    # Check if .env file exists
    env_file = Path(".env")
    if not env_file.exists():
        # Create .env file with current directory as default
        current_dir = os.getcwd()
        env_content = f"# PDF Text Extractor Configuration\nPDF_PATH={current_dir}\n"

        try:
            with open(".env", "w") as f:
                f.write(env_content)
            print(f"📝 Created .env file with default path: {current_dir}")
        except Exception as e:
            print(f"⚠️  Warning: Could not create .env file: {e}")
            print(f"   Using current directory as default: {current_dir}")

    # Load the configuration (either from existing .env or newly created one)
    load_dotenv()
    pdf_path = os.getenv("PDF_PATH", os.getcwd())

    return pdf_path


def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file using available library."""
    try:
        if PDF_LIBRARY == "PyPDF2":
            with open(pdf_path, "rb") as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                return clean_text_for_excel(text.strip())

        elif PDF_LIBRARY == "pdfplumber":
            with pdfplumber.open(pdf_path) as pdf:
                text = ""
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                return clean_text_for_excel(text.strip())

    except Exception as e:
        return f"ERROR: {str(e)}"


def find_pdf_files(directory):
    """Find all PDF files in directory and subdirectories."""
    pdf_files = []

    # Check if directory exists
    if not os.path.exists(directory):
        print(f"❌ Error: Directory '{directory}' does not exist")
        return pdf_files

    # Find all PDF files recursively
    pattern = os.path.join(directory, "**/*.pdf")
    pdf_files = glob.glob(pattern, recursive=True)

    # Also check for uppercase .PDF
    pattern_upper = os.path.join(directory, "**/*.PDF")
    pdf_files.extend(glob.glob(pattern_upper, recursive=True))

    return sorted(pdf_files)


def main():
    parser = argparse.ArgumentParser(
        description="Extract text from PDFs and save to Excel for keyword review",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 pdf_text_extractor_cli.py
  python3 pdf_text_extractor_cli.py /path/to/pdfs
  python3 pdf_text_extractor_cli.py --help
        """,
    )

    parser.add_argument(
        "path",
        nargs="?",
        help="Path to directory containing PDFs (optional, uses .env or default if not provided)",
    )

    args = parser.parse_args()

    # Determine PDF directory
    if args.path:
        pdf_directory = args.path
        print(f"📁 Using provided path: {pdf_directory}")
    else:
        pdf_directory = load_config()
        print(f"📁 Using path from .env/default: {pdf_directory}")

    # Find PDF files
    print(f"\n🔍 Searching for PDF files in: {pdf_directory}")
    pdf_files = find_pdf_files(pdf_directory)

    if not pdf_files:
        print("❌ No PDF files found in the specified directory")
        sys.exit(1)

    print(f"✅ Found {len(pdf_files)} PDF file(s)")

    # Extract text from each PDF
    results = []
    print(f"\n📄 Extracting text using {PDF_LIBRARY}...")

    for i, pdf_file in enumerate(pdf_files, 1):
        print(f"  [{i}/{len(pdf_files)}] Processing: {os.path.basename(pdf_file)}")

        # Get relative path for cleaner display
        rel_path = os.path.relpath(pdf_file, pdf_directory)

        # Extract text
        text = extract_text_from_pdf(pdf_file)

        # Get file info
        file_size = os.path.getsize(pdf_file)
        file_size_mb = file_size / (1024 * 1024)

        results.append(
            {
                "filename": os.path.basename(pdf_file),
                "filepath": rel_path,
                "filesize_mb": round(file_size_mb, 2),
                "text": text,
                "text_length": len(text),
                "extraction_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
        )

    # Create DataFrame and save to Excel
    df = pd.DataFrame(results)

    # Generate output filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"pdf_texts_{timestamp}.xlsx"

    print(f"\n💾 Saving results to: {output_file}")

    # Save to Excel with formatting
    with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="PDF_Texts", index=False)

        # Auto-adjust column widths
        worksheet = writer.sheets["PDF_Texts"]
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter

            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass

            adjusted_width = min(max_length + 2, 50)  # Cap at 50 characters
            worksheet.column_dimensions[column_letter].width = adjusted_width

    print(f"✅ Successfully extracted text from {len(pdf_files)} PDF(s)")
    print(f"📊 Summary:")
    print(f"   - Total files processed: {len(pdf_files)}")
    print(
        f"   - Total text extracted: {sum(len(r['text']) for r in results):,} characters"
    )
    print(f"   - Output file: {output_file}")

    # Show some statistics
    successful_extractions = len(
        [r for r in results if not r["text"].startswith("ERROR")]
    )
    failed_extractions = len(pdf_files) - successful_extractions

    if failed_extractions > 0:
        print(f"⚠️  Warning: {failed_extractions} file(s) had extraction errors")

    print(f"\n📋 Next steps:")
    print(f"   1. Open {output_file} in Excel")
    print(f"   2. Review the 'text' column for potential keywords")
    print(f"   3. Use Excel's search/filter features to find specific terms")


if __name__ == "__main__":
    main()
