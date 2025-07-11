# flake8: noqa
"""Unit tests for the InvoiceParser class."""

import sys
import os

sys.path.insert(
    0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "src")
)  # noqa: E402
from pathlib import Path
import pytest
from unittest.mock import patch

from ocrinvoice.parsers.invoice_parser import InvoiceParser


class TestInvoiceParserInitialization:
    """Test InvoiceParser initialization and configuration."""

    def test_init_with_default_config(self) -> None:
        """Test initialization with default configuration."""
        parser = InvoiceParser()
        assert parser.config == {}
        assert parser.debug is False
        assert parser.confidence_threshold == 0.7
        assert parser.max_retries == 3
        assert parser.parser_type == "invoice"

    def test_init_with_custom_config(self) -> None:
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

    def test_init_inherits_from_base_parser(self) -> None:
        """Test that InvoiceParser inherits from BaseParser."""
        parser = InvoiceParser()
        assert hasattr(parser, "extract_text")
        assert hasattr(parser, "preprocess_text")
        assert hasattr(parser, "validate_pdf_path")
        assert hasattr(parser, "parse")


class TestInvoiceParserCompanyExtraction:
    """Test InvoiceParser company extraction methods."""

    @pytest.fixture  # type: ignore
    def parser(self) -> InvoiceParser:
        """Create an InvoiceParser instance for testing."""
        return InvoiceParser()

    def test_extract_company_known_company(self, parser: InvoiceParser) -> None:
        """Test company extraction with known company from config."""
        # Set up known companies in config
        parser.config = {"known_companies": ["HYDRO-QUÉBEC", "RBC", "TD"]}

        text = """
        INVOICE

        HYDRO-QUÉBEC
        123 Business Street
        City, State 12345

        Bill To:
        Customer Name
        """

        result = parser.extract_company(text)

        assert result == "HYDRO-QUÉBEC"

    def test_extract_company_after_invoice_header(self, parser: InvoiceParser) -> None:
        """Test company extraction after INVOICE header."""
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

        assert result == "Acme Corporation Ltd."

    def test_extract_company_with_keyword_colon(self, parser: InvoiceParser) -> None:
        """Test company extraction with keyword: format."""
        # Clear known companies to test keyword-based extraction
        parser.config = {"known_companies": []}
        parser.company_keywords = ["FROM:", "BILLER:"]

        text = """
        FROM: XYZ Corporation
        TO: Customer Name

        Total: $100.00
        """

        result = parser.extract_company(text)

        assert result == "XYZ Corporation"

    def test_extract_company_no_match(self, parser: InvoiceParser) -> None:
        """Test company extraction when no company is found."""
        # Clear known companies to test no-match scenario
        parser.config = {"known_companies": []}

        text = """
        Customer Invoice

        Total: $100.00
        Date: 2023-01-15
        """

        result = parser.extract_company(text)

        assert result is None

    def test_extract_company_ignores_dates(self, parser: InvoiceParser) -> None:
        """Test company extraction ignores date lines."""
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

        assert result == "Acme Corporation Ltd."


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

        Date: 2023-01-15
        Due Date: 2023-02-15

        Total: $100.00
        """

        result = parser.extract_date(text)

        assert result == "2023-01-15"

    def test_extract_date_with_different_formats(self, parser: InvoiceParser) -> None:
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

    def test_extract_date_with_keywords(self, parser: InvoiceParser) -> None:
        """Test date extraction with custom keywords."""
        parser.date_keywords = ["INVOICE DATE:", "BILL DATE:"]

        text = """
        Invoice

        Invoice Date: 2023-01-15
        Bill Date: 2023-01-15
        """

        result = parser.extract_date(text)

        assert result == "2023-01-15"

    def test_extract_date_no_match(self, parser: InvoiceParser) -> None:
        """Test date extraction when no date is found."""
        text = """
        Invoice

        Total: $100.00
        """

        result = parser.extract_date(text)

        assert result is None

    def test_extract_date_multiple_matches(self, parser: InvoiceParser) -> None:
        """Test date extraction with multiple date matches."""
        text = """
        INVOICE

        Date: 2023-01-15
        Due Date: 2023-02-15
        """

        result = parser.extract_date(text)

        # Should return the invoice date (first date found)
        assert result == "2023-01-15"

    def test_extract_date_invalid_format(self, parser: InvoiceParser) -> None:
        """Test date extraction with invalid date format."""
        text = """
        Invoice

        Date: Invalid Date
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

        Invoice #: INV-2023-001
        Date: 2023-01-15

        Total: $100.00
        """

        result = parser.extract_invoice_number(text)

        assert result == "INV-2023-001"

    def test_extract_invoice_number_with_different_formats(
        self, parser: InvoiceParser
    ) -> None:
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

    def test_extract_invoice_number_no_match(self, parser: InvoiceParser) -> None:
        """Test invoice number extraction when no number is found."""
        text = """
        Invoice

        Date: 2023-01-15
        Total: $100.00
        """

        result = parser.extract_invoice_number(text)

        assert result is None

    def test_extract_invoice_number_ignores_years(self, parser: InvoiceParser) -> None:
        """Test invoice number extraction ignores years."""
        text = """
        Invoice

        Date: 2023-01-15
        Year: 2023

        Invoice #: INV-2023-001
        """

        result = parser.extract_invoice_number(text)

        assert result == "INV-2023-001"

    def test_extract_invoice_number_requires_minimum_length(
        self, parser: InvoiceParser
    ) -> None:
        """Test invoice number extraction requires minimum length."""
        text = """
        Invoice

        Invoice #: 123  # Too short
        """

        result = parser.extract_invoice_number(text)

        assert result is None


class TestInvoiceParserFullParsing:
    """Test InvoiceParser full parsing workflow."""

    @pytest.fixture  # type: ignore
    def parser(self) -> InvoiceParser:
        """Create an InvoiceParser instance for testing."""
        return InvoiceParser()

    def test_parse_with_no_data(self, parser: InvoiceParser, tmp_path: Path) -> None:
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

    def test_parse_with_error_handling(
        self, parser: InvoiceParser, tmp_path: Path
    ) -> None:
        """Test parsing with error handling."""
        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_text("dummy content")

        with patch.object(parser, "extract_text") as mock_extract:
            mock_extract.side_effect = Exception("Extraction failed")

            with pytest.raises(Exception, match="Extraction failed"):
                parser.parse(str(pdf_file))


class TestInvoiceParserValidation:
    """Test InvoiceParser validation methods."""

    @pytest.fixture  # type: ignore
    def parser(self) -> InvoiceParser:
        """Create an InvoiceParser instance for testing."""
        return InvoiceParser()

    def test_validate_invoice_data_success(self, parser: InvoiceParser) -> None:
        """Test successful invoice data validation."""
        data = {
            "company": "HYDRO-QUÉBEC",
            "total": 100.00,
            "date": "2023-01-15",
            "invoice_number": "INV-001",
        }

        result = parser._validate_invoice_data(data)

        assert result is True

    def test_validate_invoice_data_missing_required(
        self, parser: InvoiceParser
    ) -> None:
        """Test invoice data validation with missing required fields."""
        data = {
            "company": "HYDRO-QUÉBEC",
            "date": "2023-01-15",
            # Missing total and invoice_number
        }

        result = parser._validate_invoice_data(data)

        assert result is False

    def test_validate_invoice_data_invalid_total(self, parser: InvoiceParser) -> None:
        """Test invoice data validation with invalid total."""
        data = {
            "company": "HYDRO-QUÉBEC",
            "total": -100.00,  # Negative total
            "date": "2023-01-15",
            "invoice_number": "INV-001",
        }

        result = parser._validate_invoice_data(data)

        assert result is False

    def test_validate_invoice_data_invalid_date(self, parser: InvoiceParser) -> None:
        """Test invoice data validation with invalid date."""
        data = {
            "company": "HYDRO-QUÉBEC",
            "total": 100.00,
            "date": "invalid-date",
            "invoice_number": "INV-001",
        }

        result = parser._validate_invoice_data(data)

        assert result is False


class TestInvoiceParserErrorHandling:
    """Test InvoiceParser error handling and recovery."""

    @pytest.fixture  # type: ignore
    def parser(self) -> InvoiceParser:
        """Create an InvoiceParser instance for testing."""
        return InvoiceParser()

    def test_handle_extraction_error_with_retry(
        self, parser: InvoiceParser, tmp_path: Path
    ) -> None:
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

    def test_handle_extraction_error_max_retries_exceeded(
        self, parser: InvoiceParser, tmp_path: Path
    ) -> None:
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

    @pytest.fixture  # type: ignore
    def parser(self) -> InvoiceParser:
        """Create an InvoiceParser instance for testing."""
        return InvoiceParser()

    def test_large_invoice_processing(
        self, parser: InvoiceParser, tmp_path: Path
    ) -> None:
        """Test processing of large invoice files."""
        pdf_file = tmp_path / "large_invoice.pdf"
        pdf_file.write_text("x" * 1000000)  # 1MB of content

        large_text = "INVOICE\n" + "Item " + "x" * 100000 + "\nTotal: $1000.00"

        with patch.object(parser, "extract_text") as mock_extract:
            mock_extract.return_value = large_text

            result = parser.parse(str(pdf_file))

            assert result["total"] == 1000.00
            assert result["raw_text"] == large_text

    def test_multiple_concurrent_parsing(
        self, parser: InvoiceParser, tmp_path: Path
    ) -> None:
        """Test handling of multiple concurrent parsing requests."""
        import threading

        results = []
        errors = []

        def parsing_worker() -> None:
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

    @pytest.fixture  # type: ignore
    def parser(self) -> InvoiceParser:
        """Create an InvoiceParser instance for testing."""
        return InvoiceParser()

    def test_parsing_with_text_preprocessing(
        self, parser: InvoiceParser, tmp_path: Path
    ) -> None:
        """Test invoice parsing with text preprocessing workflow."""
        parser.config = {"known_companies": ["HYDRO-QUÉBEC"]}
        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_text("dummy content")
        raw_text = "  INVOICE  \n\n  Total:  $100.00  \n  Date:  2024-01-15  "
        cleaned_text = "INVOICE Total: $100.00 Date: 2024-01-15"
        with patch.object(parser, "extract_text") as mock_extract:
            mock_extract.return_value = raw_text
            with patch.object(parser, "preprocess_text") as mock_preprocess:
                mock_preprocess.return_value = cleaned_text
                result = parser.parse(str(pdf_file))
                # Just test that preprocessing was called, not the specific results
                mock_preprocess.assert_called_once_with(raw_text)
                assert result["raw_text"] == raw_text
                assert result["parser_type"] == "invoice"
