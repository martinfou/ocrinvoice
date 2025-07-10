"""
Credit Card Bill Parser implementation.

This module contains the CreditCardBillParser class for extracting
structured data from credit card bill PDFs.
"""

from typing import Any, Dict, Optional, Union
from pathlib import Path
import logging
from .base_parser import BaseParser
from ..core.ocr_engine import OCREngine
from ..utils.fuzzy_matcher import FuzzyMatcher
from ..utils.amount_normalizer import AmountNormalizer
from ..utils.ocr_corrections import OCRCorrections
from ..parsers.date_extractor import DateExtractor


class CreditCardBillParser(BaseParser):
    """Parser for extracting credit card bill data from PDFs using OCR."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.debug = config.get("debug", False)
        self.company_aliases = config.get("company_aliases", {})

    def parse(self, pdf_path: Union[str, Path]) -> Dict[str, Any]:
        """Parse the credit card bill PDF and return structured data."""
        text = self.extract_text(pdf_path)
        preprocessed = self.preprocess_text(text)

        company = self.extract_company(preprocessed)
        total = self.extract_total(preprocessed)
        date = self.extract_date(preprocessed)

        result = {"company": company, "total": total, "date": date, "raw_text": text}
        validated = self.validate_extraction_result(result)
        self.log_parsing_result(pdf_path, validated)
        return validated

    def extract_company(self, text: str) -> Optional[str]:
        """Extract company name from text using multiple strategies."""
        # For credit card bills, company is often the bank or issuer
        known_companies = self.config.get(
            "known_companies",
            [
                "VISA",
                "MASTERCARD",
                "AMEX",
                "AMERICAN EXPRESS",
                "TD",
                "RBC",
                "SCOTIA",
                "DESJARDINS",
                "NATIONAL BANK",
                "BMO",
                "CIBC",
            ],
        )
        if not text:
            return None
        lines = text.split("\n")
        search_lines = lines[:20]
        candidates = []
        for company in known_companies:
            if company.lower() in text.lower():
                candidates.append((company, 15))
                break
        if not candidates and self.company_aliases:
            for line in search_lines:
                line_clean = line.strip()
                if len(line_clean) > 5:
                    for alias, real_name in self.company_aliases.items():
                        if alias.lower() in line_clean.lower():
                            candidates.append((real_name, 12))
                            break
        if not candidates:
            for line in search_lines:
                line = line.strip()
                if len(line) < 5 or len(line) > 60:
                    continue
                if (
                    line
                    and line[0].isalpha()
                    and sum(c.isdigit() for c in line) < len(line) * 0.1
                ):
                    candidates.append((line, 5))
        if candidates:
            candidates.sort(key=lambda x: (x[1], -len(x[0])), reverse=True)
            return candidates[0][0]
        return None

    def extract_total(self, text: str) -> Optional[str]:
        """Extract credit card bill total using advanced OCR correction and normalization."""
        if not text:
            return None
        # Use the amount normalizer utility for robust extraction
        context_keywords = [
            "total",
            "amount",
            "grand total",
            "final total",
            "balance due",
            "nouveau solde",
            "solde nouveau",
            "payment due",
            "amount due",
            "balance",
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
        date = DateExtractor.extract_date_from_text(text)
        if date:
            return date
        patterns = [r"\d{1,2}/\d{1,2}/\d{2,4}", r"\d{4}-\d{2}-\d{2}"]
        return self.extract_date_with_patterns(text, patterns)
