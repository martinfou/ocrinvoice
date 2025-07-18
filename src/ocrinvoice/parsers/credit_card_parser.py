"""Credit card bill parser for extracting structured data from credit card PDFs."""

import logging
from pathlib import Path
from typing import Dict, Any, Optional, Union

from .base_parser import BaseParser
from .date_extractor import DateExtractor
from ..business.business_mapping_manager import BusinessMappingManager


class CreditCardBillParser(BaseParser):
    """Parser for extracting credit card bill data from PDFs using OCR."""

    def __init__(self, config: Dict[str, Any]):
        # Ensure config is never None
        config = config or {}
        super().__init__(config)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.debug = config.get("debug", False)
        self.company_aliases = config.get("company_aliases", {})

        # Initialize business mapping manager for company name matching
        try:
            self.business_mapping_manager = BusinessMappingManager()
        except Exception as e:
            self.logger.warning(f"Could not initialize BusinessMappingManager: {e}")
            self.business_mapping_manager = None

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
        # Use BusinessMappingManager for company name matching
        if self.business_mapping_manager:
            result = self.business_mapping_manager.find_business_match(text)
            if result:
                official_name, match_type, confidence = result
                self.logger.debug(
                    f"extract_company: Found company using BusinessMappingManager: "
                    f"'{official_name}' ({match_type}, confidence: {confidence})"
                )
                return official_name.lower()

        # For credit card bills, company is often the bank or issuer
        # Note: All business names should be configured in business_aliases.json
        # This fallback is only used if BusinessMappingManager is not available
        known_companies = self.config.get("known_companies", [])
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
                digit_count = sum(c.isdigit() for c in line)
                if line and line[0].isalpha() and digit_count < len(line) * 0.1:
                    candidates.append((line, 5))
        if candidates:
            candidates.sort(key=lambda x: (x[1], -len(x[0])), reverse=True)
            return candidates[0][0]
        return None

    def extract_total(self, text: str) -> Optional[float]:
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
            try:
                return float(total)
            except (ValueError, TypeError):
                pass
        # Fallback: try to extract any amount
        amounts = self.amount_normalizer.extract_amounts_from_text(text)
        if amounts:
            try:
                return float(amounts[0])
            except (ValueError, TypeError):
                pass
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
