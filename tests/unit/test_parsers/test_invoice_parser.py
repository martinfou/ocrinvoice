# flake8: noqa
"""Unit tests for the InvoiceParser class."""

import sys
import os

sys.path.insert(
    0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "src")
)  # noqa: E402
from pathlib import Path
import pytest
from unittest.mock import patch, MagicMock
from typing import Dict, Any

from ocrinvoice.parsers.invoice_parser import InvoiceParser


class TestInvoiceParserInitialization:
    """Test InvoiceParser initialization methods."""

    def test_init_with_default_config(self) -> None:
        """Test initialization with default configuration."""
        parser = InvoiceParser()

        assert parser.parser_type == "invoice"
        assert parser.debug is False
        assert parser.company_keywords == ["company", "inc", "ltd", "corp"]
        assert parser.total_keywords == ["TOTAL", "AMOUNT DUE"]
        assert parser.date_keywords == ["DATE", "INVOICE DATE"]

    def test_init_with_custom_config(self) -> None:
        """Test initialization with custom configuration."""
        config = {
            "debug": True,
            "company_keywords": ["FROM:", "BILLER:"],
            "total_keywords": ["FINAL AMOUNT:", "DUE:"],
            "date_keywords": ["DATE", "INVOICE DATE"],
        }

        parser = InvoiceParser(config)

        assert parser.debug is True
        assert parser.company_keywords == ["FROM:", "BILLER:"]
        assert parser.total_keywords == ["FINAL AMOUNT:", "DUE:"]
        assert parser.date_keywords == ["DATE", "INVOICE DATE"]

    def test_init_inherits_from_base_parser(self) -> None:
        """Test that InvoiceParser inherits from BaseParser."""
        parser = InvoiceParser()

        # Check that base parser attributes are available
        assert hasattr(parser, "config")
        assert hasattr(parser, "logger")
        assert hasattr(parser, "ocr_engine")


class TestInvoiceParserCompanyExtraction:
    """Test InvoiceParser company extraction methods."""

    @pytest.fixture  # type: ignore
    def parser(self) -> InvoiceParser:
        """Create an InvoiceParser instance for testing."""
        return InvoiceParser()

    @patch("ocrinvoice.business.business_mapping_manager.FuzzyMatcher")
    def test_extract_company_known_company(
        self, mock_fuzzy_matcher: MagicMock, parser: InvoiceParser
    ) -> None:
        """Test company extraction with known company."""
        # Mock the fuzzy matcher to return None (no fuzzy match)
        mock_fuzzy_matcher.fuzzy_match.return_value = None

        text = """
        INVOICE

        HYDRO-QUÉBEC
        123 Business Street
        City, State 12345

        Total: $100.00
        """

        result = parser.extract_company(text)

        assert result == "hydro-québec"

    @patch("ocrinvoice.business.business_mapping_manager.FuzzyMatcher")
    def test_extract_company_after_invoice_header(
        self, mock_fuzzy_matcher: MagicMock, parser: InvoiceParser
    ) -> None:
        """Test company extraction after INVOICE header."""
        # Mock the fuzzy matcher to return None (no fuzzy match)
        mock_fuzzy_matcher.fuzzy_match.return_value = None

        # Clear known companies to test the header-based extraction
        parser.config = {"known_companies": []}

        text = """
        INVOICE

        Acme Corporation Ltd.
        123 Business Street
        City, State 12345

        Bill To:
        Customer Name
        """

        result = parser.extract_company(text)

        assert result == "acme corporation ltd."

    @patch("ocrinvoice.business.business_mapping_manager.FuzzyMatcher")
    def test_extract_company_with_keyword_colon(
        self, mock_fuzzy_matcher: MagicMock, parser: InvoiceParser
    ) -> None:
        """Test company extraction with keyword: format."""
        # Mock the fuzzy matcher to return None (no fuzzy match)
        mock_fuzzy_matcher.fuzzy_match.return_value = None

        # Clear known companies to test keyword-based extraction
        parser.config = {"known_companies": []}
        parser.company_keywords = ["FROM:", "BILLER:"]

        text = """
        FROM: XYZ Corporation
        TO: Customer Name

        Total: $100.00
        """

        result = parser.extract_company(text)

        assert result == "xyz corporation"

    @patch("ocrinvoice.business.business_mapping_manager.FuzzyMatcher")
    def test_extract_company_no_match(
        self, mock_fuzzy_matcher: MagicMock, parser: InvoiceParser
    ) -> None:
        """Test company extraction when no company is found."""
        # Mock the fuzzy matcher to return None (no fuzzy match)
        mock_fuzzy_matcher.fuzzy_match.return_value = None

        # Clear known companies to test no-match scenario
        parser.config = {"known_companies": []}

        text = """
        Customer Invoice

        Total: $100.00
        Date: 2023-01-15
        """

        result = parser.extract_company(text)

        assert result is None

    @patch("ocrinvoice.business.business_mapping_manager.FuzzyMatcher")
    def test_extract_company_ignores_dates(
        self, mock_fuzzy_matcher: MagicMock, parser: InvoiceParser
    ) -> None:
        """Test company extraction ignores date lines."""
        # Mock the fuzzy matcher to return None (no fuzzy match)
        mock_fuzzy_matcher.fuzzy_match.return_value = None

        # Clear known companies to test date filtering
        parser.config = {"known_companies": []}

        text = """
        INVOICE

        2024-01-15
        Date: 2024-01-15

        Acme Corporation Ltd.

        Total: $100.00
        """

        result = parser.extract_company(text)

        assert result == "acme corporation ltd."


