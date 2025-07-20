"""Base parser class for all document parsers."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Union
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
    def extract_total(self, text: str) -> Optional[float]:
        """Extract total amount from text.

        Args:
            text: Raw text extracted from the document

        Returns:
            Extracted total amount as float or None if not found
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
        force_ocr = self.config.get("force_ocr", False)

        for attempt in range(self.max_retries):
            try:
                text = self.ocr_engine.extract_text_from_pdf(
                    str(path), force_ocr=force_ocr
                )
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

    def calculate_field_confidence(self, field: str, value: Any, text: str) -> float:
        """Calculate confidence score for a specific field.

        Args:
            field: Field name (company, total, date, invoice_number)
            value: Extracted value for the field
            text: Original text used for extraction

        Returns:
            Confidence score between 0.0 and 1.0
        """
        if value is None or value == "":
            return 0.0

        # Base confidence for having a value
        confidence = 0.5

        # Field-specific confidence calculations
        if field == "company":
            if len(str(value)) > 2:
                confidence += 0.3
            # Additional confidence if it matches business aliases
            if hasattr(self, "company_aliases") and str(value).lower() in [
                alias.lower() for alias in self.company_aliases
            ]:
                confidence += 0.2
        elif field == "total":
            if self.amount_normalizer.validate_amount(str(value)):
                confidence += 0.3
            # Additional confidence for reasonable amounts (not too small or too large)
            try:
                amount = float(str(value).replace("$", "").replace(",", ""))
                if 0.01 <= amount <= 1000000:  # Reasonable range for invoice amounts
                    confidence += 0.1
            except (ValueError, TypeError):
                pass
        elif field == "date":
            if self._parse_date_string(str(value)):
                confidence += 0.3
            # Additional confidence for recent dates
            try:
                parsed_date = self._parse_date_string(str(value))
                if parsed_date:
                    from datetime import datetime, timedelta

                    now = datetime.now()
                    if abs((parsed_date - now).days) < 365 * 5:  # Within 5 years
                        confidence += 0.1
            except:
                pass
        elif field == "invoice_number":
            # Confidence based on pattern matching
            if len(str(value)) >= 4:
                confidence += 0.2
            if re.search(r"[A-Z]", str(value), re.IGNORECASE):
                confidence += 0.1
            if re.search(r"\d", str(value)):
                confidence += 0.1

        return min(confidence, 1.0)  # Cap at 1.0

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
            if field in [
                "raw_text",
                "parsed_at",
                "parser_type",
                "confidence",
                "is_valid",
                "extraction_methods",
                "invoice_validation_failed",
            ]:
                continue  # Skip metadata fields

            total_fields += 1

            if value is not None and value != "":
                # Base confidence for having a value
                field_confidence = 0.5

                # Additional confidence based on field type
                if field == "company" and len(str(value)) > 2:
                    field_confidence += 0.3
                if field == "total" and self.amount_normalizer.validate_amount(
                    str(value)
                ):
                    field_confidence += 0.3
                if field == "date" and self._parse_date_string(str(value)):
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
        # Only set parser_type if not already set by the specific parser
        if "parser_type" not in validated:
            validated["parser_type"] = self.__class__.__name__

        # Calculate individual field confidence scores
        text = validated.get("raw_text", "")
        for field in ["company", "total", "date", "invoice_number"]:
            if field in validated:
                field_confidence = self.calculate_field_confidence(
                    field, validated[field], text
                )
                validated[f"{field}_confidence"] = field_confidence

        # Calculate overall confidence
        confidence = self.calculate_confidence(validated, text)
        validated["confidence"] = confidence

        # Add validation status
        validated["is_valid"] = confidence >= self.confidence_threshold

        # Track extraction methods used (if available)
        if "extraction_methods" not in validated:
            validated["extraction_methods"] = {}

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
            # Determine why parsing is considered low confidence
            reasons = []

            # Check if confidence is below threshold
            if confidence < self.confidence_threshold:
                threshold_msg = (
                    f"confidence {confidence:.2f} < threshold "
                    f"{self.confidence_threshold:.2f}"
                )
                reasons.append(threshold_msg)

            # Check for missing required fields
            required_fields = ["company", "total", "date"]
            missing_fields = [
                field for field in required_fields if not result.get(field)
            ]
            if missing_fields:
                reasons.append(f"missing fields: {', '.join(missing_fields)}")

            # Check if any fields are None or empty strings
            empty_fields = [
                field
                for field in required_fields
                if result.get(field) in [None, "", "unknown"]
            ]
            if empty_fields:
                reasons.append(f"empty/invalid fields: {', '.join(empty_fields)}")

            # Check for fallback extraction indicators
            extraction_methods = result.get("extraction_methods", {})
            if extraction_methods:
                fallback_methods = [
                    method
                    for method, used in extraction_methods.items()
                    if used and "fallback" in method.lower()
                ]
                if fallback_methods:
                    fallback_msg = (
                        f"used fallback methods: {', '.join(fallback_methods)}"
                    )
                    reasons.append(fallback_msg)

            # Check for parser-specific validation failures
            if result.get("invoice_validation_failed"):
                reasons.append("invoice-specific validation failed")

            # Check raw text for common fallback indicators
            raw_text = result.get("raw_text", "")
            if raw_text:
                fallback_indicators = []
                if "Selected most frequent total from RAW" in raw_text:
                    fallback_indicators.append("RAW nearby search")
                if "line-based fallback" in raw_text:
                    fallback_indicators.append("line-based fallback")
                if "Proximity search failed" in raw_text:
                    fallback_indicators.append("proximity search failed")
                if fallback_indicators:
                    fallback_text_msg = (
                        f"fallback extraction used: {', '.join(fallback_indicators)}"
                    )
                    reasons.append(fallback_text_msg)

            # If no specific reasons found, provide generic message
            if not reasons:
                reasons.append("unknown validation failure")
                # Add detailed debug info for unknown failures
                if self.debug:
                    self.logger.debug("DEBUG: Unknown validation failure details:")
                    self.logger.debug(f"  - Confidence: {confidence:.2f}")
                    self.logger.debug(f"  - Threshold: {self.confidence_threshold:.2f}")
                    self.logger.debug(f"  - Required fields: {required_fields}")
                    self.logger.debug(f"  - Actual fields: {list(result.keys())}")
                    for field in required_fields:
                        value = result.get(field)
                        self.logger.debug(
                            f"  - {field}: {repr(value)} (type: {type(value).__name__})"
                        )
                    self.logger.debug(f"  - is_valid: {result.get('is_valid')}")
                    self.logger.debug(f"  - parser_type: {result.get('parser_type')}")

            warning_msg = (
                f"Low confidence parsing {pdf_path} "
                f"(confidence: {confidence:.2f}, reasons: {'; '.join(reasons)})"
            )
            self.logger.warning(warning_msg)

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

    def track_extraction_method(
        self, result: Dict[str, Any], field: str, method: str
    ) -> None:
        """Track which extraction method was used for a field.

        Args:
            result: Result dictionary to update
            field: Field name (e.g., 'total', 'company', 'date')
            method: Extraction method used (e.g., 'primary', 'fallback')
        """
        if "extraction_methods" not in result:
            result["extraction_methods"] = {}

        if field not in result["extraction_methods"]:
            result["extraction_methods"][field] = []

        result["extraction_methods"][field].append(method)
