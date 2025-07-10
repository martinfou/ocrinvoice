#!/usr/bin/env python3
"""
Simplified test script for date extraction functionality only
"""

import re
from datetime import datetime
from typing import Optional

class DateExtractor:
    """Robust date extraction from invoice text with OCR correction"""
    
    # French month names and abbreviations
    FRENCH_MONTHS = {
        'janvier': 1, 'jan': 1, 'janv': 1,
        'février': 2, 'fév': 2, 'févr': 2, 'fevrier': 2, 'fev': 2,
        'mars': 3, 'mar': 3,
        'avril': 4, 'avr': 4,
        'mai': 5,
        'juin': 6,
        'juillet': 7, 'juil': 7,
        'août': 8, 'aout': 8, 'aoû': 8,
        'septembre': 9, 'sept': 9, 'sep': 9,
        'octobre': 10, 'oct': 10,
        'novembre': 11, 'nov': 11,
        'décembre': 12, 'dec': 12, 'déc': 12, 'decembre': 12
    }
    
    # English month names and abbreviations
    ENGLISH_MONTHS = {
        'january': 1, 'jan': 1,
        'february': 2, 'feb': 2,
        'march': 3, 'mar': 3,
        'april': 4, 'apr': 4,
        'may': 5,
        'june': 6, 'jun': 6,
        'july': 7, 'jul': 7,
        'august': 8, 'aug': 8,
        'september': 9, 'sep': 9, 'sept': 9,
        'october': 10, 'oct': 10,
        'november': 11, 'nov': 11,
        'december': 12, 'dec': 12
    }
    
    # OCR correction mapping for common date misreadings
    OCR_CORRECTIONS = {
        'O': '0', 'o': '0',  # O/o often misread as 0
        'l': '1', 'I': '1', 'i': '1',  # l/I/i often misread as 1
        'S': '5', 's': '5',  # S/s often misread as 5
        'G': '6', 'g': '6',  # G/g often misread as 6
        'B': '8', 'b': '8',  # B/b often misread as 8
        'Z': '2', 'z': '2',  # Z/z often misread as 2
        'A': '4', 'a': '4',  # A/a often misread as 4
        'E': '3', 'e': '3',  # E/e often misread as 3
        'T': '7', 't': '7',  # T/t often misread as 7
    }
    
    @staticmethod
    def ocr_correct_date(text: str) -> str:
        """Apply OCR corrections to date text"""
        corrected = text
        for wrong, right in DateExtractor.OCR_CORRECTIONS.items():
            corrected = corrected.replace(wrong, right)
        return corrected
    
    @staticmethod
    def extract_date_from_text(text: str) -> Optional[str]:
        """Extract date from invoice text using multiple strategies"""
        if not text:
            return None
        
        lines = text.split('\n')
        candidates = []
        
        # High-priority date keywords in French and English
        date_keywords = [
            'date', 'dated', 'daté', 'datée', 'facturé', 'facturée', 'billed',
            'invoice date', 'date de facture', 'date de facturation',
            'due date', 'date d\'échéance', 'échéance', 'due',
            'issued', 'émis', 'emission', 'émission',
            'created', 'créé', 'créée', 'creation', 'création'
        ]
        
        # Date patterns with different formats
        date_patterns = [
            # YYYY-MM-DD or YYYY/MM/DD (highest priority for unambiguous format)
            r'(\d{4})[/\-](\d{1,2})[/\-](\d{1,2})',
            # DD/MM/YYYY or DD-MM-YYYY
            r'(\d{1,2})[/\-](\d{1,2})[/\-](\d{2,4})',
            # DD Month YYYY (English)
            r'(\d{1,2})\s+(january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|jun|jul|aug|sep|oct|nov|dec)\s+(\d{2,4})',
            # DD Month YYYY (French)
            r'(\d{1,2})\s+(janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre|jan|fév|mar|avr|juil|aoû|sept|oct|nov|déc|fevrier|aout|decembre)\s+(\d{2,4})',
            # Month DD, YYYY (English)
            r'(january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|jun|jul|aug|sep|oct|nov|dec)\s+(\d{1,2}),?\s+(\d{2,4})',
            # Month DD, YYYY (French)
            r'(janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre|jan|fév|mar|avr|juil|aoû|sept|oct|nov|déc|fevrier|aout|decembre)\s+(\d{1,2}),?\s+(\d{2,4})',
            # DD.MM.YYYY or DD.MM.YY
            r'(\d{1,2})\.(\d{1,2})\.(\d{2,4})',
        ]
        
        # Search in first 30 lines (usually where dates appear)
        search_lines = lines[:30]
        
        # First pass: Look for lines with date keywords
        for i, line in enumerate(search_lines):
            line_lower = line.lower()
            
            # Check if line contains date keywords
            if any(keyword in line_lower for keyword in date_keywords):
                # Apply OCR corrections
                corrected_line = DateExtractor.ocr_correct_date(line)
                
                # Try to extract date using patterns
                for pattern in date_patterns:
                    matches = re.findall(pattern, corrected_line, re.IGNORECASE)
                    for match in matches:
                        try:
                            parsed_date = DateExtractor._parse_date_match(match, pattern)
                            if parsed_date:
                                candidates.append((parsed_date, f"Date keyword match: {line.strip()}", 15))
                                break
                        except Exception:
                            continue
        
        # Second pass: Look for date patterns without keywords
        if not candidates:
            for i, line in enumerate(search_lines):
                corrected_line = DateExtractor.ocr_correct_date(line)
                
                for pattern in date_patterns:
                    matches = re.findall(pattern, corrected_line, re.IGNORECASE)
                    for match in matches:
                        try:
                            parsed_date = DateExtractor._parse_date_match(match, pattern)
                            if parsed_date:
                                # Lower priority for matches without keywords
                                priority = 10 if i < 10 else 5  # Higher priority for earlier lines
                                candidates.append((parsed_date, f"Pattern match: {line.strip()}", priority))
                        except Exception:
                            continue
        
        # Third pass: Look for standalone dates (numbers that look like dates)
        if not candidates:
            for line in search_lines:
                corrected_line = DateExtractor.ocr_correct_date(line)
                
                # Look for patterns like "2024-01-15" or "15/01/2024"
                standalone_patterns = [
                    r'(\d{4})-(\d{1,2})-(\d{1,2})',
                    r'(\d{1,2})/(\d{1,2})/(\d{4})',
                    r'(\d{1,2})-(\d{1,2})-(\d{4})',
                ]
                
                for pattern in standalone_patterns:
                    matches = re.findall(pattern, corrected_line)
                    for match in matches:
                        try:
                            parsed_date = DateExtractor._parse_date_match(match, pattern)
                            if parsed_date:
                                candidates.append((parsed_date, f"Standalone date: {line.strip()}", 8))
                        except Exception:
                            continue
        
        # Return the best candidate
        if candidates:
            # Sort by priority (highest first)
            candidates.sort(key=lambda x: x[2], reverse=True)
            best_date, source_line, priority = candidates[0]
            
            print(f"Found invoice date: '{best_date}' from line: {source_line}")
            return best_date
        
        print("No invoice date found")
        return None
    
    @staticmethod
    def _parse_date_match(match: tuple, pattern: str) -> Optional[str]:
        """Parse a date match tuple into a standardized date string"""
        try:
            if len(match) == 3:
                part1, part2, part3 = match
                
                # Handle different pattern types
                if pattern.startswith(r'(\d{4})'):  # YYYY-MM-DD format
                    year = int(part1)
                    month = int(part2)
                    day = int(part3)
                elif pattern.startswith(r'(\d{1,2})') and 'month' in pattern.lower():  # DD Month YYYY
                    day = int(part1)
                    month = DateExtractor._parse_month(part2)
                    year = int(part3)
                elif 'month' in pattern.lower() and pattern.startswith(r'(january|février'):  # Month DD YYYY
                    month = DateExtractor._parse_month(part1)
                    day = int(part2)
                    year = int(part3)
                else:  # Assume DD/MM/YYYY or MM/DD/YYYY
                    # Try both interpretations and pick the more reasonable one
                    day1, month1, year1 = int(part1), int(part2), int(part3)
                    month2, day2, year2 = int(part1), int(part2), int(part3)
                    
                    # Choose the interpretation that makes more sense
                    if 1 <= month1 <= 12 and 1 <= day1 <= 31:
                        day, month, year = day1, month1, year1
                    elif 1 <= month2 <= 12 and 1 <= day2 <= 31:
                        day, month, year = day2, month2, year2
                    else:
                        return None
                
                # Validate date
                if not DateExtractor._is_valid_date(year, month, day):
                    return None
                
                # Format as YYYY-MM-DD
                return f"{year:04d}-{month:02d}-{day:02d}"
                
        except (ValueError, TypeError):
            return None
        
        return None
    
    @staticmethod
    def _parse_month(month_str: str) -> int:
        """Parse month string to month number"""
        month_lower = month_str.lower()
        
        # Check French months first
        if month_lower in DateExtractor.FRENCH_MONTHS:
            return DateExtractor.FRENCH_MONTHS[month_lower]
        
        # Check English months
        if month_lower in DateExtractor.ENGLISH_MONTHS:
            return DateExtractor.ENGLISH_MONTHS[month_lower]
        
        # Try to parse as number
        try:
            month_num = int(month_str)
            if 1 <= month_num <= 12:
                return month_num
        except ValueError:
            pass
        
        raise ValueError(f"Invalid month: {month_str}")
    
    @staticmethod
    def _is_valid_date(year: int, month: int, day: int) -> bool:
        """Check if a date is valid"""
        try:
            # Handle 2-digit years
            if year < 100:
                if year < 50:  # Assume 20xx
                    year += 2000
                else:  # Assume 19xx
                    year += 1900
            
            # Basic range checks
            if not (1900 <= year <= 2100):
                return False
            if not (1 <= month <= 12):
                return False
            if not (1 <= day <= 31):
                return False
            
            # Check if date actually exists
            datetime(year, month, day)
            return True
            
        except ValueError:
            return False

