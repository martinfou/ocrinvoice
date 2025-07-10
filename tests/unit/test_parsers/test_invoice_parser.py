"""Unit tests for the InvoiceParser class."""

import pytest
from unittest.mock import Mock, patch, MagicMock, call
from pathlib import Path
from typing import Dict, Any
import tempfile
import os

import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "src"))

from ocrinvoice.parsers.invoice_parser import InvoiceParser


class TestInvoiceParserInitialization:
    """Test InvoiceParser initialization and configuration."""

    def test_init_with_default_config(self):
        """Test initialization with default configuration."""
        parser = InvoiceParser()

        assert parser.config == {}
        assert parser.debug is False
        assert parser.confidence_threshold == 0.7
        assert parser.max_retries == 3
        assert parser.parser_type == "invoice"

    def test_init_with_custom_config(self):
        """Test initialization with custom configuration."""
        config = {
            "debug": True,
            "confidence_threshold": 0.8,
            "max_retries": 5,
            "company_keywords": ["INVOICE", "BILL"],
            "total_keywords": ["TOTAL", "AMOUNT DUE"],
            "date_keywords": ["DATE", "INVOICE DATE"],
        }

        parser = InvoiceParser(config)

        assert parser.config == config
        assert parser.debug is True
        assert parser.confidence_threshold == 0.8
        assert parser.max_retries == 5
        assert parser.company_keywords == ["INVOICE", "BILL"]
        assert parser.total_keywords == ["TOTAL", "AMOUNT DUE"]
        assert parser.date_keywords == ["DATE", "INVOICE DATE"]

    def test_init_inherits_from_base_parser(self):
        """Test that InvoiceParser inherits from BaseParser."""
        parser = InvoiceParser()

        # Check that it has BaseParser methods
        assert hasattr(parser, "extract_text")
        assert hasattr(parser, "preprocess_text")
        assert hasattr(parser, "validate_pdf_path")
        assert hasattr(parser, "parse")


class TestInvoiceParserCompanyExtraction:
    """Test InvoiceParser company extraction methods."""

    @pytest.fixture
    def parser(self):
        """Create an InvoiceParser instance for testing."""
        return InvoiceParser()

    def test_extract_company_success(self, parser):
        """Test successful company extraction."""
        text = """
        INVOICE

        ABC Company Inc.
        123 Business Street
        City, State 12345

        Bill To:
        Customer Name
        """

        result = parser.extract_company(text)

        assert result == "ABC Company Inc."

    def test_extract_company_with_keywords(self, parser):
        """Test company extraction with keyword matching."""
        parser.company_keywords = ["FROM:", "BILLER:"]

        text = """
        FROM: XYZ Corporation
        TO: Customer Name

        Total: $100.00
        """

        result = parser.extract_company(text)

        assert result == "XYZ Corporation"

    def test_extract_company_no_match(self, parser):
        """Test company extraction when no company is found."""
        text = """
        Customer Invoice

        Total: $100.00
        Date: 2023-01-15
        """

        result = parser.extract_company(text)

        assert result is None

    def test_extract_company_multiple_matches(self, parser):
        """Test company extraction with multiple potential matches."""
        text = """
        INVOICE

        ABC Company Inc.

        Bill To:
        XYZ Corporation

        Total: $100.00
        """

        result = parser.extract_company(text)

        # Should return the first company found (usually the billing company)
        assert result == "ABC Company Inc."

    def test_extract_company_with_fuzzy_matching(self, parser):
        """Test company extraction with fuzzy matching."""
        text = """
        INVOICE

        ABC Compny Inc.  # Typo in company name

        Total: $100.00
        """

        # Mock fuzzy matcher to return a match
        with patch.object(parser.fuzzy_matcher, "find_best_match") as mock_fuzzy:
            mock_fuzzy.return_value = ("ABC Company Inc.", 0.85)

            result = parser.extract_company(text)

            assert result == "ABC Company Inc."
            mock_fuzzy.assert_called_once()


