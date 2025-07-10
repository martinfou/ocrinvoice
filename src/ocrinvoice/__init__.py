"""
Invoice OCR Parser - Extract structured data from PDF invoices using OCR.

A comprehensive tool for parsing invoices, credit card bills, and other financial documents
using optical character recognition (OCR) technology.
"""

__version__ = "1.0.0"
__author__ = "Invoice OCR Parser Team"
__email__ = "support@ocrinvoice.com"

# Import main classes for easy access
from .core.ocr_engine import OCREngine
from .parsers.invoice_parser import InvoiceParser
from .parsers.credit_card_parser import CreditCardBillParser
from .parsers.date_extractor import DateExtractor

__all__ = [
    "OCREngine",
    "InvoiceParser",
    "CreditCardBillParser",
    "DateExtractor",
]
