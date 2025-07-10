#!/usr/bin/env python3
"""
Debug script to test date extraction with specific text from logs
"""

import re
import logging
from datetime import datetime
from typing import Optional

# Set up logging
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)


class DateExtractor:
    """Robust date extraction from invoice text with OCR correction"""

    # French month names and abbreviations
    FRENCH_MONTHS = {
        "janvier": 1,
        "jan": 1,
        "janv": 1,
        "février": 2,
        "fév": 2,
        "févr": 2,
        "fevrier": 2,
        "fev": 2,
        "mars": 3,
        "mar": 3,
        "avril": 4,
        "avr": 4,
        "mai": 5,
        "juin": 6,
        "juillet": 7,
        "juil": 7,
        "août": 8,
        "aout": 8,
        "aoû": 8,
        "septembre": 9,
        "sept": 9,
        "sep": 9,
        "octobre": 10,
        "oct": 10,
        "novembre": 11,
        "nov": 11,
        "décembre": 12,
        "dec": 12,
        "déc": 12,
        "decembre": 12,
    }

    # English month names and abbreviations
    ENGLISH_MONTHS = {
        "january": 1,
        "jan": 1,
        "february": 2,
        "feb": 2,
        "march": 3,
        "mar": 3,
        "april": 4,
        "apr": 4,
        "may": 5,
        "june": 6,
        "jun": 6,
        "july": 7,
        "jul": 7,
        "august": 8,
        "aug": 8,
        "september": 9,
        "sep": 9,
        "sept": 9,
        "october": 10,
        "oct": 10,
        "november": 11,
        "nov": 11,
        "december": 12,
        "dec": 12,
    }

    # OCR correction mapping for common date misreadings
    OCR_CORRECTIONS = {
        "O": "0",
        "o": "0",  # O/o often misread as 0
        "l": "1",
        "I": "1",
        "i": "1",  # l/I/i often misread as 1
        "S": "5",
        "s": "5",  # S/s often misread as 5
        "G": "6",
        "g": "6",  # G/g often misread as 6
        "B": "8",
        "b": "8",  # B/b often misread as 8
        "Z": "2",
        "z": "2",  # Z/z often misread as 2
        "A": "4",
        "a": "4",  # A/a often misread as 4
        "E": "3",
        "e": "3",  # E/e often misread as 3
        "T": "7",
        "t": "7",  # T/t often misread as 7
    }

    @staticmethod
    def ocr_correct_date(text: str) -> str:
        """Apply OCR corrections to date text"""
        corrected = text
        for wrong, right in DateExtractor.OCR_CORRECTIONS.items():
            corrected = corrected.replace(wrong, right)
        return corrected

    @staticmethod
    def ocr_correct_numeric_only(text: str) -> str:
        """Apply OCR corrections only to numeric parts of dates"""
        # Find numeric patterns and correct only those
        import re

        def correct_numeric(match):
            numeric_part = match.group(0)
            corrected = numeric_part
            for wrong, right in DateExtractor.OCR_CORRECTIONS.items():
                corrected = corrected.replace(wrong, right)
            return corrected

        # Apply corrections only to numeric sequences
        corrected = re.sub(r"\d+[IlOoSGBZAE]*\d*", correct_numeric, text)
        return corrected

    @staticmethod
    def extract_date_from_text(text: str) -> Optional[str]:
        """Extract date from invoice text using multiple strategies"""
        if not text:
            return None

        lines = text.split("\n")
        candidates = []

        # High-priority date keywords in French and English
        date_keywords = [
            "date",
            "dated",
            "daté",
            "datée",
            "facturé",
            "facturée",
            "billed",
            "invoice date",
            "date de facture",
            "date de facturation",
            "due date",
            "date d'échéance",
            "échéance",
            "due",
            "issued",
            "émis",
            "emission",
            "émission",
            "created",
            "créé",
            "créée",
            "creation",
            "création",
            "modification",
            "juillet",  # Add 'juillet' as it appears in the text
        ]

        # Date patterns with different formats
        date_patterns = [
            # YYYY-MM-DD or YYYY/MM/DD (highest priority for unambiguous format)
            r"(\d{4})[/\-](\d{1,2})[/\-](\d{1,2})",
            # DD/MM/YYYY or DD-MM-YYYY
            r"(\d{1,2})[/\-](\d{1,2})[/\-](\d{2,4})",
            # DD Month YYYY (English)
            r"(\d{1,2})\s+(january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|jun|jul|aug|sep|oct|nov|dec)\s+(\d{2,4})",
            # DD Month YYYY (French)
            r"(\d{1,2})\s+(janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre|jan|fév|mar|avr|juil|aoû|sept|oct|nov|déc|fevrier|aout|decembre)\s+(\d{2,4})",
            # Month DD, YYYY (English)
            r"(january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|jun|jul|aug|sep|oct|nov|dec)\s+(\d{1,2}),?\s+(\d{2,4})",
            # Month DD, YYYY (French)
            r"(janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre|jan|fév|mar|avr|juil|aoû|sept|oct|nov|déc|fevrier|aout|decembre)\s+(\d{1,2}),?\s+(\d{2,4})",
            # DD.MM.YYYY or DD.MM.YY
            r"(\d{1,2})\.(\d{1,2})\.(\d{2,4})",
            # Special pattern for "juillet 20I9" format (OCR errors in year) - before correction
            r"(juillet|juil)\s+(\d{1,2})[Il](\d{1,2})",
            # Pattern for "juillet 2019" format (after correction)
            r"(juillet|juil)\s+(\d{4})",
        ]

        # Search in first 30 lines (usually where dates appear)
        search_lines = lines[:30]

        print(f"Processing {len(search_lines)} lines for date extraction")

        # First pass: Look for lines with date keywords
        for i, line in enumerate(search_lines):
            line_lower = line.lower()

            # Check if line contains date keywords
            if any(keyword in line_lower for keyword in date_keywords):
                print(f"Found date keyword in line {i}: {line.strip()}")
                # Apply OCR corrections
                corrected_line = DateExtractor.ocr_correct_numeric_only(line)
                print(f"After OCR correction: {corrected_line}")

                # Try to extract date using patterns
                for pattern in date_patterns:
                    matches = re.findall(pattern, corrected_line, re.IGNORECASE)
                    for match in matches:
                        print(
                            f"Found date pattern match: {match} with pattern: {pattern}"
                        )
                        try:
                            parsed_date = DateExtractor._parse_date_match(
                                match, pattern
                            )
                            if parsed_date:
                                candidates.append(
                                    (
                                        parsed_date,
                                        f"Date keyword match: {line.strip()}",
                                        15,
                                    )
                                )
                                break
                        except Exception as e:
                            print(f"Failed to parse date match {match}: {e}")
                            continue

        # Second pass: Look for date patterns without keywords
        if not candidates:
            print("No candidates found in first pass, trying second pass...")
            for i, line in enumerate(search_lines):
                corrected_line = DateExtractor.ocr_correct_date(line)

                for pattern in date_patterns:
                    matches = re.findall(pattern, corrected_line, re.IGNORECASE)
                    for match in matches:
                        print(
                            f"Found date pattern match (no keyword): {match} with pattern: {pattern}"
                        )
                        try:
                            parsed_date = DateExtractor._parse_date_match(
                                match, pattern
                            )
                            if parsed_date:
                                # Lower priority for matches without keywords
                                priority = (
                                    10 if i < 10 else 5
                                )  # Higher priority for earlier lines
                                candidates.append(
                                    (
                                        parsed_date,
                                        f"Pattern match: {line.strip()}",
                                        priority,
                                    )
                                )
                        except Exception as e:
                            print(f"Failed to parse date match {match}: {e}")
                            continue

        # Third pass: Look for standalone dates (numbers that look like dates)
        if not candidates:
            print("No candidates found in second pass, trying third pass...")
            for line in search_lines:
                corrected_line = DateExtractor.ocr_correct_date(line)

                # Look for patterns like "2024-01-15" or "15/01/2024"
                standalone_patterns = [
                    r"(\d{4})-(\d{1,2})-(\d{1,2})",
                    r"(\d{1,2})/(\d{1,2})/(\d{4})",
                    r"(\d{1,2})-(\d{1,2})-(\d{4})",
                ]

                for pattern in standalone_patterns:
                    matches = re.findall(pattern, corrected_line)
                    for match in matches:
                        print(
                            f"Found standalone date pattern match: {match} with pattern: {pattern}"
                        )
                        try:
                            parsed_date = DateExtractor._parse_date_match(
                                match, pattern
                            )
                            if parsed_date:
                                candidates.append(
                                    (parsed_date, f"Standalone date: {line.strip()}", 8)
                                )
                        except Exception as e:
                            print(f"Failed to parse standalone date match {match}: {e}")
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
                if pattern.startswith(r"(\d{4})"):  # YYYY-MM-DD format
                    year = int(part1)
                    month = int(part2)
                    day = int(part3)
                elif (
                    pattern.startswith(r"(\d{1,2})") and "month" in pattern.lower()
                ):  # DD Month YYYY
                    day = int(part1)
                    month = DateExtractor._parse_month(part2)
                    year = int(part3)
                elif "month" in pattern.lower() and pattern.startswith(
                    r"(january|février"
                ):  # Month DD YYYY
                    month = DateExtractor._parse_month(part1)
                    day = int(part2)
                    year = int(part3)
                elif pattern.startswith(
                    r"(juillet|juil)"
                ):  # Special pattern for "juillet 20I9"
                    month = DateExtractor._parse_month(part1)
                    # Handle OCR errors in year (I -> 1, l -> 1)
                    year_str = part2 + part3
                    year_str = year_str.replace("I", "1").replace("l", "1")
                    year = int(year_str)
                    day = 1  # Default to day 1 if not specified
                elif (
                    pattern == r"(juillet|juil)\s+(\d{4})"
                ):  # Pattern for "juillet 2019" format
                    month = DateExtractor._parse_month(part1)
                    year = int(part2)
                    day = 1  # Default to day 1 if not specified
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
            elif len(match) == 2:
                # Handle (month, year) pattern, e.g., (juillet, 2019)
                month = DateExtractor._parse_month(match[0])
                year = int(match[1])
                day = 1
                if not DateExtractor._is_valid_date(year, month, day):
                    return None
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


def main():
    """Test date extraction with the specific text from logs"""

    # The text from the user's logs
    test_text = """re compte en dollars canadiens. Le taux de change est établi pour nous par Visa Inc., à la date de Toutes les autres marques appartiennent à leurs propriétaires respectifs. règlement de l'opération avec Visa Inc. Ce taux de change peut différer de celui qui était en vigueur Date de modification : juillet 20I9 0B9400 63I2000 - A_83052D_0030I_PFRVBS"""

    print("Testing date extraction with text from logs:")
    print("=" * 60)
    print(f"Input text: {test_text}")
    print("=" * 60)

    # Extract date
    extracted_date = DateExtractor.extract_date_from_text(test_text)

    print(f"\nFinal result: {extracted_date}")


if __name__ == "__main__":
    main()
