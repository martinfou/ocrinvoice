"""Core OCR engine for text extraction from PDFs and images."""

from typing import Dict, Any, Optional, List, Union
from pathlib import Path
import logging

from PIL import Image

# Conditional imports for optional dependencies
try:
    import pytesseract
    from pdf2image import convert_from_path
    import pdfplumber

    try:
        from pypdf import PdfReader
    except ImportError:
        from PyPDF2 import PdfReader  # Fallback for older installations
    import cv2
    import numpy as np

    DEPENDENCIES_AVAILABLE = True
except ImportError as e:
    DEPENDENCIES_AVAILABLE = False
    logging.warning(
        f"Some OCR dependencies are missing: {e}. OCR functionality will be limited."
    )


class OCREngine:
    """Core OCR functionality with dependency management.

    This class provides the main OCR capabilities for extracting text
    from PDFs and images, with proper dependency validation and error handling.
    """

    def __init__(
        self,
        tesseract_path: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize the OCR engine.

        Args:
            tesseract_path: Path to Tesseract executable (optional)
            config: Configuration dictionary for OCR settings
        """
        self.config: Dict[str, Any] = config or {}
        self.tesseract_path: Optional[str] = tesseract_path
        self.logger: logging.Logger = logging.getLogger(self.__class__.__name__)

        # Validate dependencies
        self._validate_dependencies()

        # Configure Tesseract
        self._configure_tesseract()

        # OCR settings
        self.ocr_language: str = self.config.get("ocr_language", "eng+fra")
        self.ocr_config: str = self.config.get("ocr_config", "--oem 3 --psm 6")
        self.pdf_dpi: int = self.config.get("pdf_dpi", 300)
        self.debug: bool = self.config.get("debug", False)

    def _validate_dependencies(self) -> None:
        """Validate that all required dependencies are available."""
        if not DEPENDENCIES_AVAILABLE:
            raise ImportError(
                "Required OCR dependencies are not available. Please install: "
                "pytesseract, pdf2image, pdfplumber, PyPDF2, pillow, opencv-python, numpy"
            )

    def _configure_tesseract(self) -> None:
        """Configure Tesseract path and test installation."""
        if self.tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = self.tesseract_path
            self.logger.info(f"Tesseract path configured: {self.tesseract_path}")

        # Test Tesseract installation
        try:
            version = pytesseract.get_tesseract_version()
            self.logger.info(f"Tesseract version: {version}")
        except Exception as e:
            self.logger.error(f"Tesseract not found: {e}")
            self.logger.error("Please install Tesseract and ensure it's in your PATH")

    def extract_text_from_pdf(
        self, pdf_path: Union[str, Path], force_ocr: bool = False
    ) -> str:
        """Extract text from PDF using OCR by default with text extraction as fallback.

        Args:
            pdf_path: Path to the PDF file
            force_ocr: If True, skip text extraction and use OCR directly (deprecated, OCR is now default)

        Returns:
            Extracted text from the PDF

        Raises:
            FileNotFoundError: If the PDF file doesn't exist
            Exception: If text extraction fails
        """
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        self.logger.info(f"Extracting text from PDF: {pdf_path}")

        # Always try OCR first for better consistency
        self.logger.info(f"Using OCR for PDF: {pdf_path}")
        ocr_text = self._extract_text_with_ocr(pdf_path)

        # If OCR fails or returns empty text, try text extraction methods as fallback
        if not ocr_text.strip():
            self.logger.warning(
                f"OCR returned empty text, trying text extraction methods: {pdf_path}"
            )

            # Try pdfplumber as fallback
            text = self._extract_text_with_pdfplumber(pdf_path)
            if text.strip():
                return text

            # Try PyPDF2 as final fallback
            text = self._extract_text_with_pypdf2(pdf_path)
            if text.strip():
                return text

        return ocr_text

    def _extract_text_with_pdfplumber(self, pdf_path: Path) -> str:
        """Extract text using pdfplumber.

        Args:
            pdf_path: Path to the PDF file

        Returns:
            Extracted text or empty string if failed
        """
        try:
            with pdfplumber.open(pdf_path) as pdf:
                text = ""
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"

                if text.strip():
                    self.logger.info(
                        f"Successfully extracted text using pdfplumber from {pdf_path}"
                    )
                    return text
        except Exception as e:
            self.logger.debug(f"pdfplumber extraction failed: {e}")

        return ""

    def _extract_text_with_pypdf2(self, pdf_path: Path) -> str:
        """Extract text using PyPDF2.

        Args:
            pdf_path: Path to the PDF file

        Returns:
            Extracted text or empty string if failed
        """
        try:
            with open(pdf_path, "rb") as file:
                reader = PdfReader(file)
                text = ""
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"

                if text.strip():
                    self.logger.info(
                        f"Successfully extracted text using PyPDF2 from {pdf_path}"
                    )
                    return text
        except Exception as e:
            self.logger.debug(f"PyPDF2 extraction failed: {e}")

        return ""

    def _extract_text_with_ocr(self, pdf_path: Path) -> str:
        """Extract text from PDF using OCR.

        Args:
            pdf_path: Path to the PDF file

        Returns:
            Extracted text from OCR
        """
        try:
            # Convert PDF to images
            images = self.convert_pdf_to_images(pdf_path)

            # Extract text from images
            text = self.extract_text_from_images(images)

            self.logger.info(f"Successfully extracted text using OCR from {pdf_path}")
            return text

        except Exception as e:
            self.logger.error(f"OCR extraction failed for {pdf_path}: {e}")
            return ""

    def convert_pdf_to_images(self, pdf_path: Union[str, Path]) -> List[Image.Image]:
        """Convert PDF pages to PIL Images.

        Args:
            pdf_path: Path to the PDF file

        Returns:
            List of PIL Image objects

        Raises:
            Exception: If PDF to image conversion fails
        """
        try:
            images = convert_from_path(pdf_path, dpi=self.pdf_dpi)
            self.logger.info(f"Converted PDF to {len(images)} images: {pdf_path}")
            return images
        except Exception as e:
            self.logger.error(f"Error converting PDF to images {pdf_path}: {e}")
            raise

    def extract_text_from_images(self, images: List[Image.Image]) -> str:
        """Extract text from images using OCR.

        Args:
            images: List of PIL Image objects

        Returns:
            Combined text from all images
        """
        if not images:
            return ""

        all_text = []

        for i, image in enumerate(images):
            try:
                # Preprocess image for better OCR
                processed_image = self.preprocess_image(image)

                # Extract text using Tesseract
                text = pytesseract.image_to_string(
                    processed_image, config=self.ocr_config, lang=self.ocr_language
                )

                if text.strip():
                    all_text.append(text)
                    if self.debug:
                        self.logger.debug(
                            f"Extracted text from image {i}: {text[:100]}..."
                        )

            except Exception as e:
                self.logger.error(f"Error in OCR for image {i}: {e}")
                continue

        # Combine all text
        combined_text = "\n".join(all_text)
        return combined_text

    def extract_text_from_image(self, image: Union[str, Path, Image.Image]) -> str:
        """Extract text from a single image.

        Args:
            image: Path to image file or PIL Image object

        Returns:
            Extracted text from the image
        """
        if isinstance(image, (str, Path)):
            image_path = Path(image)
            if not image_path.exists():
                raise FileNotFoundError(f"Image file not found: {image_path}")

            # Load image
            image = Image.open(image_path)

        # Preprocess image
        processed_image = self.preprocess_image(image)

        # Extract text
        text = pytesseract.image_to_string(
            processed_image, config=self.ocr_config, lang=self.ocr_language
        )

        return text.strip()

    def preprocess_image(self, image: Image.Image) -> Image.Image:
        """Preprocess image for better OCR results.

        Args:
            image: PIL Image to preprocess

        Returns:
            Preprocessed PIL Image
        """
        # Convert to numpy array for OpenCV processing
        img_array = np.array(image)

        # Convert to grayscale if not already
        if len(img_array.shape) == 3:
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        else:
            gray = img_array

        # Apply preprocessing techniques
        # 1. Resize if too small
        height, width = gray.shape
        if width < 800:
            scale_factor = 800 / width
            new_width = int(width * scale_factor)
            new_height = int(height * scale_factor)
            gray = cv2.resize(
                gray, (new_width, new_height), interpolation=cv2.INTER_CUBIC
            )

        # 2. Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (1, 1), 0)

        # 3. Apply thresholding
        _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # 4. Apply morphological operations to clean up
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
        cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

        # Convert back to PIL Image
        processed_image = Image.fromarray(cleaned)

        return processed_image

    def get_ocr_info(self) -> Dict[str, Any]:
        """Get information about OCR capabilities and configuration.

        Returns:
            Dictionary with OCR information
        """
        try:
            version = pytesseract.get_tesseract_version()
            languages = pytesseract.get_languages()
        except Exception:
            version = "Unknown"
            languages = []

        return {
            "tesseract_version": version,
            "tesseract_path": self.tesseract_path,
            "available_languages": languages,
            "ocr_language": self.ocr_language,
            "ocr_config": self.ocr_config,
            "pdf_dpi": self.pdf_dpi,
            "dependencies_available": DEPENDENCIES_AVAILABLE,
            "debug_mode": self.debug,
        }

    def test_ocr_capabilities(self) -> Dict[str, Any]:
        """Test OCR capabilities and return results.

        Returns:
            Dictionary with test results
        """
        results = {
            "tesseract_available": False,
            "dependencies_available": DEPENDENCIES_AVAILABLE,
            "errors": [],
        }

        # Test Tesseract
        try:
            version = pytesseract.get_tesseract_version()
            results["tesseract_available"] = True
            results["tesseract_version"] = version
        except Exception as e:
            results["errors"].append(f"Tesseract not available: {e}")

        # Test dependencies
        missing_deps = []
        for dep in [
            "pytesseract",
            "pdf2image",
            "pdfplumber",
            "PyPDF2",
            "PIL",
            "cv2",
            "numpy",
        ]:
            try:
                __import__(dep)
            except ImportError:
                missing_deps.append(dep)

        if missing_deps:
            results["errors"].append(f"Missing dependencies: {missing_deps}")

        return results
