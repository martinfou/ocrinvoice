"""
PDF Metadata Manager for storing and retrieving OCR invoice data.

This module provides functionality to save extracted invoice data back to PDF files
as custom metadata, allowing for faster loading of previously processed invoices.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional, Union

from PyPDF2 import PdfReader, PdfWriter
from PyPDF2.generic import NameObject, createStringObject


class PDFMetadataManager:
    """Manages custom metadata storage and retrieval for PDF files."""

    # Custom metadata key for storing OCR invoice data
    METADATA_KEY = "/OCRInvoiceData"

    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)

    def save_data_to_pdf(
        self, pdf_path: Union[str, Path], data: Dict[str, Any]
    ) -> bool:
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            self.logger.error(f"PDF file not found: {pdf_path}")
            return False
        try:
            with open(pdf_path, "rb") as file:
                reader = PdfReader(file)
                writer = PdfWriter()
                for page in reader.pages:
                    writer.add_page(page)
                # Prepare metadata: ensure all keys are NameObject and values are strings
                metadata = reader.metadata or {}
                new_metadata = {}
                for k, v in metadata.items():
                    if not isinstance(k, str):
                        continue
                    if not k.startswith("/"):
                        k = "/" + k
                    new_metadata[NameObject(k)] = createStringObject(str(v))
                # Add our custom field
                new_metadata[NameObject(self.METADATA_KEY)] = createStringObject(json.dumps(data, ensure_ascii=False))
                writer.add_metadata(new_metadata)
            with open(pdf_path, "wb") as file:
                writer.write(file)
            self.logger.info(f"Successfully saved metadata to {pdf_path}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to save metadata to {pdf_path}: {e}")
            return False

    def load_data_from_pdf(self, pdf_path: Union[str, Path]) -> Optional[Dict[str, Any]]:
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            self.logger.error(f"PDF file not found: {pdf_path}")
            return None
        try:
            with open(pdf_path, "rb") as file:
                reader = PdfReader(file)
                metadata = reader.metadata
                if not metadata or self.METADATA_KEY not in metadata:
                    self.logger.debug(f"No metadata found in {pdf_path}")
                    return None
                data_str = metadata[self.METADATA_KEY]
                data = json.loads(data_str)
                self.logger.info(f"Successfully loaded metadata from {pdf_path}")
                return data
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse metadata JSON from {pdf_path}: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Failed to load metadata from {pdf_path}: {e}")
            return None

    def has_saved_data(self, pdf_path: Union[str, Path]) -> bool:
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            return False
        try:
            with open(pdf_path, "rb") as file:
                reader = PdfReader(file)
                metadata = reader.metadata
                return metadata is not None and self.METADATA_KEY in metadata
        except Exception as e:
            self.logger.debug(f"Error checking metadata in {pdf_path}: {e}")
            return False

    def remove_data_from_pdf(self, pdf_path: Union[str, Path]) -> bool:
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            self.logger.error(f"PDF file not found: {pdf_path}")
            return False
        try:
            with open(pdf_path, "rb") as file:
                reader = PdfReader(file)
                writer = PdfWriter()
                for page in reader.pages:
                    writer.add_page(page)
                metadata = reader.metadata or {}
                new_metadata = {}
                for k, v in metadata.items():
                    if not isinstance(k, str):
                        continue
                    if not k.startswith("/"):
                        k = "/" + k
                    if k == self.METADATA_KEY:
                        continue
                    new_metadata[NameObject(k)] = createStringObject(str(v))
                writer.add_metadata(new_metadata)
            with open(pdf_path, "wb") as file:
                writer.write(file)
            self.logger.info(f"Successfully removed metadata from {pdf_path}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to remove metadata from {pdf_path}: {e}")
            return False 