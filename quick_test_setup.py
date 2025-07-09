#!/usr/bin/env python3
"""
Quick Test Setup Helper
Automatically creates test cases from facture folder by parsing filenames
"""

import os
import re
import json
from pathlib import Path
from typing import List, Dict, Any, Optional

def parse_filename_for_company_and_total(filename: str) -> Optional[Dict[str, Any]]:
    """Parse filename to extract company name and total amount"""
    
    # Remove file extension
    name = Path(filename).stem
    
    # Common patterns for extracting company and total from filename
    patterns = [
        # Pattern: date_COMPANY_total.pdf
        r'(\d{8})_([A-Z\s]+)_(\d+\.?\d*)',
        # Pattern: facture_company_date_total_description.pdf
        r'facture_([a-z-]+)_\d{4}-\d{2}-\d{2}_([a-z-]+)_\$?(\d+\.?\d*)',
        # Pattern: COMPANY_total_date.pdf
        r'([A-Z\s]+)_(\d+\.?\d*)_\d{8}',
        # Pattern: company_total.pdf
        r'([a-z\s-]+)_(\d+\.?\d*)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, name, re.IGNORECASE)
        if match:
            groups = match.groups()
            
            # Extract company name (usually the second group)
            company = groups[1] if len(groups) >= 3 else groups[0]
            company = company.replace('_', ' ').replace('-', ' ').strip().upper()
            
            # Extract total (usually the last numeric group)
            total_str = groups[-1] if len(groups) >= 2 else groups[0]
            try:
                total = float(total_str)
                return {
                    'company': company,
                    'total': total,
                    'confidence': 'high' if len(groups) >= 3 else 'medium'
                }
            except ValueError:
                continue
    
    return None

def scan_facture_folder(folder_path: str) -> List[Dict[str, Any]]:
    """Scan facture folder and extract potential test cases"""
    test_cases = []
    
    if not os.path.exists(folder_path):
        print(f"❌ Folder not found: {folder_path}")
        return test_cases
    
    pdf_files = list(Path(folder_path).glob("*.pdf"))
    print(f"📁 Found {len(pdf_files)} PDF files in {folder_path}")
    
    for pdf_file in pdf_files:
        result = parse_filename_for_company_and_total(pdf_file.name)
        if result:
            test_cases.append({
                'pdf_path': str(pdf_file),
                'filename': pdf_file.name,
                'expected_company': result['company'],
                'expected_total': result['total'],
                'confidence': result['confidence']
            })
            print(f"✅ Parsed: {pdf_file.name} -> {result['company']} (${result['total']:.2f})")
        else:
            print(f"❓ Could not parse: {pdf_file.name}")
    
    return test_cases

def create_test_data_from_facture(folder_path: str, output_file: str = "/Volumes/T7/Dropbox/scan-snap/facture/ocr-test-data/auto_test_data.json"):
    """Create test data file from facture folder"""
    test_cases = scan_facture_folder(folder_path)
    
    if not test_cases:
        print("❌ No test cases could be extracted from filenames")
        return
    
    # Convert to test data format
    test_data = {
        "tests": [
            {
                "pdf_path": case['pdf_path'],
                "expected_company": case['expected_company'],
                "expected_total": case['expected_total'],
                "description": f"Auto-generated from filename: {case['filename']}",
                "confidence": case['confidence'],
                "added_date": "2025-01-27T10:00:00"
            }
            for case in test_cases
        ]
    }
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # Save to file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(test_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 Created {len(test_cases)} test cases in {output_file}")
    print("⚠️  Please review and edit the expected values as needed!")
    
    return test_data

def interactive_review_test_cases(test_data: Dict[str, Any]):
    """Interactive review and edit of auto-generated test cases"""
    print("\n🔍 Interactive Review Mode")
    print("Review each test case and confirm or edit the expected values")
    
    for i, test_case in enumerate(test_data['tests'], 1):
        print(f"\n--- Test Case {i}/{len(test_data['tests'])} ---")
        print(f"File: {Path(test_case['pdf_path']).name}")
        print(f"Current Company: {test_case['expected_company']}")
        print(f"Current Total: ${test_case['expected_total']:.2f}")
        
        # Ask for confirmation or edit
        while True:
            action = input("Action (c=confirm, e=edit, s=skip, q=quit): ").strip().lower()
            
            if action == 'c':
                print("✅ Confirmed")
                break
            elif action == 'e':
                new_company = input(f"New company name [{test_case['expected_company']}]: ").strip()
                if new_company:
                    test_case['expected_company'] = new_company
                
                new_total = input(f"New total [{test_case['expected_total']}]: ").strip()
                if new_total:
                    try:
                        test_case['expected_total'] = float(new_total)
                    except ValueError:
                        print("❌ Invalid number, keeping original")
                
                print("✅ Updated")
                break
            elif action == 's':
                print("⏭️  Skipped")
                break
            elif action == 'q':
                print("👋 Exiting review")
                return
            else:
                print("❓ Invalid action. Use c/e/s/q")

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Quick Test Setup Helper")
    parser.add_argument("--folder", default="/Volumes/T7/Dropbox/scan-snap/facture", 
                       help="Path to facture folder")
    parser.add_argument("--output", default="/Volumes/T7/Dropbox/scan-snap/facture/ocr-test-data/auto_test_data.json", 
                       help="Output test data file")
    parser.add_argument("--review", action="store_true", 
                       help="Interactive review mode")
    
    args = parser.parse_args()
    
    print("🚀 Quick Test Setup Helper")
    print(f"📁 Scanning folder: {args.folder}")
    
    # Create test data
    test_data = create_test_data_from_facture(args.folder, args.output)
    
    if test_data and args.review:
        # Interactive review
        interactive_review_test_cases(test_data)
        
        # Save reviewed data
        os.makedirs(os.path.dirname(args.output), exist_ok=True)
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(test_data, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Reviewed test data saved to {args.output}")
    
    print(f"\n📋 Next steps:")
    print(f"1. Review the generated test data: {args.output}")
    print(f"2. Run tests: python test_suite.py --run")
    print(f"3. Add more test cases: python test_suite.py --add")

if __name__ == "__main__":
    main() 