class TestInvoiceParserTotalExtraction:
    """Test InvoiceParser total amount extraction methods."""

    @pytest.fixture  # type: ignore
    def parser(self) -> InvoiceParser:
        """Create an InvoiceParser instance for testing."""
        return InvoiceParser()

    def test_extract_total_success(self, parser: InvoiceParser) -> None:
        """Test successful total extraction."""
        text = """
        INVOICE

        Item 1: $50.00
        Item 2: $75.00

        Subtotal: $125.00
        Tax: $12.50
        Total: $137.50
        """

        result = parser.extract_total(text)

        assert result == 137.50

    def test_extract_total_with_different_formats(self, parser: InvoiceParser) -> None:
        """Test total extraction with different amount formats."""
        test_cases = [
            ("Total: $1,234.56", 1234.56),
            ("Amount Due: 2,500.00", 2500.00),
            ("TOTAL: €1,000.00", 1000.00),
            ("Grand Total: 500", 500.00),
            ("Final Total: $99.99", 99.99),
        ]

        for text, expected in test_cases:
            result = parser.extract_total(text)
            assert result == expected

    def test_extract_total_with_keywords(self, parser: InvoiceParser) -> None:
        """Test total extraction with custom keywords."""
        parser.total_keywords = ["FINAL AMOUNT:", "DUE:"]

        text = """
        Invoice Details

        Final Amount: $250.00
        Due: $250.00
        """

        result = parser.extract_total(text)

        assert result == 250.00

    def test_extract_total_no_match(self, parser: InvoiceParser) -> None:
        """Test total extraction when no total is found."""
        text = """
        Invoice

        Item 1: $50.00
        Item 2: $75.00
        """

        result = parser.extract_total(text)

        assert result is None

    def test_extract_total_ignores_subtotal(self, parser: InvoiceParser) -> None:
        """Test total extraction ignores subtotal."""
        text = """
        INVOICE

        Subtotal: $100.00
        Tax: $10.00
        Total: $110.00
        """

        result = parser.extract_total(text)

        assert result == 110.00

    def test_extract_total_ignores_line_items(self, parser: InvoiceParser) -> None:
        """Test total extraction ignores line items."""
        text = """
        INVOICE

        Item 1: $50.00
        Item 2: $75.00
        Qty: 2

        Total: $125.00
        """

        result = parser.extract_total(text)

        assert result == 125.00

    def test_extract_total_ignores_years(self, parser: InvoiceParser) -> None:
        """Test total extraction ignores years that look like amounts."""
        text = """
        INVOICE

        Date: 2024-01-15
        Year: 2024

        Total: $125.00
        """

        result = parser.extract_total(text)

        assert result == 125.00

    def test_extract_total_with_currency_symbols(self, parser: InvoiceParser) -> None:
        """Test total extraction with various currency symbols."""
        test_cases = [
            ("Total: $100.00", 100.00),
            ("Total: €100.00", 100.00),
            ("Total: £100.00", 100.00),
            ("Total: ¥100.00", 100.00),
            ("Total: 100.00", 100.00),
        ]

        for text, expected in test_cases:
            result = parser.extract_total(text)
            assert result == expected

    def test_extract_total_with_commas(self, parser: InvoiceParser) -> None:
        """Test total extraction with comma-separated numbers."""
        text = """
        INVOICE

        Total: $1,234.56
        """

        result = parser.extract_total(text)

        assert result == 1234.56

    def test_extract_total_multiple_amounts(self, parser: InvoiceParser) -> None:
        """Test total extraction when multiple amounts are present."""
        text = """
        INVOICE

        Item 1: $50.00
        Item 2: $75.00
        Subtotal: $125.00
        Tax: $12.50
        Total: $137.50
        """

        result = parser.extract_total(text)

        assert result == 137.50

    def test_extract_total_with_minimum_threshold(self, parser: InvoiceParser) -> None:
        """Test total extraction with minimum amount threshold."""
        text = """
        INVOICE

        Item 1: $5.00
        Item 2: $3.00
        Total: $8.00
        """

        result = parser.extract_total(text)

        assert result == 8.00


