"""Invoice parser for extracting structured data from invoice PDFs."""

import logging
import re
from pathlib import Path
from typing import Dict, Any, Optional, Union, List

from .base_parser import BaseParser
from .date_extractor import DateExtractor
from ..business.business_alias_manager import BusinessAliasManager


class InvoiceParser(BaseParser):
    """Parser for extracting invoice data from PDFs using OCR."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        # Ensure config is never None
        config = config or {}
        super().__init__(config)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.debug = config.get("debug", False)
        self.company_keywords = config.get(
            "company_keywords", ["company", "inc", "ltd", "corp"]
        )
        self.total_keywords = config.get("total_keywords", ["TOTAL", "AMOUNT DUE"])
        self.date_keywords = config.get("date_keywords", ["DATE", "INVOICE DATE"])
        self.parser_type = "invoice"
        # Initialize business alias manager for company name matching
        try:
            self.business_alias_manager = BusinessAliasManager()
        except Exception as e:
            self.logger.warning(f"Could not initialize BusinessAliasManager: {e}")
            self.business_alias_manager = None

    def parse(self, pdf_path: Union[str, Path], max_retries: int = 3) -> Dict[str, Any]:
        """Parse the invoice PDF and return structured data."""
        # Retry extract_text up to max_retries times
        text = None
        last_exception = None

        for attempt in range(max_retries):
            try:
                text = self.extract_text(pdf_path)
                break
            except Exception as e:
                last_exception = e
                if attempt == max_retries - 1:
                    raise last_exception
                continue

        if text is None:
            text = ""

        # Try extraction on raw text first, then fallback to corrected text if not found
        ocr_corrections = self.ocr_corrections
        corrected_text = ocr_corrections.correct_text(text)

        # Company
        company = self.extract_company(text)
        if not company:
            company = self.extract_company(corrected_text)

        # Total
        total = self.extract_total(text)
        if not total:
            total = self.extract_total(corrected_text)

        # Date
        date = self.extract_date(text)
        if not date:
            date = self.extract_date(corrected_text)

        # Invoice number
        invoice_number = self.extract_invoice_number(text)
        if not invoice_number:
            invoice_number = self.extract_invoice_number(corrected_text)

        result = {
            "company": company,
            "total": total,
            "date": date,
            "invoice_number": invoice_number,
            "raw_text": text,
            "parser_type": "invoice",
        }

        # Use base parser validation and confidence calculation
        result = self.validate_extraction_result(result)
        
        # Additional invoice-specific validation
        invoice_valid = self._validate_invoice_data(result)
        
        # If invoice validation fails, mark as invalid
        if not invoice_valid:
            result["is_valid"] = False
            result["invoice_validation_failed"] = True

        self.log_parsing_result(pdf_path, result)

        return result

    def extract_company(self, text: str) -> Optional[str]:
        """Extract company name from text using multiple strategies."""
        if not text:
            return None

        lines = [line.strip() for line in text.split("\n")]
        search_lines = lines[:20]
        # Use BusinessAliasManager for company name matching
        if self.business_alias_manager:
            print(f"[DEBUG] extract_company: Searching text for business matches...")
            print(
                f"[DEBUG] extract_company: Text sample (first 200 chars): {text[:200]}"
            )
            print(f"[DEBUG] extract_company: Full text length: {len(text)}")
            print(
                f"[DEBUG] extract_company: Text contains 'GAGNON': {'GAGNON' in text}"
            )
            print(
                f"[DEBUG] extract_company: Text contains 'gagnon': {'gagnon' in text}"
            )
            result = self.business_alias_manager.find_business_match(text)
            if result:
                official_name, match_type, confidence = result
                print(
                    f"[DEBUG] extract_company: Found company using BusinessAliasManager: '{official_name}' ({match_type}, confidence: {confidence})"
                )
                return official_name.lower()
            else:
                print(f"[DEBUG] extract_company: No business match found in text")
        else:
            print(f"[DEBUG] extract_company: BusinessAliasManager not available")

        # 1. If any known company is present anywhere in the text, return the first one
        # Note: This fallback is only used if BusinessAliasManager is not available
        # All business names should be configured in business_aliases.json
        text_lower = text.lower()
        known_companies = self.config.get("known_companies", [])
        if known_companies:
            for company in known_companies:
                if company.lower() in text_lower:
                    self.logger.debug(f"extract_company: Found known company: '{company}'")
                    return company.lower()
        # 2. After 'INVOICE' or similar, next non-empty line is likely company
        found_header = False
        for line in search_lines:
            if not line:
                continue
            # Do not return lines that look like dates or contain 'Date:'
            if re.match(r"\d{4}-\d{2}-\d{2}", line) or "date:" in line.lower():
                continue
            if any(
                keyword.lower() in line.lower() for keyword in self.company_keywords
            ):
                parts = line.split(":", 1)
                if len(parts) > 1:
                    company = parts[1].strip()
                    if company:
                        return company.lower()
            if not found_header and any(h in line.upper() for h in ["INVOICE", "BILL"]):
                found_header = True
                continue
            if (
                found_header
                and line
                and not any(
                    kw in line.upper()
                    for kw in ["TOTAL", "AMOUNT", "DUE", "BALANCE", "INVOICE", "BILL"]
                )
            ):
                # Do not return lines that look like dates or contain 'Date:'
                if re.match(r"\d{4}-\d{2}-\d{2}", line) or "date:" in line.lower():
                    continue
                return line.lower()
        # 3. Fuzzy match: extract candidate lines and match to known_companies
        # Note: This fallback is only used if BusinessAliasManager is not available
        # All business names should be configured in business_aliases.json
        from ..utils.fuzzy_matcher import FuzzyMatcher

        fuzzy_matcher = FuzzyMatcher()
        candidate_lines = [
            line
            for line in lines
            if line
            and not re.match(r"\d{4}-\d{2}-\d{2}", line)
            and "date:" not in line.lower()
        ]
        best_match = None
        best_score = 0.0
        known_companies = self.config.get("known_companies", [])
        if known_companies:
            for candidate in candidate_lines:
                match, score = fuzzy_matcher.find_best_match(candidate, known_companies)
                if score > best_score:
                    best_score = score
                    best_match = match
            if best_match and best_score > 0.8:
                return best_match.lower()
        return None

    def extract_total(self, text: str) -> Optional[float]:
        """Extract invoice total from text using a two-stage approach: raw OCR text first, then cleaned."""
        if not text:
            return None

        from typing import List, Tuple, Callable

        def find_nearby_amounts(
            text: str, keywords: List[str], max_distance: int = 50
        ) -> List[str]:
            """Find currency amounts within max_distance characters of any keyword."""
            amounts: List[str] = []
            text_lower = text.lower()
            # Find all keyword positions
            keyword_positions: List[int] = []
            for keyword in keywords:
                pos = 0
                while True:
                    pos = text_lower.find(keyword, pos)
                    if pos == -1:
                        break
                    keyword_positions.append(pos)
                    pos += 1
            # Find all currency amounts (including whole numbers)
            currency_pattern = r"\$?\d+(?:[.,]\d{3})*(?:[.,]\d{2})?"
            for match in re.finditer(currency_pattern, text):
                amount_start = match.start()
                amount_end = match.end()
                amount_text = match.group()
                # Check if this amount is near any keyword
                for keyword_pos in keyword_positions:
                    if (
                        abs(amount_start - keyword_pos) <= max_distance
                        or abs(amount_end - keyword_pos) <= max_distance
                    ):
                        amounts.append(amount_text)
                        break
            return amounts

        def normalize_amount(amount_str: str) -> float:
            """Convert amount string to float, handling different decimal separators."""
            cleaned = (
                amount_str.replace("$", "")
                .replace("€", "")
                .replace("£", "")
                .replace("¥", "")
            )
            if "," in cleaned and "." in cleaned:
                comma_pos = cleaned.rfind(",")
                dot_pos = cleaned.rfind(".")
                if comma_pos > dot_pos:
                    cleaned = cleaned.replace(".", "").replace(",", ".")
                else:
                    cleaned = cleaned.replace(",", "")
            elif "," in cleaned and "." not in cleaned:
                if cleaned.count(",") == 1 and len(cleaned.split(",")[1]) == 2:
                    cleaned = cleaned.replace(",", ".")
                else:
                    cleaned = cleaned.replace(",", "")
            return float(cleaned)

        def filter_valid_amounts(amounts: List[str]) -> List[float]:
            float_amounts: List[float] = []
            for amount_str in amounts:
                try:
                    value = normalize_amount(amount_str)
                    if 0.01 <= value <= 10000:
                        float_amounts.append(value)
                except (ValueError, TypeError):
                    continue
            return float_amounts

        # Use self.total_keywords if set, otherwise use the default list
        total_keywords = [
            "total",
            "tota",
            "mastercard",
            "visa",
            "amex",
            "american express",
            "credit card",
            "debit card",
            "card payment",
            "amount due",
            "grand total",
            "final total",
            "balance due",
        ]
        if hasattr(self, "total_keywords") and self.total_keywords:
            total_keywords = [kw.lower() for kw in self.total_keywords]

        raw_amounts = find_nearby_amounts(text, total_keywords, max_distance=50)
        print("[DEBUG] RAW nearby amounts:", raw_amounts)
        print("[DEBUG] Total keywords being searched:", total_keywords)
        print("[DEBUG] Text sample (first 200 chars):", text[:200])

        # Debug: Show all amounts before range filtering
        all_raw_floats = []
        for amount_str in raw_amounts:
            try:
                value = normalize_amount(amount_str)
                all_raw_floats.append(value)
            except (ValueError, TypeError) as e:
                print(f"[DEBUG] Failed to parse amount '{amount_str}': {e}")
        print("[DEBUG] All raw float amounts (before range filtering):", all_raw_floats)

        def filter_out_years_and_small_ints(amounts: List[float]) -> List[float]:
            # Remove values that look like years (1900-2099) or small ints (1-10)
            filtered = [a for a in amounts if not (1900 <= a <= 2099 or 1 <= a <= 10)]
            return filtered if filtered else amounts  # fallback to original if all filtered

        raw_floats = filter_valid_amounts(raw_amounts)
        raw_floats = filter_out_years_and_small_ints(raw_floats)
        print("[DEBUG] RAW float amounts (10-10000, filtered):", raw_floats)
        if len(raw_floats) == 1:
            print("[DEBUG] Selected total from RAW nearby search:", raw_floats[0])
            return float(raw_floats[0])
        elif len(raw_floats) > 1:
            from collections import Counter

            counter = Counter(raw_floats)
            most_common, count = counter.most_common(1)[0]
            if list(counter.values()).count(count) == 1 and count > 1:
                print(
                    f"[DEBUG] Selected most frequent total from RAW nearby search: "
                    f"{most_common} (appeared {count} times)"
                )
                return float(most_common)

        # Fallback: line-based search for amounts on lines containing keywords
        print("[DEBUG] Proximity search failed, trying line-based fallback.")
        lines = [line.strip() for line in text.split("\n")]
        line_amounts = []
        for line in lines:
            line_lower = line.lower()
            if any(kw in line_lower for kw in total_keywords):
                found = re.findall(r"\$?\d+(?:[.,]\d{3})*(?:[.,]\d{2})?", line)
                line_amounts.extend(found)
        print("[DEBUG] Line-based fallback amounts:", line_amounts)
        line_floats = filter_valid_amounts(line_amounts)
        line_floats = filter_out_years_and_small_ints(line_floats)
        print("[DEBUG] Line-based fallback float amounts (0.01-10000, filtered):", line_floats)
        if len(line_floats) == 1:
            print("[DEBUG] Selected total from line-based fallback:", line_floats[0])
            return float(line_floats[0])
        elif len(line_floats) > 1:
            from collections import Counter

            counter = Counter(line_floats)
            most_common, count = counter.most_common(1)[0]
            if list(counter.values()).count(count) == 1 and count > 1:
                print(
                    f"[DEBUG] Selected most frequent total from line-based fallback: "
                    f"{most_common} (appeared {count} times)"
                )
                return float(most_common)

        lines = [line.strip() for line in text.split("\n")]
        if len(lines) == 1 and len(lines[0]) > 200:
            long_line = lines[0]
            split_text = re.split(r"[;,]|\s{3,}", long_line)
            lines = [line.strip() for line in split_text if line.strip()]

        def find_total_candidates(
            lines: List[str], extract_amounts_func: Callable[[str], List[str]]
        ) -> Tuple[List[str], List[str]]:
            total_amounts: List[str] = []
            preferred_amounts: List[str] = []
            total_line_amounts: List[str] = []
            for line in lines:
                line_lower = line.lower()
                if (
                    re.search(r"tota[^a-z]*\s*:", line_lower)
                    and "subtotal:" not in line_lower
                ):
                    amounts = extract_amounts_func(line)
                    if amounts:
                        total_amounts.extend(amounts)
                        preferred_amounts.extend(amounts)
                        total_line_amounts.extend(amounts)
                elif any(
                    keyword in line_lower
                    for keyword in [
                        "mastercard",
                        "visa",
                        "amex",
                        "american express",
                        "credit card",
                        "debit card",
                        "card payment",
                    ]
                ):
                    amounts = extract_amounts_func(line)
                    if amounts:
                        total_amounts.extend(amounts)
                        preferred_amounts.extend(amounts)
            return total_line_amounts, preferred_amounts

        # If we found amounts in the line-based fallback, use them
        if line_floats:
            # Sort by amount and return the highest (most likely to be the total)
            line_floats.sort()
            print("[DEBUG] Selected highest amount from line-based fallback:", line_floats[-1])
            return float(line_floats[-1])

        total_line_amounts, preferred_amounts = find_total_candidates(
            lines, self._extract_amounts_with_ocr_correction
        )
        print("[DEBUG] CLEANED total line amounts:", total_line_amounts)
        print("[DEBUG] CLEANED preferred amounts:", preferred_amounts)
        cleaned_total_floats = filter_valid_amounts(total_line_amounts)
        if len(cleaned_total_floats) == 1:
            print(
                "[DEBUG] Selected total from CLEANED total line:",
                cleaned_total_floats[0],
            )
            return float(cleaned_total_floats[0])
        cleaned_preferred_floats = filter_valid_amounts(preferred_amounts)
        if len(cleaned_preferred_floats) == 1:
            print(
                "[DEBUG] Selected total from CLEANED preferred:",
                cleaned_preferred_floats[0],
            )
            return float(cleaned_preferred_floats[0])
        print("[DEBUG] Multiple or no candidates, returning None.")
        return None

    def _extract_amounts_with_ocr_correction(self, text: str) -> List[str]:
        """Extract amounts from text with enhanced OCR correction."""
        # First try the normal amount normalizer
        amounts = self.amount_normalizer.extract_amounts_from_text(text)

        # Try with additional OCR corrections
        corrected_text = text
        # Arabic/Unicode decimal separators
        corrected_text = re.sub(r"[٠٫٬]", ".", corrected_text)
        # Space before decimal
        corrected_text = re.sub(r"\s+\.\s*", ".", corrected_text)
        corrected_text = re.sub(r"\.\s+", ".", corrected_text)  # Space after decimal
        more_amounts = self.amount_normalizer.extract_amounts_from_text(corrected_text)
        for amt in more_amounts:
            if amt not in amounts:
                amounts.append(amt)

        # More aggressive OCR correction
        corrected_text = text
        # Fix decimal separators with spaces
        pattern1 = r"(\d{1,3}(?:,\d{3})*)\s*[٠٫٬\.]\s*(\d{2})"
        corrected_text = re.sub(pattern1, r"\1.\2", corrected_text)
        # Fix comma-dot patterns
        pattern2 = r"(\d{1,3}(?:,\d{3})*)\s*,\s*\.\s*(\d{2})"
        corrected_text = re.sub(pattern2, r"\1.\2", corrected_text)
        corrected_text = re.sub(r"(\d+)\s*\.\s*(\d+)", r"\1.\2", corrected_text)
        more_amounts = self.amount_normalizer.extract_amounts_from_text(corrected_text)
        for amt in more_amounts:
            if amt not in amounts:
                amounts.append(amt)

        # Manual pattern matching for common OCR errors
        patterns = [
            # $1,076 ٠13 or $1,076.13
            r"[\$€£¥]?\s*(\d{1,3}(?:,\d{3})*)\s*[٠٫٬\.]\s*(\d{2})",
            # $1,076 ,.13
            r"[\$€£¥]?\s*(\d{1,3}(?:,\d{3})*)\s*,\s*\.\s*(\d{2})",
        ]
        for pattern in patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if len(match) == 2:
                    amount_str = f"${match[0]}.{match[1]}"
                    if amount_str not in amounts:
                        amounts.append(amount_str)

        return amounts

    def extract_date(self, text: str) -> Optional[str]:
        if not text:
            return None
        date = DateExtractor.extract_date_from_text(text)
        if date:
            return date
        # Fallback: regex for common date formats
        date_patterns = [
            r"\b(\d{4}-\d{2}-\d{2})\b",
            r"\b(\d{2}/\d{2}/\d{4})\b",
            r"\b(\d{2}-\d{2}-\d{4})\b",
            r"\b(\d{1,2}/\d{1,2}/\d{4})\b",
            r"\b(\d{1,2}-\d{1,2}-\d{4})\b",
            r"\b(\d{1,2}/\d{1,2}/\d{2})\b",  # M/D/YY format
            r"\b(\d{2}/\d{2}/\d{2})\b",  # MM/DD/YY format
            # Month name patterns
            r"\b(January|Jan)\s+(\d{1,2}),?\s+(\d{4})\b",
            r"\b(February|Feb)\s+(\d{1,2}),?\s+(\d{4})\b",
            r"\b(March|Mar)\s+(\d{1,2}),?\s+(\d{4})\b",
            r"\b(April|Apr)\s+(\d{1,2}),?\s+(\d{4})\b",
            r"\b(May)\s+(\d{1,2}),?\s+(\d{4})\b",
            r"\b(June|Jun)\s+(\d{1,2}),?\s+(\d{4})\b",
            r"\b(July|Jul)\s+(\d{1,2}),?\s+(\d{4})\b",
            r"\b(August|Aug)\s+(\d{1,2}),?\s+(\d{4})\b",
            r"\b(September|Sep)\s+(\d{1,2}),?\s+(\d{4})\b",
            r"\b(October|Oct)\s+(\d{1,2}),?\s+(\d{4})\b",
            r"\b(November|Nov)\s+(\d{1,2}),?\s+(\d{4})\b",
            r"\b(December|Dec)\s+(\d{1,2}),?\s+(\d{4})\b",
            # Day month year patterns
            r"\b(\d{1,2})\s+(January|Jan)\s+(\d{4})\b",
            r"\b(\d{1,2})\s+(February|Feb)\s+(\d{4})\b",
            r"\b(\d{1,2})\s+(March|Mar)\s+(\d{4})\b",
            r"\b(\d{1,2})\s+(April|Apr)\s+(\d{4})\b",
            r"\b(\d{1,2})\s+(May)\s+(\d{4})\b",
            r"\b(\d{1,2})\s+(June|Jun)\s+(\d{4})\b",
            r"\b(\d{1,2})\s+(July|Jul)\s+(\d{4})\b",
            r"\b(\d{1,2})\s+(August|Aug)\s+(\d{4})\b",
            r"\b(\d{1,2})\s+(September|Sep)\s+(\d{4})\b",
            r"\b(\d{1,2})\s+(October|Oct)\s+(\d{4})\b",
            r"\b(\d{1,2})\s+(November|Nov)\s+(\d{4})\b",
            r"\b(\d{1,2})\s+(December|Dec)\s+(\d{4})\b",
        ]

        month_map = {
            "january": "01",
            "jan": "01",
            "february": "02",
            "feb": "02",
            "march": "03",
            "mar": "03",
            "april": "04",
            "apr": "04",
            "may": "05",
            "june": "06",
            "jun": "06",
            "july": "07",
            "jul": "07",
            "august": "08",
            "aug": "08",
            "september": "09",
            "sep": "09",
            "october": "10",
            "oct": "10",
            "november": "11",
            "nov": "11",
            "december": "12",
            "dec": "12",
        }

        for pattern in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                if len(match.groups()) == 1:
                    # Simple pattern like YYYY-MM-DD or DD/MM/YYYY
                    d = match.group(1)
                    if re.match(r"\d{2}/\d{2}/\d{4}", d):
                        # Convert DD/MM/YYYY to YYYY-MM-DD
                        parts = d.split("/")
                        d = f"{parts[2]}-{parts[1]}-{parts[0]}"
                    elif re.match(r"\d{2}-\d{2}-\d{4}", d):
                        parts = d.split("-")
                        d = f"{parts[2]}-{parts[1]}-{parts[0]}"
                    elif re.match(r"\d{1,2}/\d{1,2}/\d{4}", d):
                        # Convert D/M/YYYY to YYYY-MM-DD
                        parts = d.split("/")
                        d = f"{parts[2]}-{parts[1].zfill(2)}-{parts[0].zfill(2)}"
                    elif re.match(r"\d{1,2}-\d{1,2}-\d{4}", d):
                        parts = d.split("-")
                        d = f"{parts[2]}-{parts[1].zfill(2)}-{parts[0].zfill(2)}"
                    elif re.match(r"\d{1,2}/\d{1,2}/\d{2}", d):
                        # Convert M/D/YY to YYYY-MM-DD
                        parts = d.split("/")
                        year = parts[2]
                        # Convert 2-digit year to 4-digit (assuming 20xx for years 00-29, 19xx for 30-99)
                        if int(year) <= 29:
                            year = "20" + year
                        else:
                            year = "19" + year
                        d = f"{year}-{parts[1].zfill(2)}-{parts[0].zfill(2)}"
                    elif re.match(r"\d{2}/\d{2}/\d{2}", d):
                        # Convert MM/DD/YY to YYYY-MM-DD
                        parts = d.split("/")
                        year = parts[2]
                        # Convert 2-digit year to 4-digit (assuming 20xx for years 00-29, 19xx for 30-99)
                        if int(year) <= 29:
                            year = "20" + year
                        else:
                            year = "19" + year
                        d = f"{year}-{parts[1]}-{parts[0]}"
                    return d
                elif len(match.groups()) == 3:
                    # Month name pattern
                    if match.group(1).lower() in month_map:
                        # Month Day Year pattern
                        month = month_map[match.group(1).lower()]
                        day = match.group(2).zfill(2)
                        year = match.group(3)
                    else:
                        # Day Month Year pattern
                        day = match.group(1).zfill(2)
                        month = month_map[match.group(2).lower()]
                        year = match.group(3)
                    return f"{year}-{month}-{day}"
        return None

    def extract_invoice_number(self, text: str) -> Optional[str]:
        if not text:
            return None
        # Invoice number patterns
        patterns = [
            r"invoice\s*number\s*:\s*([A-Z0-9\-]{4,})",  # Invoice Number: format
            r"invoice\s*#\s*:\s*([A-Z0-9\-]{4,})",  # Invoice #: format
            r"invoice\s*:\s*([A-Z0-9\-]{4,})",  # Invoice: format
            r"inv\s*:\s*([A-Z0-9\-]{4,})",  # INV: format
            r"bill\s*#\s*:\s*([A-Z0-9\-]{4,})",  # Bill #: format
            r"bill\s*#\s*([A-Z0-9\-]{4,})",  # Bill # format
            r"bill\s*#?\s*([A-Z0-9\-]{4,})",  # Fallback bill pattern
            # Invoice ID: format (case insensitive)
            r"invoice\s*id\s*:\s*([A-Z0-9\-]{4,})",
            r"([A-Z]{2,4}-\d{4}-\d{3})",
            r"([A-Z]{2,4}\d{4}\d{3})",
            r"([A-Z]{2,4}-\d{3})",  # BILL-001 format
            r"(\d{4}-\d{3})",  # 2023-001 format
            r"(\d{4,})",  # Allow digit-only numbers if at least 4 digits
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                group = match.group(1)
                # Only return if not just the keyword and looks like a real invoice number
                if group and group.lower() not in ["invoice", "bill", "inv", "number"]:
                    # For digit-only patterns, must be at least 4 digits and not look like a year
                    if re.match(r"^\d+$", group):
                        if len(group) >= 4 and not (
                            len(group) == 4 and group.startswith("20")
                        ):
                            return group
                    # Must contain at least one digit and one letter for other patterns
                    elif re.search(r"[A-Z]", group, re.IGNORECASE) and re.search(
                        r"\d", group
                    ):
                        return group
                    # For patterns with digits and hyphens (like 2023-001), must contain digits
                    elif re.search(r"\d", group) and "-" in group:
                        return group
                    # For alphanumeric patterns without digits (like ABC123)
                    elif re.search(r"[A-Z]", group, re.IGNORECASE) and len(group) >= 4:
                        return group
        return None

    def _validate_invoice_data(self, data: Dict[str, Any]) -> bool:
        """Validate extracted invoice data."""
        if not data:
            return False

        # Check for main fields
        has_company = bool(data.get("company"))
        has_total = (
            isinstance(data.get("total"), (int, float)) and data.get("total", 0) > 0
        )
        has_date = (
            bool(data.get("date"))
            and isinstance(data.get("date"), str)
            and bool(re.match(r"\d{4}-\d{2}-\d{2}", data.get("date", "")))
        )
        has_invoice_number = bool(data.get("invoice_number"))

        # If total is present, it must be positive
        if data.get("total") is not None and not has_total:
            return False

        # If date is present, it must be valid format
        if data.get("date") is not None and not has_date:
            return False

        # Require at least 3 of the 4 main fields to be present and valid
        valid_fields = sum([has_company, has_total, has_date, has_invoice_number])
        return valid_fields >= 3

    def _calculate_confidence(self, data: Dict[str, Any]) -> float:
        """Calculate confidence score for the parsed data."""
        confidence = 0.0

        if data.get("company"):
            confidence += 0.25
        if data.get("total") is not None:
            confidence += 0.25
        if data.get("date"):
            confidence += 0.25
        if data.get("invoice_number"):
            confidence += 0.25

        return confidence
