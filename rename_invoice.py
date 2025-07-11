#!/usr/bin/env python3
"""
Script to rename invoice PDF files based on extracted data.
Format: date_company_$total.pdf
"""

import sys
import os
from pathlib import Path
from datetime import datetime
from ocrinvoice.parsers.invoice_parser import InvoiceParser


def safe_filename(text: str) -> str:
    """Convert text to a safe filename by removing/replacing invalid characters."""
    # Replace invalid filename characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        text = text.replace(char, '_')
    
    # Replace spaces with underscores
    text = text.replace(' ', '_')
    
    # Remove multiple consecutive underscores
    while '__' in text:
        text = text.replace('__', '_')
    
    # Remove leading/trailing underscores
    text = text.strip('_')
    
    return text


def rename_invoice_pdf(pdf_path: str, dry_run: bool = False) -> bool:
    """
    Parse invoice PDF and rename it based on extracted data.
    
    Args:
        pdf_path: Path to the PDF file
        dry_run: If True, only show what would be renamed without actually doing it
    
    Returns:
        True if successful, False otherwise
    """
    pdf_path = Path(pdf_path)
    
    if not pdf_path.exists():
        print(f"❌ File not found: {pdf_path}")
        return False
    
    if not pdf_path.suffix.lower() == '.pdf':
        print(f"❌ Not a PDF file: {pdf_path}")
        return False
    
    try:
        # Parse the invoice
        print(f"📄 Parsing: {pdf_path.name}")
        parser = InvoiceParser()
        result = parser.parse(str(pdf_path))
        
        # Extract data
        company = result.get('company', 'unknown')
        total = result.get('total')
        date_str = result.get('date', 'unknown')
        
        # Handle missing data
        if not company or company == 'unknown':
            print(f"⚠️  Could not extract company name from {pdf_path.name}")
            company = 'unknown'
        
        if not total:
            print(f"⚠️  Could not extract total from {pdf_path.name}")
            total = 'unknown'
        else:
            # Format total as currency
            total = f"${total:.2f}"
        
        if not date_str or date_str == 'unknown':
            print(f"⚠️  Could not extract date from {pdf_path.name}")
            date_str = 'unknown'
        else:
            # Convert ISO date to YYYY-MM-DD format
            try:
                date_obj = datetime.fromisoformat(date_str)
                date_str = date_obj.strftime('%Y-%m-%d')
            except:
                date_str = 'unknown'
        
        # Create new filename
        new_filename = f"{date_str}_{company}_{total}.pdf"
        new_filename = safe_filename(new_filename)
        new_path = pdf_path.parent / new_filename
        
        # Check if target file already exists
        if new_path.exists() and not dry_run:
            print(f"⚠️  Target file already exists: {new_filename}")
            # Add timestamp to make it unique
            timestamp = datetime.now().strftime('%H%M%S')
            new_filename = f"{date_str}_{company}_{total}_{timestamp}.pdf"
            new_filename = safe_filename(new_filename)
            new_path = pdf_path.parent / new_filename
        
        if dry_run:
            print(f"🔍 DRY RUN - Would rename:")
            print(f"   From: {pdf_path.name}")
            print(f"   To:   {new_filename}")
            print(f"   Data: Date={date_str}, Company={company}, Total={total}")
        else:
            # Rename the file
            pdf_path.rename(new_path)
            print(f"✅ Renamed: {pdf_path.name} → {new_filename}")
            print(f"   Data: Date={date_str}, Company={company}, Total={total}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error processing {pdf_path.name}: {e}")
        return False


def main():
    """Main function to handle command line arguments."""
    if len(sys.argv) < 2:
        print("Usage: python rename_invoice.py <pdf_file> [pdf_file2 ...] [--dry-run]")
        print("       python rename_invoice.py --batch <directory> [--dry-run]")
        print("\nExamples:")
        print("  python rename_invoice.py invoice.pdf")
        print("  python rename_invoice.py invoice.pdf --dry-run")
        print("  python rename_invoice.py --batch ./invoices/")
        print("  python rename_invoice.py --batch ./invoices/ --dry-run")
        sys.exit(1)
    
    dry_run = '--dry-run' in sys.argv
    batch_mode = '--batch' in sys.argv
    
    if batch_mode:
        # Batch mode: process all PDFs in a directory
        batch_index = sys.argv.index('--batch')
        if batch_index + 1 >= len(sys.argv):
            print("❌ Error: --batch requires a directory path")
            sys.exit(1)
        
        directory = Path(sys.argv[batch_index + 1])
        if not directory.exists() or not directory.is_dir():
            print(f"❌ Error: Directory not found: {directory}")
            sys.exit(1)
        
        pdf_files = list(directory.glob("*.pdf"))
        if not pdf_files:
            print(f"❌ No PDF files found in {directory}")
            sys.exit(1)
        
        print(f"📁 Processing {len(pdf_files)} PDF files in {directory}")
        success_count = 0
        
        for pdf_file in pdf_files:
            if rename_invoice_pdf(str(pdf_file), dry_run):
                success_count += 1
        
        print(f"\n📊 Summary: {success_count}/{len(pdf_files)} files processed successfully")
        
    else:
        # Single file mode: process individual PDF files
        pdf_files = [arg for arg in sys.argv[1:] if not arg.startswith('--')]
        
        if not pdf_files:
            print("❌ Error: No PDF files specified")
            sys.exit(1)
        
        success_count = 0
        for pdf_file in pdf_files:
            if rename_invoice_pdf(pdf_file, dry_run):
                success_count += 1
        
        print(f"\n📊 Summary: {success_count}/{len(pdf_files)} files processed successfully")


if __name__ == "__main__":
    main() 