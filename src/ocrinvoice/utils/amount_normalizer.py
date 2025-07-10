"""Amount normalization utilities for OCR text processing."""

from typing import Optional, Union, Dict, Any, List
import re
from decimal import Decimal, InvalidOperation


class AmountNormalizer:
    """Utility for normalizing monetary amounts from OCR text.

    This class provides methods to clean and standardize monetary amounts
    extracted from OCR text, handling various formats and common OCR errors.
    """

    def __init__(self, default_currency: str = "USD") -> None:
        """Initialize the amount normalizer.

        Args:
            default_currency: Default currency code to use when not specified
        """
        self.default_currency: str = default_currency

        # Common OCR errors for numbers
        self.ocr_corrections: Dict[str, str] = {
            "O": "0",  # Letter O to zero
            "l": "1",  # Lowercase L to one
            "I": "1",  # Capital I to one
            "S": "5",  # Letter S to five
            "G": "6",  # Letter G to six
            "B": "8",  # Letter B to eight
            "g": "9",  # Lowercase G to nine
        }

    def normalize_amount(self, amount_str: str) -> Optional[str]:
        """Normalize a monetary amount string.

        Args:
            amount_str: Raw amount string from OCR

        Returns:
            Normalized amount string or None if invalid
        """
        if not amount_str or not isinstance(amount_str, str):
            return None

        # Clean the input
        cleaned = self._clean_amount_string(amount_str)

        # Apply OCR corrections
        corrected = self._apply_ocr_corrections(cleaned)

        # Extract the numeric value
        numeric_value = self._extract_numeric_value(corrected)

        if numeric_value is None:
            return None

        # Format the result
        return self._format_amount(numeric_value)

    def _clean_amount_string(self, amount_str: str) -> str:
        """Clean and prepare amount string for processing.

        Args:
            amount_str: Raw amount string

        Returns:
            Cleaned amount string
        """
        # Remove extra whitespace
        cleaned = " ".join(amount_str.split())

        # Remove common non-numeric characters except decimal point and comma
        cleaned = re.sub(r"[^\d.,\-$€£¥%]", "", cleaned)

        # Handle negative amounts
        if cleaned.startswith("-"):
            cleaned = cleaned[1:]  # Remove leading minus
            is_negative = True
        else:
            is_negative = False

        # Remove currency symbols for processing
        cleaned = re.sub(r"[\$€£¥]", "", cleaned)

        # Remove percentage signs
        cleaned = re.sub(r"%", "", cleaned)

        # Add back negative sign if needed
        if is_negative:
            cleaned = "-" + cleaned

        return cleaned.strip()

    def _apply_ocr_corrections(self, amount_str: str) -> str:
        """Apply common OCR corrections to amount string.

        Args:
            amount_str: Amount string to correct

        Returns:
            Corrected amount string
        """
        corrected = amount_str

        # Apply character corrections
        for incorrect, correct in self.ocr_corrections.items():
            corrected = corrected.replace(incorrect, correct)

        return corrected

    def _extract_numeric_value(self, amount_str: str) -> Optional[Decimal]:
        """Extract numeric value from amount string.

        Args:
            amount_str: Cleaned amount string

        Returns:
            Decimal value or None if invalid
        """
        try:
            # Handle different decimal separators
            if "," in amount_str and "." in amount_str:
                # Format like "1,234.56" - remove commas
                amount_str = amount_str.replace(",", "")
            elif "," in amount_str and "." not in amount_str:
                # Format like "1234,56" - replace comma with dot
                amount_str = amount_str.replace(",", ".")

            # Convert to Decimal
            return Decimal(amount_str)
        except (InvalidOperation, ValueError):
            return None

    def _format_amount(self, value: Decimal) -> str:
        """Format amount value as string.

        Args:
            value: Decimal amount value

        Returns:
            Formatted amount string
        """
        # Format with 2 decimal places
        formatted = f"{value:.2f}"

        # Add currency symbol if needed
        if self.default_currency == "USD":
            return f"${formatted}"
        elif self.default_currency == "EUR":
            return f"€{formatted}"
        elif self.default_currency == "GBP":
            return f"£{formatted}"
        else:
            return formatted

    def parse_amount_range(
        self, amount_str: str
    ) -> Optional[Dict[str, Union[str, float]]]:
        """Parse amount range (e.g., "100-200" or "100 to 200").

        Args:
            amount_str: Amount range string

        Returns:
            Dictionary with min and max values or None if invalid
        """
        # Look for range patterns
        range_patterns = [
            r"([\d,]+\.?\d*)\s*[-–—]\s*([\d,]+\.?\d*)",  # 100-200
            r"([\d,]+\.?\d*)\s+to\s+([\d,]+\.?\d*)",  # 100 to 200
            r"([\d,]+\.?\d*)\s*-\s*([\d,]+\.?\d*)",  # 100 - 200
        ]

        for pattern in range_patterns:
            match = re.search(pattern, amount_str, re.IGNORECASE)
            if match:
                min_str = match.group(1)
                max_str = match.group(2)

                min_amount = self.normalize_amount(min_str)
                max_amount = self.normalize_amount(max_str)

                if min_amount and max_amount:
                    return {"min": min_amount, "max": max_amount, "type": "range"}

        return None

    def extract_amounts_from_text(self, text: str) -> List[str]:
        """Extract all monetary amounts from text.

        Args:
            text: Text to extract amounts from

        Returns:
            List of normalized amount strings
        """
        # Amount patterns
        amount_patterns = [
            r"[\$€£¥]?\s*\d{1,3}(?:,\d{3})*(?:\.\d{2})?",  # $1,234.56
            r"[\$€£¥]?\s*\d+\.\d{2}",  # $123.45
            r"[\$€£¥]?\s*\d+",  # $123
            r"\d{1,3}(?:,\d{3})*(?:\.\d{2})?\s*[\$€£¥]",  # 1,234.56$
            r"\d+\.\d{2}\s*[\$€£¥]",  # 123.45$
        ]

        amounts = []
        for pattern in amount_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                normalized = self.normalize_amount(match)
                if normalized:
                    amounts.append(normalized)

        return amounts

    def validate_amount(self, amount_str: str) -> bool:
        """Validate if a string represents a valid monetary amount.

        Args:
            amount_str: Amount string to validate

        Returns:
            True if valid amount, False otherwise
        """
        normalized = self.normalize_amount(amount_str)
        return normalized is not None

    def compare_amounts(
        self, amount1: str, amount2: str, tolerance: float = 0.01
    ) -> bool:
        """Compare two amounts with tolerance.

        Args:
            amount1: First amount string
            amount2: Second amount string
            tolerance: Tolerance for comparison (default 0.01 = 1 cent)

        Returns:
            True if amounts are within tolerance, False otherwise
        """
        try:
            val1 = self._extract_numeric_value(self._clean_amount_string(amount1))
            val2 = self._extract_numeric_value(self._clean_amount_string(amount2))

            if val1 is None or val2 is None:
                return False

            return abs(val1 - val2) <= Decimal(str(tolerance))
        except Exception:
            return False

    def get_currency_symbol(self, currency_code: str) -> str:
        """Get currency symbol for currency code.

        Args:
            currency_code: Three-letter currency code

        Returns:
            Currency symbol
        """
        currency_symbols = {
            "USD": "$",
            "EUR": "€",
            "GBP": "£",
            "JPY": "¥",
            "CAD": "C$",
            "AUD": "A$",
        }

        return currency_symbols.get(currency_code.upper(), "")

    def convert_currency_format(
        self, amount_str: str, from_currency: str, to_currency: str
    ) -> Optional[str]:
        """Convert amount between different currency formats.

        Args:
            amount_str: Amount string to convert
            from_currency: Source currency code
            to_currency: Target currency code

        Returns:
            Converted amount string or None if conversion fails
        """
        # Extract numeric value
        numeric_value = self._extract_numeric_value(
            self._clean_amount_string(amount_str)
        )

        if numeric_value is None:
            return None

        # For now, just change the currency symbol
        # In a real implementation, you would use exchange rates
        from_symbol = self.get_currency_symbol(from_currency)
        to_symbol = self.get_currency_symbol(to_currency)

        # Remove old symbol and add new one
        cleaned = amount_str.replace(from_symbol, "").strip()
        return f"{to_symbol}{cleaned}"