class TestInvoiceParserTotalExtraction:
    """Test InvoiceParser total amount extraction methods."""

    @pytest.fixture
    def parser(self):
        """Create an InvoiceParser instance for testing."""
        return InvoiceParser()

    def test_extract_total_success(self, parser):
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

    def test_extract_total_with_different_formats(self, parser):
        """Test total extraction with different amount formats."""
        test_cases = [
            ("Total: $1,234.56", 1234.56),
            ("Amount Due: 2,500.00", 2500.00),
            ("TOTAL: €1,000.00", 1000.00),
            ("Grand Total: 500", 500.00),
            ("Final Amount: $99.99", 99.99),
        ]

        for text, expected in test_cases:
            result = parser.extract_total(text)
            assert result == expected

    def test_extract_total_with_keywords(self, parser):
        """Test total extraction with custom keywords."""
        parser.total_keywords = ["FINAL AMOUNT:", "DUE:"]

        text = """
        Invoice Details

        Final Amount: $250.00
        Due: $250.00
        """

        result = parser.extract_total(text)

        assert result == 250.00

    def test_extract_total_no_match(self, parser):
        """Test total extraction when no total is found."""
        text = """
        Invoice

        Item 1: $50.00
        Item 2: $75.00
        """

        result = parser.extract_total(text)

        assert result is None

    def test_extract_total_multiple_matches(self, parser):
        """Test total extraction with multiple amount matches."""
        text = """
        INVOICE

        Subtotal: $100.00
        Tax: $10.00
        Total: $110.00
        Amount Due: $110.00
        """

        result = parser.extract_total(text)

        # Should return the highest amount (usually the final total)
        assert result == 110.00

    def test_extract_total_with_currency_symbols(self, parser):
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


class TestInvoiceParserDateExtraction:
    """Test InvoiceParser date extraction methods."""

    @pytest.fixture
    def parser(self):
        """Create an InvoiceParser instance for testing."""
        return InvoiceParser()

    def test_extract_date_success(self, parser):
        """Test successful date extraction."""
        text = """
        INVOICE

        Date: 2023-01-15
        Due Date: 2023-02-15

        Total: $100.00
        """

        result = parser.extract_date(text)

        assert result == "2023-01-15"

    def test_extract_date_with_different_formats(self, parser):
        """Test date extraction with different date formats."""
        test_cases = [
            ("Date: 01/15/2023", "2023-01-15"),
            ("Date: 15-01-2023", "2023-01-15"),
            ("Date: January 15, 2023", "2023-01-15"),
            ("Date: 15 Jan 2023", "2023-01-15"),
            ("Date: 2023-01-15", "2023-01-15"),
        ]

        for text, expected in test_cases:
            result = parser.extract_date(text)
            assert result == expected

    def test_extract_date_with_keywords(self, parser):
        """Test date extraction with custom keywords."""
        parser.date_keywords = ["INVOICE DATE:", "BILL DATE:"]

        text = """
        Invoice

        Invoice Date: 2023-01-15
        Bill Date: 2023-01-15
        """

        result = parser.extract_date(text)

        assert result == "2023-01-15"

    def test_extract_date_no_match(self, parser):
        """Test date extraction when no date is found."""
        text = """
        Invoice

        Total: $100.00
        """

        result = parser.extract_date(text)

        assert result is None

    def test_extract_date_multiple_matches(self, parser):
        """Test date extraction with multiple date matches."""
        text = """
        INVOICE

        Date: 2023-01-15
        Due Date: 2023-02-15
        """

        result = parser.extract_date(text)

        # Should return the invoice date (first date found)
        assert result == "2023-01-15"

    def test_extract_date_invalid_format(self, parser):
        """Test date extraction with invalid date format."""
        text = """
        Invoice

        Date: Invalid Date
        """

        result = parser.extract_date(text)

        assert result is None


class TestInvoiceParserInvoiceNumberExtraction:
    """Test InvoiceParser invoice number extraction methods."""

    @pytest.fixture
    def parser(self):
        """Create an InvoiceParser instance for testing."""
        return InvoiceParser()

    def test_extract_invoice_number_success(self, parser):
        """Test successful invoice number extraction."""
        text = """
        INVOICE

        Invoice #: INV-2023-001
        Date: 2023-01-15

        Total: $100.00
        """

        result = parser.extract_invoice_number(text)

        assert result == "INV-2023-001"

    def test_extract_invoice_number_with_different_formats(self, parser):
        """Test invoice number extraction with different formats."""
        test_cases = [
            ("Invoice #: INV-2023-001", "INV-2023-001"),
            ("Invoice Number: 12345", "12345"),
            ("Bill #: BILL-001", "BILL-001"),
            ("Invoice ID: 2023-001", "2023-001"),
            ("Invoice: ABC123", "ABC123"),
        ]

        for text, expected in test_cases:
            result = parser.extract_invoice_number(text)
            assert result == expected

    def test_extract_invoice_number_no_match(self, parser):
        """Test invoice number extraction when no number is found."""
        text = """
        Invoice

        Date: 2023-01-15
        Total: $100.00
        """

        result = parser.extract_invoice_number(text)

        assert result is None