class TestInvoiceParserDateExtraction:
    """Test InvoiceParser date extraction methods."""

    @pytest.fixture  # type: ignore
    def parser(self) -> InvoiceParser:
        """Create an InvoiceParser instance for testing."""
        return InvoiceParser()

    def test_extract_date_success(self, parser: InvoiceParser) -> None:
        """Test successful date extraction."""
        text = """
        INVOICE

        Date: 2024-01-15
        Due Date: 2024-02-15

        Total: $100.00
        """

        result = parser.extract_date(text)

        assert result == "2024-01-15"

    def test_extract_date_with_different_formats(self, parser: InvoiceParser) -> None:
        """Test date extraction with different date formats."""
        test_cases = [
            ("Date: 2024-01-15", "2024-01-15"),
            ("Invoice Date: 15/01/2024", "2024-01-15"),
            ("Date: 01-15-2024", "2024-01-15"),
            ("Date: January 15, 2024", "2024-01-15"),
            ("Date: Jan 15, 2024", "2024-01-15"),
        ]

        for text, expected in test_cases:
            result = parser.extract_date(text)
            assert result == expected

    def test_extract_date_with_keywords(self, parser: InvoiceParser) -> None:
        """Test date extraction with custom keywords."""
        parser.date_keywords = ["INVOICE DATE:", "ISSUED:"]

        text = """
        Invoice Details

        Invoice Date: 2024-01-15
        Issued: 2024-01-15
        """

        result = parser.extract_date(text)

        assert result == "2024-01-15"

    def test_extract_date_no_match(self, parser: InvoiceParser) -> None:
        """Test date extraction when no date is found."""
        text = """
        Invoice

        Total: $100.00
        """

        result = parser.extract_date(text)

        assert result is None

    def test_extract_date_multiple_matches(self, parser: InvoiceParser) -> None:
        """Test date extraction when multiple dates are present."""
        text = """
        INVOICE

        Date: 2024-01-15
        Due Date: 2024-02-15
        Issue Date: 2024-01-10

        Total: $100.00
        """

        result = parser.extract_date(text)

        # Should return the first date found
        assert result == "2024-01-15"

    def test_extract_date_invalid_format(self, parser: InvoiceParser) -> None:
        """Test date extraction with invalid date format."""
        text = """
        INVOICE

        Date: Invalid Date
        Total: $100.00
        """

        result = parser.extract_date(text)

        assert result is None


