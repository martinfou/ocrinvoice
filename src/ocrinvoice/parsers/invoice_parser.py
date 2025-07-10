"""Invoice OCR Parser for extracting data from invoice PDFs."""

from typing import Any, Dict, Optional, Union
from pathlib import Path
import logging
from .base_parser import BaseParser
from ..core.ocr_engine import OCREngine
from ..utils.fuzzy_matcher import FuzzyMatcher
from ..utils.amount_normalizer import AmountNormalizer
from ..utils.ocr_corrections import OCRCorrections
from ..parsers.date_extractor import DateExtractor
import re


class InvoiceParser(BaseParser):
    """Parser for extracting invoice data from PDFs using OCR."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the invoice parser.

        Args:
            config: Configuration dictionary for parser settings
        """
        config = config or {}
        super().__init__(config)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.debug = config.get("debug", False)
        self.company_aliases = config.get("company_aliases", {})

        # Add missing attributes that tests expect
        self.company_keywords = config.get("company_keywords", ["INVOICE", "BILL"])
        self.amount_keywords = config.get("amount_keywords", ["TOTAL", "AMOUNT", "DUE"])
        self.date_keywords = config.get("date_keywords", ["DATE", "ISSUED", "DUE"])
        self.total_keywords = config.get("total_keywords", ["TOTAL", "AMOUNT DUE"])
        self.parser_type = "invoice"

    def parse(self, pdf_path: Union[str, Path], max_retries: int = 3) -> Dict[str, Any]:
        """Parse the invoice PDF and return structured data."""
        text = self.extract_text(pdf_path)
        preprocessed = self.preprocess_text(text)

        company = self.extract_company(preprocessed)
        total = self.extract_total(preprocessed)
        date = self.extract_date(preprocessed)

        result = {"company": company, "total": total, "date": date, "raw_text": text}
        validated = self._validate_invoice_data(result)
        self.log_parsing_result(pdf_path, validated)
        return validated

    def extract_company(self, text: str) -> Optional[str]:
        """Extract company name from text using multiple strategies."""
        if not text:
            return None
        lines = text.split("\n")
        search_lines = lines[:20]
        candidates = []
        known_companies = self.config.get(
            "known_companies",
            [
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
        )
        exclude_indicators = [
            "TOTAL",
            "AMOUNT",
            "DUE",
            "BALANCE",
            "GRAND TOTAL",
            "FINAL TOTAL",
            "INVOICE",
            "BILL",
            "RECEIPT",
            "DATE",
            "TIME",
            "PHONE",
            "FAX",
            "EMAIL",
            "WEB",
            "WWW",
            "HTTP",
            "HTTPS",
            "COM",
            "ORG",
            "NET",
            "ADDRESS",
            "STREET",
            "AVENUE",
            "BOULEVARD",
            "ROAD",
            "DRIVE",
            "CITY",
            "STATE",
            "PROVINCE",
            "POSTAL",
            "ZIP",
            "CODE",
            "ACCOUNT",
            "REFERENCE",
            "REF",
            "INVOICE #",
            "BILL #",
            "QUANTITY",
            "QTY",
            "DESCRIPTION",
            "DESC",
            "UNIT",
            "PRICE",
            "SUBTOTAL",
            "TAX",
            "SHIPPING",
            "HANDLING",
            "DISCOUNT",
            "PAYMENT",
            "TERMS",
            "DUE DATE",
            "BALANCE DUE",
        ]
        # First pass: exact match
        for company in known_companies:
            if company.lower() in text.lower():
                candidates.append((company, 15))
                break
        # Special pass: strict fuzzy/alias
        if not candidates and self.company_aliases:
            for line in search_lines:
                line_clean = line.strip()
                if len(line_clean) > 5:
                    for alias, real_name in self.company_aliases.items():
                        if alias.lower() in line_clean.lower():
                            candidates.append((real_name, 12))
                            break
        # Second pass: company-like lines
        if not candidates:
            for line in search_lines:
                line = line.strip()
                if len(line) < 5 or len(line) > 60:
                    continue
                if any(ind in line.upper() for ind in exclude_indicators):
                    continue
                if (
                    line
                    and line[0].isalpha()
                    and sum(c.isdigit() for c in line) < len(line) * 0.1
                ):
                    candidates.append((line, 5))
        # Third pass: company keywords
        if not candidates:
            company_keywords = [
                "SERVICES",
                "CENTRE",
                "CLINIQUE",
                "RESTAURANT",
                "STORE",
                "MAGASIN",
                "CONSTRUCTION",
            ]
            for line in search_lines:
                line = line.strip()
                if any(keyword in line.upper() for keyword in company_keywords):
                    if 5 < len(line) < 50:
                        candidates.append((line, 3))
        if candidates:
            candidates.sort(key=lambda x: (x[1], -len(x[0])), reverse=True)
            return candidates[0][0]
        return None

    def extract_total(self, text: str) -> Optional[str]:
        """Extract invoice total from text using advanced OCR correction and normalization."""
        if not text:
            return None
        # Use the amount normalizer utility for robust extraction
        context_keywords = [
            "total",
            "amount",
            "grand total",
            "final total",
            "balance due",
            "montant",
            "somme",
        ]
        total = self.extract_amount_with_context(text, context_keywords)
        if total:
            return total
        # Fallback: try to extract any amount
        amounts = self.amount_normalizer.extract_amounts_from_text(text)
        if amounts:
            return amounts[0]
        return None

    def extract_date(self, text: str) -> Optional[str]:
        """Extract date from text using DateExtractor utility."""
        if not text:
            return None
        # Use DateExtractor for robust date extraction
        date = DateExtractor.extract_date_from_text(text)
        if date:
            return date
        # Fallback: use base parser's pattern-based extraction
        patterns = [r"\d{1,2}/\d{1,2}/\d{2,4}", r"\d{4}-\d{2}-\d{2}"]
        return self.extract_date_with_patterns(text, patterns)

    def extract_invoice_number(self, text: str) -> Optional[str]:
        """Extract invoice number from text.

        Args:
            text: Raw text extracted from the document

        Returns:
            Extracted invoice number or None if not found
        """
        if not text:
            return None

        # Common invoice number patterns
        patterns = [
            r"INVOICE\s*#?\s*(\d+)",
            r"BILL\s*#?\s*(\d+)",
            r"INV\s*#?\s*(\d+)",
            r"INVOICE\s*NUMBER\s*:?\s*(\d+)",
            r"REF\s*#?\s*(\d+)",
            r"REFERENCE\s*:?\s*(\d+)",
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)

        return None

    def _validate_invoice_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate extracted invoice data.

        Args:
            data: Dictionary containing extracted invoice data

        Returns:
            Validated data with any corrections applied
        """
        validated = data.copy()

        # Validate company name
        if not validated.get("company"):
            validated["company"] = None

        # Validate total amount
        total = validated.get("total")
        if total:
            # Convert string amounts to numeric if needed
            if isinstance(total, str):
                # Remove currency symbols and convert to float
                total_clean = re.sub(r"[^\d.]", "", total)
                try:
                    validated["total"] = float(total_clean)
                except ValueError:
                    validated["total"] = None
            elif isinstance(total, (int, float)):
                validated["total"] = float(total)
        else:
            validated["total"] = None

        # Validate date
        date = validated.get("date")
        if date:
            # Ensure date is in ISO format
            try:
                if isinstance(date, str):
                    # Try to parse and format date
                    from datetime import datetime

                    parsed_date = datetime.strptime(date, "%Y-%m-%d")
                    validated["date"] = parsed_date.strftime("%Y-%m-%d")
            except ValueError:
                validated["date"] = None
        else:
            validated["date"] = None

        return validated