class TestInvoiceParserFullParsing:
    """Test InvoiceParser full parsing workflow."""

    @pytest.fixture
    def parser(self):
        """Create an InvoiceParser instance for testing."""
        return InvoiceParser()

    def test_parse_success(self, parser, tmp_path):
        """Test successful full parsing workflow."""
        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_text("dummy content")

        sample_text = """
        INVOICE

        Invoice #: INV-2023-001
        Date: 2023-01-15

        ABC Company Inc.
        123 Business Street

        Item 1: $50.00
        Item 2: $75.00

        Total: $125.00
        """

        with patch.object(parser, "extract_text") as mock_extract:
            mock_extract.return_value = sample_text

            result = parser.parse(str(pdf_file))

            assert result["company"] == "ABC Company Inc."
            assert result["total"] == 125.00
            assert result["date"] == "2023-01-15"
            assert result["invoice_number"] == "INV-2023-001"
            assert result["raw_text"] == sample_text
            assert result["confidence"] > 0.7
            assert result["parser_type"] == "invoice"

    def test_parse_with_partial_data(self, parser, tmp_path):
        """Test parsing with partial data extraction."""
        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_text("dummy content")

        sample_text = """
        INVOICE

        Date: 2023-01-15
        Total: $100.00
        """

        with patch.object(parser, "extract_text") as mock_extract:
            mock_extract.return_value = sample_text

            result = parser.parse(str(pdf_file))

            assert result["company"] is None
            assert result["total"] == 100.00
            assert result["date"] == "2023-01-15"
            assert result["invoice_number"] is None
            assert result["confidence"] < 0.7  # Lower confidence due to missing data

    def test_parse_with_no_data(self, parser, tmp_path):
        """Test parsing with no extractable data."""
        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_text("dummy content")

        sample_text = """
        Document

        Some text without invoice data
        """

        with patch.object(parser, "extract_text") as mock_extract:
            mock_extract.return_value = sample_text

            result = parser.parse(str(pdf_file))

            assert result["company"] is None
            assert result["total"] is None
            assert result["date"] is None
            assert result["invoice_number"] is None
            assert result["confidence"] == 0.0

    def test_parse_with_error_handling(self, parser, tmp_path):
        """Test parsing with error handling."""
        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_text("dummy content")

        with patch.object(parser, "extract_text") as mock_extract:
            mock_extract.side_effect = Exception("Extraction failed")

            with pytest.raises(Exception, match="Extraction failed"):
                parser.parse(str(pdf_file))


class TestInvoiceParserValidation:
    """Test InvoiceParser validation methods."""

    @pytest.fixture
    def parser(self):
        """Create an InvoiceParser instance for testing."""
        return InvoiceParser()

    def test_validate_invoice_data_success(self, parser):
        """Test successful invoice data validation."""
        data = {
            "company": "ABC Company",
            "total": 100.00,
            "date": "2023-01-15",
            "invoice_number": "INV-001",
        }

        result = parser._validate_invoice_data(data)

        assert result is True

    def test_validate_invoice_data_missing_required(self, parser):
        """Test invoice data validation with missing required fields."""
        data = {
            "company": "ABC Company",
            "date": "2023-01-15",
            # Missing total and invoice_number
        }

        result = parser._validate_invoice_data(data)

        assert result is False

    def test_validate_invoice_data_invalid_total(self, parser):
        """Test invoice data validation with invalid total."""
        data = {
            "company": "ABC Company",
            "total": -100.00,  # Negative total
            "date": "2023-01-15",
            "invoice_number": "INV-001",
        }

        result = parser._validate_invoice_data(data)

        assert result is False

    def test_validate_invoice_data_invalid_date(self, parser):
        """Test invoice data validation with invalid date."""
        data = {
            "company": "ABC Company",
            "total": 100.00,
            "date": "invalid-date",
            "invoice_number": "INV-001",
        }

        result = parser._validate_invoice_data(data)

        assert result is False