class TestInvoiceParserInvoiceNumberExtraction:
    """Test InvoiceParser invoice number extraction methods."""

    @pytest.fixture  # type: ignore
    def parser(self) -> InvoiceParser:
        """Create an InvoiceParser instance for testing."""
        return InvoiceParser()

    def test_extract_invoice_number_success(self, parser: InvoiceParser) -> None:
        """Test successful invoice number extraction."""
        text = """
        INVOICE

        Invoice #: INV-2024-001
        Date: 2024-01-15

        Total: $100.00
        """

        result = parser.extract_invoice_number(text)

        assert result == "INV-2024-001"

    def test_extract_invoice_number_with_different_formats(
        self, parser: InvoiceParser
    ) -> None:
        """Test invoice number extraction with different formats."""
        test_cases = [
            ("Invoice #: INV-2024-001", "INV-2024-001"),
            ("Invoice Number: 2024-001", "2024-001"),
            ("INV: ABC123", "ABC123"),
            ("Bill #: BILL-001", "BILL-001"),
            ("Invoice: 12345", "12345"),
        ]

        for text, expected in test_cases:
            result = parser.extract_invoice_number(text)
            assert result == expected

    def test_extract_invoice_number_no_match(self, parser: InvoiceParser) -> None:
        """Test invoice number extraction when no number is found."""
        text = """
        Invoice

        Date: 2024-01-15
        Total: $100.00
        """

        result = parser.extract_invoice_number(text)

        assert result is None

    def test_extract_invoice_number_ignores_years(self, parser: InvoiceParser) -> None:
        """Test invoice number extraction ignores years."""
        text = """
        INVOICE

        Date: 2024-01-15
        Year: 2024
        Invoice #: INV-2024-001

        Total: $100.00
        """

        result = parser.extract_invoice_number(text)

        assert result == "INV-2024-001"

    def test_extract_invoice_number_requires_minimum_length(
        self, parser: InvoiceParser
    ) -> None:
        """Test invoice number extraction requires minimum length."""
        text = """
        INVOICE

        Invoice #: 12
        Total: $100.00
        """

        result = parser.extract_invoice_number(text)

        # Should not return very short numbers
        assert result is None


class TestInvoiceParserFullParsing:
    """Test InvoiceParser full parsing methods."""

    @pytest.fixture  # type: ignore
    def parser(self) -> InvoiceParser:
        """Create an InvoiceParser instance for testing."""
        return InvoiceParser()

    def test_parse_with_no_data(self, parser: InvoiceParser, tmp_path: Path) -> None:
        """Test parsing with no data."""
        # Create an empty PDF file
        pdf_path = tmp_path / "empty.pdf"
        pdf_path.write_text("")

        result = parser.parse(pdf_path)

        assert result["company"] is None
        assert result["total"] is None
        assert result["date"] is None
        assert result["invoice_number"] is None
        assert result["parser_type"] == "invoice"
        assert "confidence" in result

    def test_parse_with_error_handling(
        self, parser: InvoiceParser, tmp_path: Path
    ) -> None:
        """Test parsing with error handling."""
        # Create a non-existent PDF file
        pdf_path = tmp_path / "nonexistent.pdf"

        with pytest.raises(FileNotFoundError):
            parser.parse(pdf_path)


class TestInvoiceParserValidation:
    """Test InvoiceParser validation methods."""

    @pytest.fixture  # type: ignore
    def parser(self) -> InvoiceParser:
        """Create an InvoiceParser instance for testing."""
        return InvoiceParser()

    def test_validate_invoice_data_success(self, parser: InvoiceParser) -> None:
        """Test successful invoice data validation."""
        data = {
            "company": "Test Company",
            "total": 100.00,
            "date": "2024-01-15",
            "invoice_number": "INV-001",
        }

        result = parser._validate_invoice_data(data)

        assert result is True

    def test_validate_invoice_data_missing_required(
        self, parser: InvoiceParser
    ) -> None:
        """Test invoice data validation with missing required fields."""
        data = {
            "company": "Test Company",
            "total": 100.00,
            # Missing date and invoice_number
        }

        result = parser._validate_invoice_data(data)

        assert result is False

    def test_validate_invoice_data_invalid_total(self, parser: InvoiceParser) -> None:
        """Test invoice data validation with invalid total."""
        data = {
            "company": "Test Company",
            "total": -100.00,  # Negative total
            "date": "2024-01-15",
            "invoice_number": "INV-001",
        }

        result = parser._validate_invoice_data(data)

        assert result is False

    def test_validate_invoice_data_invalid_date(self, parser: InvoiceParser) -> None:
        """Test invoice data validation with invalid date."""
        data = {
            "company": "Test Company",
            "total": 100.00,
            "date": "invalid-date",  # Invalid date format
            "invoice_number": "INV-001",
        }

        result = parser._validate_invoice_data(data)

        assert result is False


