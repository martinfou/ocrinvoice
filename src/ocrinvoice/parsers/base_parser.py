"""Base parser class for all document parsers."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Union, Tuple
from pathlib import Path
import logging
import re
from datetime import datetime

from ..core.ocr_engine import OCREngine

try:
    from ..utils.fuzzy_matcher import FuzzyMatcher
    from ..utils.amount_normalizer import AmountNormalizer
    from ..utils.ocr_corrections import OCRCorrections

    UTILS_AVAILABLE = True
except ImportError:
    # Create mock classes for testing
    class FuzzyMatcher:
        def __init__(self, threshold=0.8):
            self.threshold = threshold

    class AmountNormalizer:
        def __init__(self, default_currency="USD"):
            self.default_currency = default_currency

        def extract_amounts_from_text(self, text):
            return []

        def validate_amount(self, amount):
            return True

    class OCRCorrections:
        def correct_text(self, text):
            return text

    UTILS_AVAILABLE = False


class BaseParser(ABC):
    """Abstract base class for all document parsers.

    This class provides common functionality for parsing different types
    of documents (invoices, credit card bills, etc.) using OCR.
    """

    def __init__(self, config: Dict[str, Any]) -> None:
        """Initialize the parser with configuration.

        Args:
            config: Configuration dictionary containing parser settings
        """
        self.config: Dict[str, Any] = config
        self.logger: logging.Logger = logging.getLogger(self.__class__.__name__)

        # Initialize core components
        self.ocr_engine: OCREngine = OCREngine(
            tesseract_path=config.get("tesseract_path"),
            config=config.get("ocr_config", {}),
        )

        # Initialize utility classes
        self.fuzzy_matcher: FuzzyMatcher = FuzzyMatcher(
            config={"threshold": config.get("fuzzy_threshold", 0.8)}
        )
        self.amount_normalizer: AmountNormalizer = AmountNormalizer(
            default_currency=config.get("default_currency", "USD")
        )
        self.ocr_corrections: OCRCorrections = OCRCorrections()

        # Parser configuration
        self.debug: bool = config.get("debug", False)
        self.confidence_threshold: float = config.get("confidence_threshold", 0.7)
        self.max_retries: int = config.get("max_retries", 3)

        # Load company aliases if available
        self.company_aliases: Dict[str, str] = config.get("company_aliases", {})

    @abstractmethod
    def parse(self, pdf_path: Union[str, Path]) -> Dict[str, Any]:
        """Parse document and return structured data.

        Args:
            pdf_path: Path to the PDF file to parse

        Returns:
            Dictionary containing extracted data from the document

        Raises:
            FileNotFoundError: If the PDF file doesn't exist
            ValueError: If the PDF file is invalid or corrupted
        """
        pass

    @abstractmethod
    def extract_company(self, text: str) -> Optional[str]:
        """Extract company name from text.

        Args:
            text: Raw text extracted from the document

        Returns:
            Extracted company name or None if not found
        """
        pass

    @abstractmethod
    def extract_total(self, text: str) -> Optional[str]:
        """Extract total amount from text.

        Args:
            text: Raw text extracted from the document

        Returns:
            Extracted total amount or None if not found
        """
        pass

    @abstractmethod
    def extract_date(self, text: str) -> Optional[str]:
        """Extract date from text.

        Args:
            text: Raw text extracted from the document

        Returns:
            Extracted date in ISO format or None if not found
        """
        pass

    def validate_pdf_path(self, pdf_path: Union[str, Path]) -> Path:
        """Validate that the PDF file exists and is accessible.

        Args:
            pdf_path: Path to the PDF file

        Returns:
            Path object for the validated PDF file

        Raises:
            FileNotFoundError: If the PDF file doesn't exist
            ValueError: If the path is not a file
        """
        path = Path(pdf_path)
        if not path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        if not path.is_file():
            raise ValueError(f"Path is not a file: {pdf_path}")
        if not path.suffix.lower() == ".pdf":
            raise ValueError(f"File is not a PDF: {pdf_path}")
        return path

    def extract_text(self, pdf_path: Union[str, Path]) -> str:
        """Extract text from PDF using OCR engine.

        Args:
            pdf_path: Path to the PDF file

        Returns:
            Extracted text from the PDF

        Raises:
            Exception: If text extraction fails
        """
        path = self.validate_pdf_path(pdf_path)

        for attempt in range(self.max_retries):
            try:
                text = self.ocr_engine.extract_text_from_pdf(str(path))
                if text.strip():
                    return text
                else:
                    self.logger.warning(
                        f"Empty text extracted on attempt {attempt + 1}"
                    )
            except Exception as e:
                self.logger.error(
                    f"Text extraction failed on attempt {attempt + 1}: {e}"
                )
                if attempt == self.max_retries - 1:
                    raise

        return ""

    def preprocess_text(self, text: str) -> str:
        """Preprocess extracted text for better parsing.

        Args:
            text: Raw extracted text

        Returns:
            Preprocessed text
        """
        if not text:
            return ""

        # Apply OCR corrections
        corrected_text = self.ocr_corrections.correct_text(text)

        # Just normalize whitespace - don't remove any characters
        normalized_text = " ".join(corrected_text.split())

        return normalized_text.strip()

    def extract_amount_with_context(
        self, text: str, context_keywords: List[str]
    ) -> Optional[str]:
        """Extract amount with specific context keywords.

        Args:
            text: Text to search in
            context_keywords: Keywords that should be near the amount

        Returns:
            Extracted amount or None if not found
        """
        lines = text.split("\n")

        for line in lines:
            line_lower = line.lower()

            # Check if any context keyword is in the line (exact match)
            if any(keyword.lower() in line_lower for keyword in context_keywords):
                # Extract amounts from this line
                amounts = self.amount_normalizer.extract_amounts_from_text(line)

                if amounts:
                    # Return the first (and usually largest) amount
                    return amounts[0]

        return None

    def extract_date_with_patterns(
        self, text: str, date_patterns: List[str]
    ) -> Optional[str]:
        """Extract date using specific patterns.

        Args:
            text: Text to search in
            date_patterns: List of regex patterns for date matching

        Returns:
            Extracted date in ISO format or None if not found
        """
        for pattern in date_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)

            for match in matches:
                try:
                    # Try to parse the date
                    parsed_date = self._parse_date_string(match)
                    if parsed_date:
                        return parsed_date.isoformat()
                except ValueError:
                    continue

        return None

    def _parse_date_string(self, date_str: str) -> Optional[datetime]:
        """Parse date string into datetime object.

        Args:
            date_str: Date string to parse

        Returns:
            Parsed datetime object or None if parsing fails
        """
        # Common date formats
        formats = [
            "%m/%d/%Y",
            "%m/%d/%y",
            "%m-%d-%Y",
            "%m-%d-%y",
            "%Y/%m/%d",
            "%Y-%m-%d",
            "%B %d, %Y",
            "%B %d %Y",
            "%b %d, %Y",
            "%b %d %Y",
            "%d %B %Y",
            "%d %b %Y",
        ]

        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue

        return None

    def calculate_confidence(self, extracted_data: Dict[str, Any], text: str) -> float:
        """Calculate confidence score for extracted data.

        Args:
            extracted_data: Dictionary of extracted data
            text: Original text used for extraction

        Returns:
            Confidence score between 0.0 and 1.0
        """
        confidence = 0.0
        total_fields = 0

        # Check each field
        for field, value in extracted_data.items():
            if field in ["raw_text", "parsed_at"]:
                continue  # Skip metadata fields

            total_fields += 1

            if value is not None and value != "":
                # Base confidence for having a value
                field_confidence = 0.5

                # Additional confidence based on field type
                if field == "company" and len(str(value)) > 2:
                    field_confidence += 0.3
                elif field == "total" and self.amount_normalizer.validate_amount(
                    str(value)
                ):
                    field_confidence += 0.3
                elif field == "date" and self._parse_date_string(str(value)):
                    field_confidence += 0.3

                confidence += field_confidence

        return confidence / total_fields if total_fields > 0 else 0.0

    def validate_extraction_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and clean extraction result.

        Args:
            result: Raw extraction result

        Returns:
            Validated and cleaned result
        """
        validated = result.copy()

        # Add metadata
        validated["parsed_at"] = datetime.now().isoformat()
        validated["parser_type"] = self.__class__.__name__

        # Calculate confidence
        confidence = self.calculate_confidence(validated, validated.get("raw_text", ""))
        validated["confidence"] = confidence

        # Add validation status
        validated["is_valid"] = confidence >= self.confidence_threshold

        return validated

    def log_parsing_result(
        self, pdf_path: Union[str, Path], result: Dict[str, Any]
    ) -> None:
        """Log the parsing result for debugging.

        Args:
            pdf_path: Path to the parsed PDF file
            result: Parsing result dictionary
        """
        confidence = result.get("confidence", 0.0)
        is_valid = result.get("is_valid", False)

        if is_valid:
            self.logger.info(
                f"Successfully parsed {pdf_path} (confidence: {confidence:.2f})"
            )
        else:
            self.logger.warning(
                f"Low confidence parsing {pdf_path} (confidence: {confidence:.2f})"
            )

        if self.debug:
            self.logger.debug(f"Parsing result: {result}")

    def get_parser_info(self) -> Dict[str, Any]:
        """Get information about the parser.

        Returns:
            Dictionary with parser information
        """
        return {
            "parser_type": self.__class__.__name__,
            "debug_mode": self.debug,
            "confidence_threshold": self.confidence_threshold,
            "max_retries": self.max_retries,
            "company_aliases_count": len(self.company_aliases),
            "ocr_engine_info": self.ocr_engine.get_ocr_info(),
        }

    def test_parser_capabilities(self) -> Dict[str, Any]:
        """Test parser capabilities and return results.

        Returns:
            Dictionary with test results
        """
        results = {
            "parser_available": True,
            "ocr_engine_available": False,
            "dependencies_available": False,
            "errors": [],
        }

        # Test OCR engine
        try:
            ocr_test = self.ocr_engine.test_ocr_capabilities()
            results["ocr_engine_available"] = ocr_test["tesseract_available"]
            results["dependencies_available"] = ocr_test["dependencies_available"]
            results["errors"].extend(ocr_test["errors"])
        except Exception as e:
            results["errors"].append(f"OCR engine test failed: {e}")

        return results
