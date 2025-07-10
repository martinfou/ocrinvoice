#!/usr/bin/env python3
"""
Invoice OCR Parser CLI
Command-line interface for the Invoice OCR Parser
"""

import os
import sys
import logging
from pathlib import Path
from datetime import datetime

import pandas as pd

# Add dotenv import for .env file support
try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv():
        pass

# Import the main parser module
from invoice_ocr_parser import InvoiceOCRParser

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_config():
    """Load configuration from .env file or use defaults."""
    # Check if .env file exists
    env_file = Path('.env')
    if not env_file.exists():
        # Create .env file with current directory as default
        current_dir = os.getcwd()
        env_content = f"# Invoice OCR Parser Configuration\nPDF_PATH={current_dir}\n"
        
        try:
            with open('.env', 'w') as f:
                f.write(env_content)
            print(f"📝 Created .env file with default path: {current_dir}")
        except Exception as e:
            print(f"⚠️  Warning: Could not create .env file: {e}")
            print(f"   Using current directory as default: {current_dir}")
    
    # Load the configuration (either from existing .env or newly created one)
    load_dotenv()
    pdf_path = os.getenv('PDF_PATH', os.getcwd())
    
    return pdf_path

def main():
    """Main function to run the invoice parser"""
    # Parse command line arguments
    args = sys.argv[1:]
    
    output_file = None
    use_database = False  # Default to False
    auto_rename = True    # Default to True (enable auto-rename by default)
    debug = False         # Default to False
    dry_run = False       # Default to False
    
    # Parse command line flags first
    if "--no-database" in args:
        use_database = False
        args.remove("--no-database")
    
    if "--database" in args:
        use_database = True
        args.remove("--database")
    
    if "--no-auto-rename" in args:
        auto_rename = False
        args.remove("--no-auto-rename")
    
    if "--dry-run" in args:
        dry_run = True
        auto_rename = False  # Disable auto-rename when dry-run is used
        args.remove("--dry-run")
    
    if "--debug" in args:
        debug = True
        args.remove("--debug")
    
    # Check if path is provided (after removing flags)
    if len(args) == 0:
        # No path provided, use .env file or current directory
        input_path = load_config()
        print(f"📁 Using path from .env/default: {input_path}")
    else:
        input_path = args[0]
    
    # Get output file if provided
    if len(args) > 1:
        output_file = args[1]
    
    # Initialize parser with the same options as the main module
    parser = InvoiceOCRParser(debug=debug, use_database=use_database)
    
    # Check if input is a file or folder
    if os.path.isfile(input_path) and input_path.lower().endswith('.pdf'):
        # Single PDF file
        print(f"🔍 Processing single file: {input_path}")
        result = parser.parse_invoice(input_path, auto_rename=auto_rename)
        results_df = pd.DataFrame([result])
        
        # Print results for single file
        print(f"\n📋 Results for {input_path}:")
        print(f"   Company: {result['company_name']}")
        print(f"   Total: ${result['invoice_total']}")
        print(f"   Date: {result.get('invoice_date', 'Not found')}")
        print(f"   Method: {result['extraction_method']}")
        print(f"   Confidence: {result['confidence']}")
        print(f"   Processing time: {result['processing_time']:.3f}s")
        
        if result['error']:
            print(f"   Error: {result['error']}")
        
        # Show what would be renamed in dry-run mode
        if dry_run and result['company_name'] and result['invoice_total'] and result['invoice_date']:
            old_name = os.path.basename(input_path)
            new_name = f"{result['invoice_date']}_{result['company_name']}_${result['invoice_total']}.pdf"
            print(f"   📝 Would rename: {old_name} → {new_name}")
            
    else:
        # Folder of PDFs
        print(f"📁 Processing folder: {input_path}")
        if dry_run:
            print("🔍 DRY RUN MODE: Files will not be renamed")
            results_df = parser.parse_invoices_batch(input_path, output_file, auto_rename=False)
            
            # Show what would be renamed
            successful_results = results_df[results_df['error'].isna()]
            for _, result in successful_results.iterrows():
                if result['company_name'] and result['invoice_total'] and result['invoice_date']:
                    old_name = os.path.basename(result['file_path'])
                    new_name = f"{result['invoice_date']}_{result['company_name']}_${result['invoice_total']}.pdf"
                    print(f"   📝 Would rename: {old_name} → {new_name}")
        elif auto_rename:
            results_df = parser.parse_and_rename_invoices(input_path, output_file)
        else:
            results_df = parser.parse_invoices_batch(input_path, output_file, auto_rename=False)
    
    # Generate output filename with pattern companyName_total if not provided
    if output_file is None and not results_df.empty:
        # Get the most common company name and total for naming
        successful_results = results_df[results_df['error'].isna()]
        if not successful_results.empty:
            # Get the first successful result for naming
            first_result = successful_results.iloc[0]
            company_name = first_result['company_name'] or 'Unknown'
            total = first_result['invoice_total'] or '0.00'
            
            # Clean company name for filename (remove special chars, replace spaces with underscores)
            import re
            clean_company = re.sub(r'[^\w\s-]', '', company_name).strip()
            clean_company = re.sub(r'\s+', '_', clean_company)
            
            # Format total (remove $ and ensure 2 decimal places)
            if isinstance(total, str):
                total_str = total.replace('$', '').replace(',', '')
            else:
                total_str = f"{total:.2f}"
            
            # Generate filename
            output_file = f"{clean_company}_{total_str}.csv"
            
            # Save with the generated filename
            results_df.to_csv(output_file, index=False)
            logger.info(f"Results saved to {output_file}")
    
    # Print summary
    if not results_df.empty:
        print(f"\n✅ Processing complete!")
        print(f"Total files processed: {len(results_df)}")
        print(f"Successful extractions: {len(results_df[results_df['error'].isna()])}")
        print(f"Company names found: {len(results_df[results_df['company_name'].notna()])}")
        print(f"Totals found: {len(results_df[results_df['invoice_total'].notna()])}")
        print(f"Dates found: {len(results_df[results_df['invoice_date'].notna()])}")
        
        # Show database statistics if available
        if hasattr(parser, 'invoice_db') and parser.invoice_db:
            stats = parser.invoice_db.get_database_stats()
            print(f"\n📊 Database Statistics:")
            print(f"   Total companies: {stats['total_companies']}")
            if 'company_frequencies' in stats:
                most_common = max(stats['company_frequencies'].items(), key=lambda x: x[1]) if stats['company_frequencies'] else None
                if most_common:
                    print(f"   Most common company: {most_common[0]} ({most_common[1]} times)")
        
        # Show sample results
        print(f"\n📋 Sample results:")
        columns_to_show = ['file_path', 'company_name', 'invoice_total', 'invoice_date', 'confidence']
        available_columns = [col for col in columns_to_show if col in results_df.columns]
        sample_results = results_df[available_columns].head(10)
        print(sample_results.to_string(index=False))
    else:
        print("\n❌ No files processed!")
        print("\nUsage: python invoice_ocr_parser_cli.py [folder_path_or_file] [output_csv] [options]")
        print("\nOptions:")
        print("  --database      Enable invoice database for fallback matching")
        print("  --no-database   Disable invoice database (default)")
        print("  --no-auto-rename  Disable auto-rename (auto-rename is enabled by default)")
        print("  --dry-run       Perform a dry run (show what would be renamed without actually renaming)")
        print("  --debug         Enable debug logging")
        print("\nExamples:")
        print("  python invoice_ocr_parser_cli.py /path/to/invoices results.csv")
        print("  python invoice_ocr_parser_cli.py /path/to/invoice.pdf results.csv")
        print("  python invoice_ocr_parser_cli.py /path/to/invoices --dry-run")
        print("  python invoice_ocr_parser_cli.py /path/to/invoices --no-auto-rename")
        print("  python invoice_ocr_parser_cli.py /path/to/invoices --database --debug")
        print("  python invoice_ocr_parser_cli.py  # Uses .env file or current directory")
        sys.exit(1)

if __name__ == "__main__":
    main() 