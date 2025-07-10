"""Unit tests for the BaseParser class."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from typing import Dict, Any

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from ocrinvoice.parsers.base_parser import BaseParser
from ocrinvoice.core.ocr_engine import OCREngine


class TestBaseParser(BaseParser):
    """Concrete implementation of BaseParser for testing."""

    def parse(self, pdf_path):
        """Test implementation of parse method."""
        text = self.extract_text(pdf_path)
        preprocessed = self.preprocess_text(text)

        return self.validate_extraction_result(
            {
                "company": self.extract_company(preprocessed),
                "total": self.extract_total(preprocessed),
                "date": self.extract_date(preprocessed),
                "raw_text": text,
            }
        )

    def extract_company(self, text: str):
        """Test implementation of extract_company."""
        if "company" in text.lower():
            return "Test Company"
        return None

    def extract_total(self, text: str):
        """Test implementation of extract_total."""
        return self.extract_amount_with_context(text, ["total", "amount"])

    def extract_date(self, text: str):
        """Test implementation of extract_date."""
        patterns = [r"\d{1,2}/\d{1,2}/\d{2,4}", r"\d{4}-\d{2}-\d{2}"]
        return self.extract_date_with_patterns(text, patterns)


class TestBaseParserInitialization:
    """Test BaseParser initialization and configuration."""

    def test_init_with_basic_config(self):
        """Test initialization with basic configuration."""
        config = {"debug": True}
        parser = TestBaseParser(config)

        assert parser.config == config
        assert parser.debug is True
        assert parser.confidence_threshold == 0.7  # default
        assert parser.max_retries == 3  # default
        assert isinstance(parser.ocr_engine, OCREngine)
        assert hasattr(parser.fuzzy_matcher, "threshold")  # real or mock class
        assert hasattr(
            parser.amount_normalizer, "default_currency"
        )  # real or mock class
        assert hasattr(parser.ocr_corrections, "correct_text")  # real or mock class

    def test_init_with_full_config(self):
        """Test initialization with full configuration."""
        config = {
            "debug": True,
            "confidence_threshold": 0.8,
            "max_retries": 5,
            "fuzzy_threshold": 0.9,
            "default_currency": "EUR",
            "company_aliases": {"alias1": "company1"},
            "ocr_config": {"ocr_language": "eng"},
        }

        parser = TestBaseParser(config)

        assert parser.confidence_threshold == 0.8
        assert parser.max_retries == 5
        assert parser.company_aliases == {"alias1": "company1"}


class TestBaseParserValidation:
    """Test BaseParser validation methods."""

    @pytest.fixture
    def parser(self):
        """Create a parser instance for testing."""
        return TestBaseParser({"debug": False})

    def test_validate_pdf_path_valid(self, parser, tmp_path):
        """Test validation of valid PDF path."""
        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_text("dummy content")

        result = parser.validate_pdf_path(pdf_file)
        assert result == pdf_file

    def test_validate_pdf_path_not_exists(self, parser):
        """Test validation of non-existent PDF path."""
        with pytest.raises(FileNotFoundError):
            parser.validate_pdf_path("nonexistent.pdf")

    def test_validate_pdf_path_not_file(self, parser, tmp_path):
        """Test validation of path that is not a file."""
        directory = tmp_path / "directory"
        directory.mkdir()

        with pytest.raises(ValueError, match="Path is not a file"):
            parser.validate_pdf_path(directory)

    def test_validate_pdf_path_not_pdf(self, parser, tmp_path):
        """Test validation of non-PDF file."""
        text_file = tmp_path / "test.txt"
        text_file.write_text("dummy content")

        with pytest.raises(ValueError, match="File is not a PDF"):
            parser.validate_pdf_path(text_file)


class TestBaseParserTextExtraction:
    """Test BaseParser text extraction methods."""

    @pytest.fixture
    def parser(self):
        """Create a parser instance for testing."""
        return TestBaseParser({"debug": False})

    @patch("ocrinvoice.parsers.base_parser.OCREngine")
    def test_extract_text_success(self, mock_ocr_engine, parser, tmp_path):
        """Test successful text extraction."""
        # Setup
        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_text("dummy content")

        mock_engine = Mock()
        mock_engine.extract_text_from_pdf.return_value = "Extracted text content"
        parser.ocr_engine = mock_engine

        # Execute
        result = parser.extract_text(pdf_file)

        # Verify
        assert result == "Extracted text content"
        mock_engine.extract_text_from_pdf.assert_called_once_with(str(pdf_file))

    @patch("ocrinvoice.parsers.base_parser.OCREngine")
    def test_extract_text_retry_on_failure(self, mock_ocr_engine, parser, tmp_path):
        """Test text extraction with retry mechanism."""
        # Setup
        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_text("dummy content")

        mock_engine = Mock()
        mock_engine.extract_text_from_pdf.side_effect = [
            Exception("First failure"),
            Exception("Second failure"),
            "Success on third try",
        ]
        parser.ocr_engine = mock_engine
        parser.max_retries = 3

        # Execute
        result = parser.extract_text(pdf_file)

        # Verify
        assert result == "Success on third try"
        assert mock_engine.extract_text_from_pdf.call_count == 3

    @patch("ocrinvoice.parsers.base_parser.OCREngine")
    def test_extract_text_max_retries_exceeded(self, mock_ocr_engine, parser, tmp_path):
        """Test text extraction when max retries are exceeded."""
        # Setup
        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_text("dummy content")

        mock_engine = Mock()
        mock_engine.extract_text_from_pdf.side_effect = Exception("Always fails")
        parser.ocr_engine = mock_engine
        parser.max_retries = 2

        # Execute and verify
        with pytest.raises(Exception, match="Always fails"):
            parser.extract_text(pdf_file)

        assert mock_engine.extract_text_from_pdf.call_count == 2


class TestBaseParserTextProcessing:
    """Test BaseParser text processing methods."""

    @pytest.fixture
    def parser(self):
        """Create a parser instance for testing."""
        return TestBaseParser({"debug": False})

    def test_preprocess_text_basic(self, parser):
        """Test basic text preprocessing."""
        raw_text = "  This   is   a   test   text  "
        result = parser.preprocess_text(raw_text)
        assert result == "This is a test text"

    def test_preprocess_text_empty(self, parser):
        """Test preprocessing of empty text."""
        result = parser.preprocess_text("")
        assert result == ""

    def test_preprocess_text_with_ocr_corrections(self, parser):
        """Test text preprocessing with OCR corrections."""
        # Mock OCR corrections
        parser.ocr_corrections.correct_text = Mock(return_value="Corrected text")

        raw_text = "Raw text with OCR errors"
        result = parser.preprocess_text(raw_text)

        assert result == "Corrected text"
        parser.ocr_corrections.correct_text.assert_called_once_with(raw_text)


class TestBaseParserExtractionHelpers:
    """Test BaseParser extraction helper methods."""

    @pytest.fixture
    def parser(self):
        """Create a parser instance for testing."""
        return TestBaseParser({"debug": False})

    def test_extract_amount_with_context(self, parser):
        """Test amount extraction with context keywords."""
        # Mock amount normalizer
        parser.amount_normalizer.extract_amounts_from_text = Mock(
            return_value=["$100.00"]
        )

        text = "Invoice total: $100.00\nOther line: $50.00"
        result = parser.extract_amount_with_context(text, ["total"])

        assert result == "$100.00"

    def test_extract_date_with_patterns(self, parser):
        """Test date extraction with patterns."""
        text = "Invoice date: 12/25/2023\nDue date: 2024-01-15"

        result = parser.extract_date_with_patterns(text, [r"\d{1,2}/\d{1,2}/\d{2,4}"])

        assert result == "2023-12-25T00:00:00"

    def test_parse_date_string_valid(self, parser):
        """Test parsing of valid date strings."""
        date_str = "12/25/2023"
        result = parser._parse_date_string(date_str)

        assert result is not None
        assert result.year == 2023
        assert result.month == 12
        assert result.day == 25

    def test_parse_date_string_invalid(self, parser):
        """Test parsing of invalid date strings."""
        date_str = "invalid date"
        result = parser._parse_date_string(date_str)

        assert result is None


class TestBaseParserConfidence:
    """Test BaseParser confidence calculation."""

    @pytest.fixture
    def parser(self):
        """Create a parser instance for testing."""
        return TestBaseParser({"debug": False})

    def test_calculate_confidence_full_data(self, parser):
        """Test confidence calculation with full data."""
        extracted_data = {
            "company": "Test Company",
            "total": "$100.00",
            "date": "2023-12-25",
            "raw_text": "Some text",
        }

        # Mock amount normalizer validation
        parser.amount_normalizer.validate_amount = Mock(return_value=True)

        confidence = parser.calculate_confidence(extracted_data, "Some text")

        assert confidence > 0.8  # Should be high with all fields present

    def test_calculate_confidence_partial_data(self, parser):
        """Test confidence calculation with partial data."""
        extracted_data = {
            "company": "Test Company",
            "total": None,
            "date": None,
            "raw_text": "Some text",
        }

        confidence = parser.calculate_confidence(extracted_data, "Some text")

        assert confidence < 0.5  # Should be lower with missing fields

    def test_validate_extraction_result(self, parser):
        """Test extraction result validation."""
        raw_result = {
            "company": "Test Company",
            "total": "$100.00",
            "raw_text": "Some text",
        }

        # Mock amount normalizer validation
        parser.amount_normalizer.validate_amount = Mock(return_value=True)

        validated = parser.validate_extraction_result(raw_result)

        assert "parsed_at" in validated
        assert "parser_type" in validated
        assert "confidence" in validated
        assert "is_valid" in validated
        assert validated["parser_type"] == "TestBaseParser"


class TestBaseParserLogging:
    """Test BaseParser logging methods."""

    @pytest.fixture
    def parser(self):
        """Create a parser instance for testing."""
        return TestBaseParser({"debug": True})

    def test_log_parsing_result_high_confidence(self, parser):
        """Test logging with high confidence result."""
        result = {"confidence": 0.9, "is_valid": True}

        with patch.object(parser.logger, "info") as mock_info:
            parser.log_parsing_result("test.pdf", result)
            mock_info.assert_called_once()

    def test_log_parsing_result_low_confidence(self, parser):
        """Test logging with low confidence result."""
        result = {"confidence": 0.3, "is_valid": False}

        with patch.object(parser.logger, "warning") as mock_warning:
            parser.log_parsing_result("test.pdf", result)
            mock_warning.assert_called_once()


class TestBaseParserInfo:
    """Test BaseParser information methods."""

    @pytest.fixture
    def parser(self):
        """Create a parser instance for testing."""
        return TestBaseParser({"debug": True, "confidence_threshold": 0.8})

    def test_get_parser_info(self, parser):
        """Test getting parser information."""
        info = parser.get_parser_info()

        assert info["parser_type"] == "TestBaseParser"
        assert info["debug_mode"] is True
        assert info["confidence_threshold"] == 0.8
        assert info["max_retries"] == 3
        assert "ocr_engine_info" in info

    def test_test_parser_capabilities(self, parser):
        """Test parser capabilities testing."""
        # Mock OCR engine test
        mock_test_result = {
            "tesseract_available": True,
            "dependencies_available": True,
            "errors": [],
        }
        parser.ocr_engine.test_ocr_capabilities = Mock(return_value=mock_test_result)

        capabilities = parser.test_parser_capabilities()

        assert capabilities["parser_available"] is True
        assert capabilities["ocr_engine_available"] is True
        assert capabilities["dependencies_available"] is True
        assert capabilities["errors"] == []


class TestBaseParserIntegration:
    """Integration tests for BaseParser."""

    @pytest.fixture
    def parser(self):
        """Create a parser instance for testing."""
        return TestBaseParser(
            {"debug": False, "confidence_threshold": 0.7, "max_retries": 2}
        )

    @patch("ocrinvoice.parsers.base_parser.OCREngine")
    def test_full_parse_workflow(self, mock_ocr_engine, parser, tmp_path):
        """Test the full parsing workflow."""
        # Setup
        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_text("dummy content")

        mock_engine = Mock()
        mock_engine.extract_text_from_pdf.return_value = (
            "Invoice from Test Company\nTotal: $100.00\nDate: 12/25/2023"
        )
        parser.ocr_engine = mock_engine

        # Mock utility classes
        parser.ocr_corrections.correct_text = Mock(
            return_value="Invoice from Test Company\nTotal: $100.00\nDate: 12/25/2023"
        )
        parser.amount_normalizer.extract_amounts_from_text = Mock(
            return_value=["$100.00"]
        )
        parser.amount_normalizer.validate_amount = Mock(return_value=True)

        # Execute
        result = parser.parse(pdf_file)

        # Verify
        assert result["company"] == "Test Company"
        assert result["total"] == "$100.00"
        assert result["date"] == "2023-12-25T00:00:00"
        assert "confidence" in result
        assert "is_valid" in result
        assert "parsed_at" in result