class TestInvoiceParserErrorHandling:
    """Test InvoiceParser error handling and recovery."""

    @pytest.fixture
    def parser(self):
        """Create an InvoiceParser instance for testing."""
        return InvoiceParser()

    def test_handle_extraction_error_with_retry(self, parser, tmp_path):
        """Test extraction error handling with retry mechanism."""
        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_text("dummy content")

        with patch.object(parser, "extract_text") as mock_extract:
            mock_extract.side_effect = [
                Exception("First failure"),
                Exception("Second failure"),
                "Success on third try",
            ]

            result = parser.parse(str(pdf_file), max_retries=3)

            assert result["raw_text"] == "Success on third try"
            assert mock_extract.call_count == 3

    def test_handle_extraction_error_max_retries_exceeded(self, parser, tmp_path):
        """Test extraction error handling when max retries are exceeded."""
        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_text("dummy content")

        with patch.object(parser, "extract_text") as mock_extract:
            mock_extract.side_effect = Exception("Always fails")

            with pytest.raises(Exception, match="Always fails"):
                parser.parse(str(pdf_file), max_retries=2)

            assert mock_extract.call_count == 2


class TestInvoiceParserPerformance:
    """Test InvoiceParser performance characteristics."""

    @pytest.fixture
    def parser(self):
        """Create an InvoiceParser instance for testing."""
        return InvoiceParser()

    def test_large_invoice_processing(self, parser, tmp_path):
        """Test processing of large invoice files."""
        pdf_file = tmp_path / "large_invoice.pdf"
        pdf_file.write_text("x" * 1000000)  # 1MB of content

        large_text = "INVOICE\n" + "Item " + "x" * 100000 + "\nTotal: $1000.00"

        with patch.object(parser, "extract_text") as mock_extract:
            mock_extract.return_value = large_text

            result = parser.parse(str(pdf_file))

            assert result["total"] == 1000.00
            assert result["raw_text"] == large_text

    def test_multiple_concurrent_parsing(self, parser, tmp_path):
        """Test handling of multiple concurrent parsing requests."""
        import threading

        results = []
        errors = []

        def parsing_worker():
            try:
                pdf_file = tmp_path / f"test_{threading.current_thread().name}.pdf"
                pdf_file.write_text("dummy content")

                sample_text = f"""
                INVOICE {threading.current_thread().name}
                Total: $100.00
                Date: 2023-01-15
                """

                with patch.object(parser, "extract_text") as mock_extract:
                    mock_extract.return_value = sample_text
                    result = parser.parse(str(pdf_file))
                    results.append(result)
            except Exception as e:
                errors.append(e)

        threads = []
        for i in range(5):
            thread = threading.Thread(target=parsing_worker)
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        assert len(results) == 5
        assert len(errors) == 0


class TestInvoiceParserIntegration:
    """Integration tests for InvoiceParser."""

    @pytest.fixture
    def parser(self):
        """Create an InvoiceParser instance for testing."""
        return InvoiceParser()

    def test_full_invoice_parsing_workflow(self, parser, tmp_path):
        """Test complete invoice parsing workflow."""
        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_text("dummy content")

        sample_text = """
        INVOICE

        Invoice #: INV-2023-001
        Date: 2023-01-15

        ABC Company Inc.
        123 Business Street
        City, State 12345

        Item 1: $50.00
        Item 2: $75.00
        Tax: $12.50

        Total: $137.50
        """

        with patch.object(parser, "extract_text") as mock_extract:
            mock_extract.return_value = sample_text

            result = parser.parse(str(pdf_file))

            assert result["company"] == "ABC Company Inc."
            assert result["total"] == 137.50
            assert result["date"] == "2023-01-15"
            assert result["invoice_number"] == "INV-2023-001"
            assert result["raw_text"] == sample_text
            assert result["confidence"] > 0.7
            assert result["parser_type"] == "invoice"

    def test_parsing_with_text_preprocessing(self, parser, tmp_path):
        """Test invoice parsing with text preprocessing workflow."""
        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_text("dummy content")

        raw_text = "  INVOICE  \n\n  Total:  $100.00  \n  Date:  2023-01-15  "
        cleaned_text = "INVOICE Total: $100.00 Date: 2023-01-15"

        with patch.object(parser, "extract_text") as mock_extract:
            mock_extract.return_value = raw_text

            with patch.object(parser, "preprocess_text") as mock_preprocess:
                mock_preprocess.return_value = cleaned_text

                result = parser.parse(str(pdf_file))

                assert result["total"] == 100.00
                assert result["date"] == "2023-01-15"
                mock_preprocess.assert_called_once_with(raw_text)
