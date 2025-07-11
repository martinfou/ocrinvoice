"""PDF text extraction utilities."""

from typing import Dict, Any, Optional, List, Union
from pathlib import Path
import logging
import re
import importlib.util

# Conditional imports for optional dependencies
try:
    import pdfplumber
    from PyPDF2 import PdfReader
    from pdf2image import convert_from_path
    from PIL import Image

    DEPENDENCIES_AVAILABLE = True
except ImportError as e:
    DEPENDENCIES_AVAILABLE = False
    logging.warning(
        f"Some PDF processing dependencies are missing: {e}. "
        "PDF text extraction will be limited."
    )


class TextExtractor:
    """Utility for extracting text from PDFs using multiple methods.

    This class provides specialized text extraction capabilities
    that can be used independently of OCR when text is already
    present in the PDF.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize the text extractor.

        Args:
            config: Configuration dictionary for text extraction settings
        """
        self.config: Dict[str, Any] = config or {}
        self.logger: logging.Logger = logging.getLogger(self.__class__.__name__)

        # Validate dependencies
        self._validate_dependencies()

        # Configuration
        self.extraction_methods: List[str] = self.config.get(
            "extraction_methods", ["pdfplumber", "pypdf2", "fallback"]
        )
        self.debug: bool = self.config.get("debug", False)
        self.min_text_length: int = self.config.get("min_text_length", 10)

        # Validate configuration
        self._validate_extraction_methods()

    def _validate_dependencies(self) -> None:
        """Validate that required dependencies are available."""
        if not DEPENDENCIES_AVAILABLE:
            raise ImportError(
                "Required PDF processing dependencies are not available. "
                "Please install: pdfplumber, PyPDF2, pdf2image, pillow"
            )

    def _validate_extraction_methods(self) -> None:
        """Validate extraction methods configuration."""
        valid_methods = ["pdfplumber", "pypdf2", "fallback"]

        for method in self.extraction_methods:
            if method not in valid_methods:
                raise ValueError(
                    f"Invalid extraction method: {method}. Valid methods are: {valid_methods}"
                )

    def extract_text(self, pdf_path: Union[str, Path], max_retries: int = 3) -> str:
        """Extract text from PDF using configured methods, with retry logic."""
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        # Validate file type
        if pdf_path.suffix.lower() != ".pdf":
            raise ValueError(f"File is not a PDF: {pdf_path}")

        self.logger.info(f"Extracting text from PDF: {pdf_path}")

        # Try each extraction method in order, with retries
        for method in self.extraction_methods:
            for attempt in range(max_retries):
                try:
                    if method == "pdfplumber":
                        text = self._extract_with_pdfplumber(pdf_path)
                    elif method == "pypdf2":
                        text = self._extract_with_pypdf2(pdf_path)
                    elif method == "fallback":
                        text = self._extract_with_fallback(pdf_path)
                    else:
                        self.logger.warning(f"Unknown extraction method: {method}")
                        break

                    if text.strip():
                        cleaned_text = self._clean_text(text)
                        if self._is_text_sufficient(cleaned_text):
                            self.logger.info(
                                f"Successfully extracted text using {method} from {pdf_path} (attempt {attempt+1})"
                            )
                            return cleaned_text
                except Exception as e:
                    self.logger.debug(
                        f"{method} extraction failed on attempt {attempt+1}: {e}"
                    )
                    continue
                # If text was empty or insufficient, try again (up to max_retries)
            # After all retries for this method, move to next method

        # If no method worked, return empty string
        self.logger.warning(f"No text could be extracted from {pdf_path}")
        return ""

    def _extract_with_pdfplumber(self, pdf_path: Path) -> str:
        """Extract text using pdfplumber.

        Args:
            pdf_path: Path to the PDF file

        Returns:
            Extracted text or empty string if failed
        """
        # Convert Path to string for pdfplumber
        pdf_path_str = str(pdf_path)
        with pdfplumber.open(pdf_path_str) as pdf:
            text = ""
            for page_num, page in enumerate(pdf.pages):
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"

                if self.debug:
                    self.logger.debug(
                        f"Page {page_num + 1}: {len(page_text)} characters"
                    )

            return text.strip()

    def _extract_with_pypdf2(self, pdf_path: Path) -> str:
        """Extract text using PyPDF2.

        Args:
            pdf_path: Path to the PDF file

        Returns:
            Extracted text or empty string if failed
        """
        # Convert Path to string for PyPDF2
        pdf_path_str = str(pdf_path)
        with open(pdf_path_str, "rb") as file:
            reader = PdfReader(file)
            text = ""

            for page_num, page in enumerate(reader.pages):
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"

                if self.debug:
                    self.logger.debug(
                        f"Page {page_num + 1}: {len(page_text)} characters"
                    )

            return text.strip()

    def _extract_with_fallback(self, pdf_path: Path) -> str:
        """Fallback text extraction method.

        Args:
            pdf_path: Path to the PDF file

        Returns:
            Extracted text or empty string if failed
        """
        # Try to convert PDF to images and extract text
        images = convert_from_path(pdf_path)
        text = ""

        for i, image in enumerate(images):
            # This would require OCR, but for now just return empty
            # In a real implementation, you'd use OCR here
            if self.debug:
                self.logger.debug(f"Fallback method processed page {i + 1}")

        return text.strip()

    def _clean_text(self, text: str) -> str:
        """Clean and normalize extracted text.

        Args:
            text: Raw extracted text

        Returns:
            Cleaned text
        """
        if not text:
            return ""

        # Remove extra whitespace but preserve meaningful characters
        cleaned = " ".join(text.split())

        # Remove only problematic OCR artifacts, preserve useful characters
        cleaned = re.sub(r"[^\w\s.,$€£¥%\-/#:!?@&*()]", "", cleaned)

        return cleaned.strip()

    def _is_text_sufficient(self, text: str) -> bool:
        """Check if extracted text is sufficient for processing.

        Args:
            text: Text to check

        Returns:
            True if text is sufficient, False otherwise
        """
        if not text:
            return False

        # Check minimum length
        if len(text.strip()) < self.min_text_length:
            return False

        # Check if text contains meaningful content (not just numbers/symbols)
        words = text.split()
        if len(words) < 3:
            return False

        return True

    def extract_text_by_page(self, pdf_path: Union[str, Path]) -> List[str]:
        """Extract text from each page separately.

        Args:
            pdf_path: Path to the PDF file

        Returns:
            List of text from each page

        Raises:
            FileNotFoundError: If the PDF file doesn't exist
        """
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        pages_text = []

        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    page_text = page.extract_text() or ""
                    pages_text.append(page_text)

                    if self.debug:
                        self.logger.debug(
                            f"Page {page_num + 1}: {len(page_text)} characters"
                        )

        except Exception as e:
            self.logger.error(f"Error extracting text by page from {pdf_path}: {e}")

        return pages_text

    def extract_text_with_metadata(self, pdf_path: Union[str, Path]) -> Dict[str, Any]:
        """Extract text along with metadata about the extraction.

        Args:
            pdf_path: Path to the PDF file

        Returns:
            Dictionary containing text and metadata

        Raises:
            FileNotFoundError: If the PDF file doesn't exist
        """
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        result = {
            "text": "",
            "pages": 0,
            "characters": 0,
            "method_used": None,
            "success": False,
            "errors": [],
        }

        # Try each extraction method
        for method in self.extraction_methods:
            try:
                if method == "pdfplumber":
                    text = self._extract_with_pdfplumber(pdf_path)
                elif method == "pypdf2":
                    text = self._extract_with_pypdf2(pdf_path)
                else:
                    continue

                if text.strip():
                    result["text"] = text
                    result["method_used"] = method
                    result["success"] = True
                    result["characters"] = len(text)

                    # Get page count
                    try:
                        with pdfplumber.open(pdf_path) as pdf:
                            result["pages"] = len(pdf.pages)
                    except:
                        result["pages"] = 0

                    break

            except Exception as e:
                result["errors"].append(f"{method}: {str(e)}")

        return result

    def is_text_based_pdf(self, pdf_path: Union[str, Path]) -> bool:
        """Check if PDF contains extractable text.

        Args:
            pdf_path: Path to the PDF file

        Returns:
            True if PDF contains text, False if it's image-based

        Raises:
            FileNotFoundError: If the PDF file doesn't exist
        """
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        try:
            # Try to extract text
            text = self.extract_text(pdf_path)

            # If we get substantial text, it's text-based
            if len(text.strip()) > 50:  # Threshold for meaningful text
                return True

            return False

        except Exception as e:
            self.logger.debug(f"Error checking if PDF is text-based: {e}")
            return False

    def get_pdf_info(self, pdf_path: Union[str, Path]) -> Dict[str, Any]:
        """Get information about the PDF file.

        Args:
            pdf_path: Path to the PDF file

        Returns:
            Dictionary with PDF information

        Raises:
            FileNotFoundError: If the PDF file doesn't exist
        """
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        info = {
            "file_size": pdf_path.stat().st_size,
            "pages": 0,
            "is_text_based": False,
            "extractable_text_length": 0,
            "errors": [],
        }

        try:
            with pdfplumber.open(pdf_path) as pdf:
                info["pages"] = len(pdf.pages)

                # Try to extract text
                text = self.extract_text(pdf_path)
                info["extractable_text_length"] = len(text)
                info["is_text_based"] = len(text.strip()) > 50

        except Exception as e:
            info["errors"].append(str(e))

        return info
