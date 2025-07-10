"""Date extraction utilities for OCR text processing."""

import logging
import re
from typing import Optional, Tuple
from datetime import datetime


class DateExtractor:
    """Robust date extraction from invoice text with OCR correction."""

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
        """Apply OCR corrections to date text."""
        corrected = text
        for wrong, right in DateExtractor.OCR_CORRECTIONS.items():
            corrected = corrected.replace(wrong, right)
        return corrected

    @staticmethod
    def ocr_correct_numeric_only(text: str) -> str:
        """Apply OCR corrections only to numeric parts of dates."""

        def correct_numeric(match):
            numeric_part = match.group(0)
            corrected = numeric_part
            for wrong, right in DateExtractor.OCR_CORRECTIONS.items():
                corrected = corrected.replace(wrong, right)
            return corrected

        corrected = re.sub(r"\d+[IlOoSGBZAE]*\d*", correct_numeric, text)
        return corrected

    @staticmethod
    def extract_date_from_text(text: str) -> Optional[str]:
        """Extract date from invoice text using multiple strategies with robust OCR error handling."""
        if not text:
            return None
        lines = text.split("\n")
        candidates = []
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
            "juillet",
            "relevé",
            "releve",
        ]
        robust_date_patterns = [
            r"(\d{3}[0-9Oo])\s*[/\-]\s*(\d{1,2})\s*[/\-]\s*(\d{1,2})",
            r"(\d{1,2})\s*[/\-]\s*(\d{1,2})\s*[/\-]\s*(\d{3}[0-9Oo])",
            r"(\d{1,2})\s+(january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|jun|jul|aug|sep|oct|nov|dec)\s+(\d{3}[0-9Oo])",
            r"(\d{1,2})\s+(janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre|jan|fév|mar|avr|juil|aoû|sept|oct|nov|déc|fevrier|aout|decembre)\s+(\d{3}[0-9Oo])",
            r"(january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|jun|jul|aug|sep|oct|nov|dec)\s+(\d{1,2}),?\s+(\d{3}[0-9Oo])",
            r"(janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre|jan|fév|mar|avr|juil|aoû|sept|oct|nov|déc|fevrier|aout|decembre)\s+(\d{1,2}),?\s+(\d{3}[0-9Oo])",
            r"(\d{1,2})\.(\d{1,2})\.(\d{3}[0-9Oo])",
            r"(juillet|juil)\s+(\d{1,2})[Il](\d{1,2})",
            r"(juillet|juil)\s+(\d{4})",
            r"(\d{1,2})\s+(jan|fév|mar|avr|mai|juin|juil|aoû|sept|oct|nov|déc|fevrier|aout|decembre)\s+(\d{3}[0-9OoSs])",
            r"date\s+du\s+relevé\s*:\s*(\d{1,2})\s+(jan|fév|mar|avr|mai|juin|juil|aoû|sept|oct|nov|déc|fevrier|aout|decembre)\s+(\d{3}[0-9OoSs])",
            r"date\s+du\s+relevé\s*:\s*(\d{1,2})\s+(jan|fév|mar|avr|mai|juin|juil|aoû|sept|oct|nov|déc|fevrier|aout|decembre)\s+(\d{3}[0-9OoSs])",
        ]
        search_lines = lines[:30]
        for i, line in enumerate(search_lines):
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in date_keywords):
                logging.debug(f"Found date keyword in line {i}: {line.strip()}")
                for pattern in robust_date_patterns:
                    matches = re.findall(pattern, line, re.IGNORECASE)
                    for match in matches:
                        logging.debug(
                            f"Found robust date pattern match: {match} with pattern: {pattern}"
                        )
                        try:
                            parsed_date = DateExtractor._parse_robust_date_match(
                                match, pattern
                            )
                            if parsed_date:
                                candidates.append(
                                    (
                                        parsed_date,
                                        f"Robust date keyword match: {line.strip()}",
                                        20,
                                    )
                                )
                                break
                        except Exception as e:
                            logging.debug(
                                f"Failed to parse robust date match {match}: {e}"
                            )
                            continue
        if not candidates:
            for i, line in enumerate(search_lines):
                for pattern in robust_date_patterns:
                    matches = re.findall(pattern, line, re.IGNORECASE)
                    for match in matches:
                        logging.debug(
                            f"Found robust date pattern match (no keyword): {match} with pattern: {pattern}"
                        )
                        try:
                            parsed_date = DateExtractor._parse_robust_date_match(
                                match, pattern
                            )
                            if parsed_date:
                                priority = 15 if i < 10 else 10
                                candidates.append(
                                    (
                                        parsed_date,
                                        f"Robust pattern match: {line.strip()}",
                                        priority,
                                    )
                                )
                        except Exception as e:
                            logging.debug(
                                f"Failed to parse robust date match {match}: {e}"
                            )
                            continue
        if candidates:
            candidates.sort(key=lambda x: (x[2]), reverse=True)
            best_date, source_line, priority = candidates[0]
            logging.info(f"Found invoice date: '{best_date}' from line: {source_line}")
            return best_date
        logging.info("No invoice date found")
        return None

    @staticmethod
    def _parse_robust_date_match(match: tuple, pattern: str) -> Optional[str]:
        try:
            if len(match) == 3:
                part1, part2, part3 = match
                part1_corrected = (
                    DateExtractor.ocr_correct_date(part1) if part1.isdigit() else part1
                )
                part2_corrected = (
                    DateExtractor.ocr_correct_date(part2) if part2.isdigit() else part2
                )
                part3_corrected = (
                    DateExtractor.ocr_correct_date(part3) if part3.isdigit() else part3
                )
                logging.debug(
                    f"OCR correction: {part1}->{part1_corrected}, {part2}->{part2_corrected}, {part3}->{part3_corrected}"
                )
                if pattern.startswith(r"(\d{3}[0-9Oo])"):
                    year = int(part1_corrected)
                    month = int(part2_corrected)
                    day = int(part3_corrected)
                elif pattern.startswith(r"(\d{1,2})") and "month" in pattern.lower():
                    day = int(part1_corrected)
                    month = DateExtractor._parse_month(part2)
                    year = int(part3_corrected)
                elif "month" in pattern.lower() and pattern.startswith(
                    r"(january|février"
                ):
                    month = DateExtractor._parse_month(part1)
                    day = int(part2_corrected)
                    year = int(part3_corrected)
                elif pattern.startswith(r"(juillet|juil)"):
                    month = DateExtractor._parse_month(part1)
                    year_str = part2_corrected + part3_corrected
                    year = int(year_str)
                    day = 1
                elif pattern == r"(juillet|juil)\s+(\d{4})":
                    month = DateExtractor._parse_month(part1)
                    year = int(part2_corrected)
                    day = 1
                elif "relevé" in pattern.lower():
                    day = int(part1_corrected)
                    month = DateExtractor._parse_month(part2)
                    year = int(part3_corrected)
                else:
                    day1, month1, year1 = (
                        int(part1_corrected),
                        int(part2_corrected),
                        int(part3_corrected),
                    )
                    month2, day2, year2 = (
                        int(part1_corrected),
                        int(part2_corrected),
                        int(part3_corrected),
                    )
                    if 1 <= month1 <= 12 and 1 <= day1 <= 31:
                        day, month, year = day1, month1, year1
                    elif 1 <= month2 <= 12 and 1 <= day2 <= 31:
                        day, month, year = day2, month2, year2
                    else:
                        return None
                if not DateExtractor._is_valid_date(year, month, day):
                    return None
                return f"{year:04d}-{month:02d}-{day:02d}"
            elif len(match) == 2:
                month = DateExtractor._parse_month(match[0])
                year = int(DateExtractor.ocr_correct_date(match[1]))
                day = 1
                if not DateExtractor._is_valid_date(year, month, day):
                    return None
                return f"{year:04d}-{month:02d}-{day:02d}"
        except (ValueError, TypeError) as e:
            logging.debug(f"Failed to parse robust date match {match}: {e}")
            return None
        return None

    @staticmethod
    def _apply_ocr_correction_to_year(match: str) -> Optional[int]:
        year_str = match
        year_str = (
            year_str.replace("I", "1")
            .replace("l", "1")
            .replace("O", "0")
            .replace("o", "0")
            .replace("S", "5")
            .replace("s", "5")
            .replace("G", "6")
            .replace("g", "6")
            .replace("B", "8")
            .replace("b", "8")
            .replace("Z", "2")
            .replace("z", "2")
            .replace("A", "4")
            .replace("a", "4")
            .replace("E", "3")
            .replace("e", "3")
            .replace("T", "7")
            .replace("t", "7")
        )
        try:
            return int(year_str)
        except ValueError:
            return None

    @staticmethod
    def _extract_month_day_from_line(line: str) -> Optional[Tuple[int, int]]:
        line_lower = line.lower()
        for month_name, month_num in DateExtractor.FRENCH_MONTHS.items():
            if month_name in line_lower:
                day_match = re.search(r"(\d{1,2})", line_lower)
                if day_match:
                    day = int(day_match.group(0))
                    return (month_num, day)
        for month_name, month_num in DateExtractor.ENGLISH_MONTHS.items():
            if month_name in line_lower:
                day_match = re.search(r"(\d{1,2})", line_lower)
                if day_match:
                    day = int(day_match.group(0))
                    return (month_num, day)
        return None

    @staticmethod
    def _parse_month(month_str: str) -> int:
        month_lower = month_str.lower()
        if month_lower in DateExtractor.FRENCH_MONTHS:
            return DateExtractor.FRENCH_MONTHS[month_lower]
        if month_lower in DateExtractor.ENGLISH_MONTHS:
            return DateExtractor.ENGLISH_MONTHS[month_lower]
        try:
            month_num = int(month_str)
            if 1 <= month_num <= 12:
                return month_num
        except ValueError:
            pass
        raise ValueError(f"Invalid month: {month_str}")

    @staticmethod
    def _is_valid_date(year: int, month: int, day: int) -> bool:
        try:
            if year < 100:
                if year < 50:
                    year += 2000
                else:
                    year += 1900
            if not (1900 <= year <= 2100):
                return False
            if not (1 <= month <= 12):
                return False
            if not (1 <= day <= 31):
                return False
            datetime(year, month, day)
            return True
        except Exception:
            return False
