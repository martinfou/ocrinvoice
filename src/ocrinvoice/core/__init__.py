"""
Core OCR functionality for the Invoice OCR Parser.

This package contains the fundamental OCR and text extraction capabilities
that are used by all parsers in the system.
"""

from .ocr_engine import OCREngine
from .text_extractor import TextExtractor
from .image_processor import ImageProcessor

__all__ = [
    "OCREngine",
    "TextExtractor",
    "ImageProcessor",
]
