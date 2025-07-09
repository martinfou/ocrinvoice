#!/usr/bin/env python3
"""
Invoice OCR Parser Test Suite
Allows testing with sample PDFs and expected outputs for validation
"""

import os
import sys
import json
import csv
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import shutil
import logging
import re

from invoice_ocr_parser import InvoiceOCRParser

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class TestSuite:
    """Test suite for invoice OCR parser validation"""
    
    def __init__(self, test_data_file: str = "/Volumes/T7/Dropbox/scan-snap/facture/ocr-test-data/test_data.json"):
        self.test_data_file = test_data_file
        self.parser = InvoiceOCRParser()
        self.test_results = []
        
    def load_test_data(self) -> Dict[str, Any]:
        """Load test data from JSON file"""
        if not os.path.exists(self.test_data_file):
            return {"tests": []}
        
        try:
            with open(self.test_data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            print(f"❌ Error loading test data: {e}")
            return {"tests": []}
    
    def save_test_data(self, test_data: Dict[str, Any]):
        """Save test data to JSON file"""
        # Ensure the directory exists
        os.makedirs(os.path.dirname(self.test_data_file), exist_ok=True)
        
        with open(self.test_data_file, 'w', encoding='utf-8') as f:
            json.dump(test_data, f, indent=2, ensure_ascii=False)
    
    def add_test_case(self, pdf_path: str, expected_company: str, 
                     expected_total: float, description: str = ""):
        """Add a new test case to the test data"""
        test_data = self.load_test_data()
        
        test_case = {
            "pdf_path": pdf_path,
            "expected_company": expected_company,
            "expected_total": expected_total,
            "description": description,
            "added_date": datetime.now().isoformat()
        }
        
        test_data["tests"].append(test_case)
        self.save_test_data(test_data)
        print(f"✅ Added test case: {pdf_path}")
    
    def run_single_test(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """Run a single test case"""
        pdf_path = test_case['pdf_path']
        expected_company = test_case['expected_company']
        expected_total = test_case['expected_total']
        
        print(f"🔍 Testing: {pdf_path}")
        print(f"   Expected Company: {expected_company}")
        print(f"   Expected Total: ${expected_total:.2f}")
        
        # Initialize parser with debug enabled
        parser = InvoiceOCRParser(debug=True)
        
        # Parse the invoice
        result = parser.parse_invoice(pdf_path)
        
        # Extract results
        actual_company = result.get('company_name', 'Unknown')
        actual_total_str = result.get('invoice_total', '0.00')
        try:
            actual_total = float(actual_total_str) if actual_total_str else 0.0
        except (ValueError, TypeError):
            actual_total = 0.0
        
        confidence = result.get('confidence', 'unknown')
        method = result.get('extraction_method', 'unknown')
        
        # Compare results
        company_match = self._normalize_company_name(actual_company) == self._normalize_company_name(expected_company)
        total_match = abs(actual_total - expected_total) < 0.01
        
        if company_match and total_match:
            status = "✅ PASS: Both company and total match"
        elif company_match:
            status = "⚠️  PARTIAL: Company matches, total doesn't"
        elif total_match:
            status = "⚠️  PARTIAL: Total matches, company doesn't"
        else:
            status = "❌ FAIL: Neither company nor total match"
        
        print(f"   {status}")
        print(f"   Actual Company: {actual_company}")
        print(f"   Actual Total: ${actual_total:.2f}")
        print(f"   Method: {method}")
        print(f"   Confidence: {confidence}")
        
        # Show extracted text for failing cases
        if not (company_match and total_match):
            extracted_text = result.get('extracted_text', '')
            if extracted_text:
                lines = extracted_text.split('\n')
                print(f"\n🔍 DEBUG - First 20 lines of extracted text:")
                for i, line in enumerate(lines[:20], 1):
                    print(f"    {i}: {line}")
        
        return {
            'pdf_path': pdf_path,
            'expected_company': expected_company,
            'expected_total': expected_total,
            'actual_company': actual_company,
            'actual_total': actual_total,
            'company_match': company_match,
            'total_match': total_match,
            'both_match': company_match and total_match,
            'confidence': confidence,
            'method': method,
            'status': status,
            'error': result.get('error', '')
        }
    
    def run_all_tests(self) -> List[Dict[str, Any]]:
        """Run all test cases"""
        # Restore PDFs from backup before running tests
        backup_dir = "/Volumes/T7/Dropbox/scan-snap/facture/ocr-test-data/backup"
        test_data_dir = "/Volumes/T7/Dropbox/scan-snap/facture/ocr-test-data"
        # Delete all existing PDFs in the test data directory
        for fname in os.listdir(test_data_dir):
            if fname.lower().endswith('.pdf'):
                try:
                    os.remove(os.path.join(test_data_dir, fname))
                except Exception as e:
                    print(f"Warning: Could not delete {fname}: {e}")
        # Copy fresh PDFs from backup
        for fname in [f"invoice{i}.pdf" for i in range(1, 7)]:
            src = os.path.join(backup_dir, fname)
            dst = os.path.join(test_data_dir, fname)
            if os.path.exists(src):
                shutil.copy2(src, dst)
        
        test_data = self.load_test_data()
        results = []
        print(f"🚀 Running {len(test_data['tests'])} test cases...")
        for i, test_case in enumerate(test_data['tests'], 1):
            print(f"\n--- Test {i}/{len(test_data['tests'])} ---")
            result = self.run_single_test(test_case)
            results.append(result)
        return results
    
    def _compare_company(self, actual: str, expected: str) -> bool:
        """Compare company names with fuzzy matching"""
        if not actual or not expected:
            return False
        
        # Normalize strings
        actual_norm = self._normalize_company_name(actual)
        expected_norm = self._normalize_company_name(expected)
        
        # Exact match
        if actual_norm == expected_norm:
            return True
        
        # Check if expected is contained in actual
        if expected_norm in actual_norm:
            return True
        
        # Check if actual is contained in expected
        if actual_norm in expected_norm:
            return True
        
        return False
    
    def _normalize_company_name(self, name: str) -> str:
        """Normalize company name for comparison"""
        if not name:
            return ""
        name = name.lower()
        name = re.sub(r'[^\w]', '', name)  # Remove all non-alphanumeric characters including spaces
        return name
    
    def _compare_total(self, actual, expected: float, tolerance: float = 0.01) -> bool:
        """Compare invoice totals with tolerance"""
        if actual is None or expected is None:
            return False
        
        # Convert actual to float if it's a string
        try:
            if isinstance(actual, str):
                actual_float = float(actual)
            else:
                actual_float = actual
            return abs(actual_float - expected) <= tolerance
        except (ValueError, TypeError):
            return False
    
    def generate_report(self, results: List[Dict[str, Any]], output_file: str = "/Volumes/T7/Dropbox/scan-snap/facture/ocr-test-data/test_report.csv"):
        """Generate a detailed test report"""
        if not results:
            print("❌ No test results to report")
            return
        
        # Calculate statistics
        total_tests = len(results)
        company_matches = sum(1 for r in results if r['company_match'])
        total_matches = sum(1 for r in results if r['total_match'])
        both_matches = sum(1 for r in results if r['company_match'] and r['total_match'])
        errors = sum(1 for r in results if r['error'])
        
        # Print summary
        print(f"\n📊 Test Results Summary:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Company Matches: {company_matches}/{total_tests} ({company_matches/total_tests*100:.1f}%)")
        print(f"   Total Matches: {total_matches}/{total_tests} ({total_matches/total_tests*100:.1f}%)")
        print(f"   Both Match: {both_matches}/{total_tests} ({both_matches/total_tests*100:.1f}%)")
        print(f"   Errors: {errors}/{total_tests} ({errors/total_tests*100:.1f}%)")
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # Save detailed report
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)
        
        print(f"📄 Detailed report saved to: {output_file}")
    
    def interactive_add_test(self):
        """Interactive mode to add test cases"""
        print("🎯 Interactive Test Case Addition")
        print("Enter 'quit' at any time to exit\n")
        
        while True:
            # Get PDF path
            pdf_path = input("Enter PDF file path: ").strip()
            if pdf_path.lower() == 'quit':
                break
            
            if not os.path.exists(pdf_path):
                print("❌ File not found. Please try again.")
                continue
            
            # Get expected company
            expected_company = input("Enter expected company name: ").strip()
            if expected_company.lower() == 'quit':
                break
            
            # Get expected total
            while True:
                total_input = input("Enter expected total amount: ").strip()
                if total_input.lower() == 'quit':
                    break
                
                try:
                    expected_total = float(total_input)
                    break
                except ValueError:
                    print("❌ Please enter a valid number.")
            
            if total_input.lower() == 'quit':
                break
            
            # Get description (optional)
            description = input("Enter description (optional): ").strip()
            if description.lower() == 'quit':
                break
            
            # Add the test case
            self.add_test_case(pdf_path, expected_company, expected_total, description)
            
            # Ask if user wants to add another
            another = input("\nAdd another test case? (y/n): ").strip().lower()
            if another != 'y':
                break
        
        print("\n✅ Test case addition complete!")

def main():
    """Main function for command line interface"""
    parser = argparse.ArgumentParser(description="Invoice OCR Parser Test Suite")
    parser.add_argument("--add", action="store_true", help="Add new test cases interactively")
    parser.add_argument("--run", action="store_true", help="Run all test cases")
    parser.add_argument("--report", default="/Volumes/T7/Dropbox/scan-snap/facture/ocr-test-data/test_report.csv", help="Output file for test report")
    parser.add_argument("--pdf", help="PDF file path for single test")
    parser.add_argument("--company", help="Expected company name for single test")
    parser.add_argument("--total", type=float, help="Expected total for single test")
    parser.add_argument("--description", help="Description for single test")
    
    args = parser.parse_args()
    
    test_suite = TestSuite()
    
    if args.add:
        # Interactive mode
        test_suite.interactive_add_test()
    
    elif args.pdf and args.company and args.total is not None:
        # Single test case
        test_suite.add_test_case(args.pdf, args.company, args.total, args.description or "")
        print("✅ Test case added!")
    
    elif args.run:
        # Run all tests
        results = test_suite.run_all_tests()
        test_suite.generate_report(results, args.report)
    
    else:
        # Show help
        parser.print_help()
        print("\n📝 Examples:")
        print("  # Add test cases interactively:")
        print("  python test_suite.py --add")
        print("\n  # Add a single test case:")
        print("  python test_suite.py --pdf invoice.pdf --company 'ABC Corp' --total 123.45")
        print("\n  # Run all tests:")
        print("  python test_suite.py --run")

if __name__ == "__main__":
    main() 