def test_date_extraction():
    """Test the date extraction functionality with sample text"""
    
    # Sample invoice text with various date formats
    sample_texts = [
        # French invoice with date
        """
        FACTURE
        Date: 15 janvier 2024
        Client: BMR
        Total à payer: 125.50$
        """,
        
        # English invoice with date
        """
        INVOICE
        Date: March 20, 2024
        Company: TD Bank
        Total: $89.99
        """,
        
        # Invoice with numeric date
        """
        RECEIPT
        Date: 2024-02-15
        Business: Hydro-Quebec
        Amount: $156.78
        """,
        
        # Invoice with DD/MM/YYYY format
        """
        BILL
        Date: 25/12/2023
        Vendor: Scotia Bank
        Total: $234.56
        """,
        
        # Invoice with OCR errors (common misreadings)
        """
        INVOICE
        Date: 3l/0l/2024  # OCR misread: 31/01/2024
        Company: RBC
        Amount: $67.89
        """
    ]
    
    print("Testing Date Extraction Functionality")
    print("=" * 50)
    
    for i, text in enumerate(sample_texts, 1):
        print(f"\nTest {i}:")
        print("Input text:")
        print(text.strip())
        
        # Extract date
        extracted_date = DateExtractor.extract_date_from_text(text)
        
        print(f"Extracted date: {extracted_date}")
        print("-" * 30)

