"""OCR correction utilities for improving text accuracy."""

from typing import Dict, Any, Optional, List
import re
import logging

logger = logging.getLogger(__name__)


class OCRCorrections:
    """Utility for correcting common OCR errors in text.

    This class provides methods to correct common OCR errors
    such as character misrecognitions and formatting issues.
    """

    def __init__(self) -> None:
        """Initialize the OCR corrections utility."""
        # Common OCR character corrections
        self.character_corrections: Dict[str, str] = {
            "O": "0",  # Letter O to zero
            "l": "1",  # Lowercase L to one
            "I": "1",  # Capital I to one
            "S": "5",  # Letter S to five
            # "G": "6",  # Letter G to six - REMOVED: too aggressive, corrupts company names
            "B": "8",  # Letter B to eight
            "g": "9",  # Lowercase G to nine
            "rn": "m",  # rn to m
            "cl": "d",  # cl to d
            "vv": "w",  # vv to w
        }

        # Common company name corrections
        self.company_corrections: Dict[str, str] = {
            "Mlcrosoft": "Microsoft",
            "App1e": "Apple",
            "Goog1e": "Google",
            "Amaz0n": "Amazon",
            "Netf1ix": "Netflix",
            "Faceb00k": "Facebook",
            "Tw1tter": "Twitter",
            "1nstagram": "Instagram",
            "L1nked1n": "LinkedIn",
            "Y0utube": "YouTube",
        }

    def correct_text(self, text: str) -> str:
        """Apply general OCR corrections to text.

        Args:
            text: Text to correct

        Returns:
            Corrected text
        """
        corrected = text

        # Apply character corrections
        for incorrect, correct in self.character_corrections.items():
            corrected = corrected.replace(incorrect, correct)

        # Fix common spacing issues
        corrected = re.sub(r"\s+", " ", corrected)  # Multiple spaces to single
        corrected = re.sub(
            r"(\d)\s*([A-Za-z])", r"\1 \2", corrected
        )  # Add space between number and letter
        corrected = re.sub(
            r"([A-Za-z])\s*(\d)", r"\1 \2", corrected
        )  # Add space between letter and number

        return corrected.strip()

    def correct_company_name(self, company_name: str) -> str:
        """Correct common OCR errors in company names.

        Args:
            company_name: Company name to correct

        Returns:
            Corrected company name
        """
        corrected = company_name

        # Apply company-specific corrections
        for incorrect, correct in self.company_corrections.items():
            if incorrect.lower() in corrected.lower():
                corrected = corrected.replace(incorrect, correct)
                corrected = corrected.replace(incorrect.lower(), correct)
                corrected = corrected.replace(incorrect.title(), correct)

        # Apply general character corrections
        corrected = self.correct_text(corrected)

        return corrected

    def correct_amount(self, amount_str: str) -> str:
        """Correct common OCR errors in monetary amounts.

        Args:
            amount_str: Amount string to correct

        Returns:
            Corrected amount string
        """
        corrected = amount_str

        # Apply character corrections for numbers
        for incorrect, correct in self.character_corrections.items():
            corrected = corrected.replace(incorrect, correct)

        # Fix common amount formatting issues
        corrected = re.sub(
            r"(\d)\s*([.,])\s*(\d)", r"\1\2\3", corrected
        )  # Remove spaces around decimal
        corrected = re.sub(
            r"([.,])\s*(\d{2})\s*$", r"\1\2", corrected
        )  # Fix cents formatting

        return corrected

    def correct_date(self, date_str: str) -> str:
        """Correct common OCR errors in date strings.

        Args:
            date_str: Date string to correct

        Returns:
            Corrected date string
        """
        corrected = date_str

        # Apply character corrections
        for incorrect, correct in self.character_corrections.items():
            corrected = corrected.replace(incorrect, correct)

        # Fix common date formatting issues
        corrected = re.sub(
            r"(\d)\s*[/-]\s*(\d)\s*[/-]\s*(\d)", r"\1/\2/\3", corrected
        )  # Standardize separators
        corrected = re.sub(
            r"(\d{1,2})\s*[/-]\s*(\d{1,2})\s*[/-]\s*(\d{2,4})", r"\1/\2/\3", corrected
        )

        return corrected

    def correct_invoice_number(self, invoice_number: str) -> str:
        """Correct common OCR errors in invoice numbers.

        Args:
            invoice_number: Invoice number to correct

        Returns:
            Corrected invoice number
        """
        corrected = invoice_number

        # Apply character corrections
        for incorrect, correct in self.character_corrections.items():
            corrected = corrected.replace(incorrect, correct)

        # Remove common OCR artifacts
        corrected = re.sub(
            r"[^\w\-]", "", corrected
        )  # Keep only alphanumeric and hyphens

        return corrected

    def get_correction_stats(self) -> Dict[str, Any]:
        """Get statistics about available corrections.

        Returns:
            Dictionary with correction statistics
        """
        return {
            "character_corrections": len(self.character_corrections),
            "company_corrections": len(self.company_corrections),
            "total_corrections": len(self.character_corrections)
            + len(self.company_corrections),
        }
