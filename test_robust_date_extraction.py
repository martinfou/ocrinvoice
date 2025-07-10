#!/usr/bin/env python3
"""
Test script for robust date extraction with OCR error handling
"""

import logging
from invoice_ocr_parser import DateExtractor

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def test_robust_date_extraction():
    """Test the robust date extraction with various OCR errors"""
    
    # Test cases with OCR errors
    test_cases = [
        # Original text from the PDF
        "Date du relevé : 7 fév 202S",
        "Date du relevé : 7 fév 2025",
        
        # Common OCR errors
        "juillet 20I9",  # I instead of 1
        "juillet 2019",  # Correct
        "7 fév 202S",    # S instead of 5
        "7 fév 2025",    # Correct
        "15 jan 202O",   # O instead of 0
        "15 jan 2020",   # Correct
        "2024-0l-15",    # l instead of 1
        "2024-01-15",    # Correct
        "2024-0S-15",    # S instead of 5
        "2024-05-15",    # Correct
        "2024-1O-15",    # O instead of 0
        "2024-10-15",    # Correct
        "2024-1S-15",    # S instead of 5
        "2024-15-15",    # Correct (but invalid month)
        "2024-1G-15",    # G instead of 6
        "2024-16-15",    # Correct (but invalid month)
        "2024-1B-15",    # B instead of 8
        "2024-18-15",    # Correct (but invalid month)
        "2024-1Z-15",    # Z instead of 2
        "2024-12-15",    # Correct
        "2024-1A-15",    # A instead of 4
        "2024-14-15",    # Correct
        "2024-1E-15",    # E instead of 3
        "2024-13-15",    # Correct
        "2024-1T-15",    # T instead of 7
        "2024-17-15",    # Correct
        
        # French dates with OCR errors
        "7 février 202S",
        "7 février 2025",
        "15 janvier 202O",
        "15 janvier 2020",
        "Date de facture : 20 mars 202S",
        "Date de facture : 20 mars 2025",
        
        # English dates with OCR errors
        "January 15, 202S",
        "January 15, 2025",
        "15 Jan 202O",
        "15 Jan 2020",
        "Invoice date: March 20, 202S",
        "Invoice date: March 20, 2025",
        
        # Mixed formats
        "202S-01-15",
        "2025-01-15",
        "15/01/202S",
        "15/01/2025",
        "15.01.202S",
        "15.01.2025",
        
        # Edge cases
        "juillet 202S",  # Just month and year with OCR error
        "juillet 2025",  # Correct
        "202S",          # Just year with OCR error
        "2025",          # Correct
    ]
    
    print("Testing robust date extraction with OCR errors...")
    print("=" * 60)
    
    success_count = 0
    total_count = len(test_cases)
    
    for i, test_text in enumerate(test_cases, 1):
        print(f"\nTest {i}: '{test_text}'")
        
        try:
            extracted_date = DateExtractor.extract_date_from_text(test_text)
            
            if extracted_date:
                print(f"  ✓ Extracted: {extracted_date}")
                success_count += 1
            else:
                print(f"  ✗ No date found")
                
        except Exception as e:
            print(f"  ✗ Error: {e}")
    
    print("\n" + "=" * 60)
    print(f"Results: {success_count}/{total_count} tests passed ({success_count/total_count*100:.1f}%)")
    
    # Test specific OCR correction methods
    print("\nTesting OCR correction methods...")
    print("=" * 40)
    
    ocr_test_cases = [
        ("20I9", "2019"),
        ("202S", "2025"),
        ("202O", "2020"),
        ("0l", "01"),
        ("0S", "05"),
        ("1O", "10"),
        ("1S", "15"),
        ("1G", "16"),
        ("1B", "18"),
        ("1Z", "12"),
        ("1A", "14"),
        ("1E", "13"),
        ("1T", "17"),
    ]
    
    for original, expected in ocr_test_cases:
        corrected = DateExtractor.ocr_correct_date(original)
        status = "✓" if corrected == expected else "✗"
        print(f"{status} '{original}' -> '{corrected}' (expected: '{expected}')")
    
    # Test year correction specifically
    print("\nTesting year correction...")
    print("=" * 30)
    
    year_test_cases = [
        ("20I9", 2019),
        ("202S", 2025),
        ("202O", 2020),
        ("202l", 2021),
        ("202S", 2025),
    ]
    
    for original, expected in year_test_cases:
        corrected = DateExtractor._apply_ocr_correction_to_year(original)
        status = "✓" if corrected == expected else "✗"
        print(f"{status} '{original}' -> {corrected} (expected: {expected})")

if __name__ == "__main__":
    test_robust_date_extraction() 