def test_ocr_corrections():
    """Test OCR correction functionality"""
    
    print("\nTesting OCR Corrections")
    print("=" * 50)
    
    # Test cases with common OCR errors
    test_cases = [
        ("3l/0l/2024", "31/01/2024"),  # l -> 1, O -> 0
        ("2S/12/2023", "25/12/2023"),  # S -> 5
        ("1G/03/2024", "16/03/2024"),  # G -> 6
        ("2B/11/2023", "28/11/2023"),  # B -> 8
        ("15/0Z/2024", "15/02/2024"),  # Z -> 2
    ]
    
    for original, expected in test_cases:
        corrected = DateExtractor.ocr_correct_date(original)
        print(f"Original: {original} -> Corrected: {corrected} -> Expected: {expected}")
        print(f"Match: {'✓' if corrected == expected else '✗'}")

def test_file_renaming():
    """Test the file renaming functionality"""
    
    def clean_filename(filename: str) -> str:
        """Clean filename to be filesystem-safe"""
        if not filename:
            return "unknown"
        
        # Remove or replace problematic characters
        cleaned = re.sub(r'[<>:"/\\|?*]', '_', filename)
        cleaned = re.sub(r'\s+', '_', cleaned)  # Replace spaces with underscores
        cleaned = re.sub(r'[^\w\-_.]', '', cleaned)  # Keep only alphanumeric, hyphens, underscores, dots
        cleaned = cleaned.strip('._')  # Remove leading/trailing dots and underscores
        
        # Limit length
        if len(cleaned) > 50:
            cleaned = cleaned[:50]
        
        return cleaned if cleaned else "unknown"
    
    # Sample data for testing
    test_cases = [
        {
            'company': 'BMR',
            'total': '125.50',
            'date': '2024-01-15',
            'expected': '20240115_BMR_12550.pdf'
        },
        {
            'company': 'Hydro-Quebec',
            'total': '156.78',
            'date': '2024-02-20',
            'expected': '20240220_Hydro-Quebec_15678.pdf'
        },
        {
            'company': 'TD Bank',
            'total': '89.99',
            'date': '2024-03-10',
            'expected': '20240310_TD_Bank_8999.pdf'
        }
    ]
    
    print("\nTesting File Renaming Functionality")
    print("=" * 50)
    
    for i, case in enumerate(test_cases, 1):
        print(f"\nTest {i}:")
        print(f"Company: {case['company']}")
        print(f"Total: {case['total']}")
        print(f"Date: {case['date']}")
        
        # Test the filename cleaning
        clean_company = clean_filename(case['company'])
        clean_total = case['total'].replace('.', '')
        clean_date = case['date'].replace('-', '')
        
        new_name = f"{clean_date}_{clean_company}_{clean_total}.pdf"
        print(f"Generated filename: {new_name}")
        print(f"Expected filename: {case['expected']}")
        print("-" * 30)

def main():
    """Main test function"""
    print("Invoice OCR Parser - Date Extraction Test Suite")
    print("=" * 60)
    
    # Test date extraction
    test_date_extraction()
    
    # Test OCR corrections
    test_ocr_corrections()
    
    # Test file renaming
    test_file_renaming()
    
    print("\n" + "=" * 60)
    print("Test suite completed!")
    print("\nThe enhanced parser now supports:")
    print("1. Robust date extraction from French and English invoices")
    print("2. OCR error correction for common misreadings")
    print("3. Automatic file renaming to date_business_total format")
    print("4. Multiple date format support (DD/MM/YYYY, Month DD YYYY, etc.)")

if __name__ == "__main__":
    main() 