"""Invoice parser for extracting structured data from invoice PDFs."""

import logging
import re
from pathlib import Path
from typing import Dict, Any, Optional, Union

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

        preprocessed = self.preprocess_text(text)

        company = self.extract_company(preprocessed)
        total = self.extract_total(preprocessed)
        date = self.extract_date(preprocessed)
        invoice_number = self.extract_invoice_number(preprocessed)

        result = {
            "company": company,
            "total": total,
            "date": date,
            "invoice_number": invoice_number,
            "raw_text": text,
            "parser_type": "invoice",
        }

        result["confidence"] = self._calculate_confidence(result)

        self._validate_invoice_data(result)
        self.log_parsing_result(pdf_path, result)

        # Return the data regardless of validation result for now
        # In a real implementation, you might want to handle invalid data differently
        return result

    def extract_company(self, text: str) -> Optional[str]:
        """Extract company name from text using multiple strategies."""
        if not text:
            return None

        lines = [line.strip() for line in text.split("\n")]
        search_lines = lines[:20]
        # Use BusinessAliasManager for company name matching
        if self.business_alias_manager:
            result = self.business_alias_manager.find_business_match(text)
            if result:
                official_name, match_type, confidence = result
                self.logger.debug(
                    f"extract_company: Found company using BusinessAliasManager: "
                    f"'{official_name}' ({match_type}, confidence: {confidence})"
                )
                return official_name.lower()

        # 1. If any known company is present anywhere in the text, return the first one found
        text_lower = text.lower()
        for company in self.config.get(
            "known_companies",
            [
                "ABC Company Inc.",
                "BMR",
                "TD",
                "RBC",
                "SCOTIA",
                "DESJARDINS",
                "HYDRO-QUÉBEC",
                "HYDRO QUEBEC",
                "LA FORFAITERIE",
                "COMPTE DE TAXES SCOLAIRE",
                "CENTRE DE SERVICES SCOLAIRES",
                "GARY CHARTRAND",
            ],
        ):
            if company.lower() in text_lower:
                self.logger.debug(f"extract_company: Found known company: '{company}'")
                return company.lower()
        # 2. After 'INVOICE' or similar, next non-empty, non-excluded line is likely company
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
        for candidate in candidate_lines:
            match, score = fuzzy_matcher.find_best_match(
                candidate, self.config.get("known_companies", [])
            )
            if score > best_score:
                best_score = score
                best_match = match
        if best_match and best_score > 0.8:
            return best_match.lower()
        return None

    def extract_total(self, text: str) -> Optional[float]:
        """Extract invoice total from text using advanced OCR correction and normalization."""
        if not text:
            return None

        lines = [line.strip() for line in text.split("\n")]
        total_amounts = []

        for line in lines:
            line_lower = line.lower()
            # Look for lines that contain "total:" but not "subtotal:"
            # (case-insensitive, allow anywhere in line)
            if "total:" in line_lower and "subtotal:" not in line_lower:
                amounts = self.amount_normalizer.extract_amounts_from_text(line)
                if amounts:
                    total_amounts.extend(amounts)

        # If no total found, look for other total indicators
        if not total_amounts:
            for line in lines:
                line_lower = line.lower()
                if any(
                    keyword in line_lower
                    for keyword in [
                        "amount due:",
                        "grand total:",
                        "final total:",
                        "balance due:",
                    ]
                ):
                    amounts = self.amount_normalizer.extract_amounts_from_text(line)
                    if amounts:
                        total_amounts.extend(amounts)

        # Return the highest amount found
        if total_amounts:
            try:
                float_amounts = []
                for amount_str in total_amounts:
                    cleaned = (
                        amount_str.replace("$", "")
                        .replace("€", "")
                        .replace("£", "")
                        .replace("¥", "")
                    )
                    float_amounts.append(float(cleaned))
                return max(float_amounts)
            except (ValueError, TypeError):
                pass

        # Fallback: try to extract any amount above a reasonable threshold,
        # but ignore line items and years
        float_amounts = []
        for line in lines:
            if any(kw in line.lower() for kw in ["item", "qty", "quantity"]):
                continue
            amounts = self.amount_normalizer.extract_amounts_from_text(line)
            for amount_str in amounts:
                try:
                    cleaned = (
                        amount_str.replace("$", "")
                        .replace("€", "")
                        .replace("£", "")
                        .replace("¥", "")
                    )
                    value = float(cleaned)
                    # Ignore values that look like years (1900-2100)
                    if 1900 <= value <= 2100:
                        continue
                    if value > 10:
                        float_amounts.append(value)
                except (ValueError, TypeError):
                    continue
        if float_amounts:
            return max(float_amounts)
        return None

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
            r"invoice\s*id\s*:\s*([A-Z0-9\-]{4,})",  # Invoice ID: format (case insensitive)
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