class TestInvoiceParserErrorHandling:
    """Test InvoiceParser error handling methods."""

    @pytest.fixture  # type: ignore
    def parser(self) -> InvoiceParser:
        """Create an InvoiceParser instance for testing."""
        return InvoiceParser()

    def test_handle_extraction_error_with_retry(
        self, parser: InvoiceParser, tmp_path: Path
    ) -> None:
        """Test error handling with retry mechanism."""
        # Create a PDF file that will cause extraction errors
        pdf_path = tmp_path / "error.pdf"
        pdf_path.write_text("Invalid PDF content")

        # Should handle the error gracefully
        result = parser.parse(pdf_path, max_retries=1)

        assert isinstance(result, dict)
        assert "confidence" in result

    def test_handle_extraction_error_max_retries_exceeded(
        self, parser: InvoiceParser, tmp_path: Path
    ) -> None:
        """Test error handling when max retries are exceeded."""
        # Create a PDF file that will cause extraction errors
        pdf_path = tmp_path / "error.pdf"
        pdf_path.write_text("Invalid PDF content")

        # Should handle the error gracefully and return a result
        result = parser.parse(pdf_path, max_retries=0)

        assert isinstance(result, dict)
        assert "confidence" in result
        assert result["confidence"] <= 0.3  # Low confidence due to extraction failure


class TestInvoiceParserPerformance:
    """Test InvoiceParser performance methods."""

    @pytest.fixture  # type: ignore
    def parser(self) -> InvoiceParser:
        """Create an InvoiceParser instance for testing."""
        return InvoiceParser()

    def test_large_invoice_processing(
        self, parser: InvoiceParser, tmp_path: Path
    ) -> None:
        """Test processing of large invoice files."""
        # Create a large text file
        large_text = "INVOICE\n" * 1000 + "Total: $100.00\n"
        pdf_path = tmp_path / "large.pdf"
        pdf_path.write_text(large_text)

        # Should process without errors
        result = parser.parse(pdf_path)

        assert isinstance(result, dict)
        assert "confidence" in result

    def test_multiple_concurrent_parsing(
        self, parser: InvoiceParser, tmp_path: Path
    ) -> None:
        """Test multiple concurrent parsing operations."""
        import threading
        import time

        results = []
        errors = []

        def parsing_worker() -> None:
            try:
                # Create a simple PDF file
                pdf_path = tmp_path / f"test_{threading.current_thread().ident}.pdf"
                pdf_path.write_text("INVOICE\nTotal: $100.00\n")

                result = parser.parse(pdf_path)
                results.append(result)
            except Exception as e:
                errors.append(e)

        # Create multiple threads
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=parsing_worker)
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Should have processed all files
        assert len(results) == 5
        assert len(errors) == 0


class TestInvoiceParserIntegration:
    """Test InvoiceParser integration methods."""

    @pytest.fixture  # type: ignore
    def parser(self) -> InvoiceParser:
        """Create an InvoiceParser instance for testing."""
        return InvoiceParser()

    @patch.object(InvoiceParser, "extract_text")
    @patch.object(InvoiceParser, "preprocess_text")
    @patch("ocrinvoice.business.business_mapping_manager.BusinessMappingManager")
    def test_parsing_with_text_preprocessing(
        self,
        mock_business_mapping_manager: MagicMock,
        mock_preprocess_text: MagicMock,
        mock_extract_text: MagicMock,
        parser: InvoiceParser,
        tmp_path: Path,
    ) -> None:
        """Test parsing with text preprocessing."""
        # Mock the business mapping manager to return None (no match)
        mock_bmm_instance = MagicMock()
        mock_bmm_instance.find_business_match.return_value = None
        mock_business_mapping_manager.return_value = mock_bmm_instance

        # Mock the preprocessing to return text unchanged
        mock_preprocess_text.side_effect = lambda text: text

        # Mock the text extraction to return our test text with a known company
        test_text = """
        INVOICE

        HYDRO-QUÉBEC
        Business Street
        City, State

        Date: 2024-01-15
        Invoice #: ABC123

        Total: $100.00
        """
        mock_extract_text.return_value = test_text

        # Create a dummy PDF file
        pdf_path = tmp_path / "test.pdf"
        pdf_path.write_text("dummy content")

        result = parser.parse(pdf_path)

        assert result["company"] == "hydro-québec"
        assert result["total"] == 100.00
        assert result["date"] == "2024-01-15"
        assert result["invoice_number"] == "ABC123"
        assert result["parser_type"] == "invoice"
        assert "confidence" in result
