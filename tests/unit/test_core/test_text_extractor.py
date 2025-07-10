"""Unit tests for the TextExtractor class."""

import pytest
from unittest.mock import Mock, patch, MagicMock, call
from pathlib import Path
from typing import Dict, Any
import tempfile
import os

import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "src"))

from ocrinvoice.core.text_extractor import TextExtractor


class TestTextExtractorInitialization:
    """Test TextExtractor initialization and configuration."""

    def test_init_with_default_config(self):
        """Test initialization with default configuration."""
        extractor = TextExtractor()

        assert extractor.config == {}
        assert extractor.extraction_methods == ["pdfplumber", "pypdf2", "fallback"]
        assert extractor.min_text_length == 10

    def test_init_with_custom_config(self):
        """Test initialization with custom configuration."""
        config = {
            "extraction_methods": ["pdfplumber"],
            "min_text_length": 50,
            "pdfplumber_config": {"laparams": {"line_margin": 0.5}},
        }

        extractor = TextExtractor(config)

        assert extractor.config == config
        assert extractor.extraction_methods == ["pdfplumber"]
        assert extractor.min_text_length == 50

    def test_init_with_invalid_methods(self):
        """Test initialization with invalid extraction methods."""
        config = {"extraction_methods": ["invalid_method"]}

        with pytest.raises(ValueError, match="Invalid extraction method"):
            TextExtractor(config)


class TestTextExtractorDependencyValidation:
    """Test TextExtractor dependency validation methods."""

    def test_validate_dependencies_success(self):
        """Test successful dependency validation."""
        with patch(
            "ocrinvoice.core.text_extractor.importlib.util.find_spec"
        ) as mock_find_spec:
            mock_find_spec.return_value = Mock()

            extractor = TextExtractor()
            # Should not raise any exception
            assert extractor._validate_dependencies() is None

    @patch("ocrinvoice.core.text_extractor.importlib.util.find_spec")
    def test_validate_dependencies_missing_pdfplumber(self, mock_find_spec):
        """Test dependency validation with missing pdfplumber."""

        def side_effect(name):
            if name == "pdfplumber":
                return None
            return Mock()

        mock_find_spec.side_effect = side_effect

        with pytest.raises(ImportError, match="pdfplumber not installed"):
            TextExtractor({"extraction_methods": ["pdfplumber"]})

    @patch("ocrinvoice.core.text_extractor.importlib.util.find_spec")
    def test_validate_dependencies_missing_pypdf2(self, mock_find_spec):
        """Test dependency validation with missing PyPDF2."""

        def side_effect(name):
            if name == "PyPDF2":
                return None
            return Mock()

        mock_find_spec.side_effect = side_effect

        with pytest.raises(ImportError, match="PyPDF2 not installed"):
            TextExtractor({"extraction_methods": ["pypdf2"]})


class TestTextExtractorPDFPlumberExtraction:
    """Test TextExtractor PDFPlumber extraction methods."""

    @pytest.fixture
    def extractor(self):
        """Create a TextExtractor instance for testing."""
        return TextExtractor()

    @patch("ocrinvoice.core.text_extractor.pdfplumber")
    def test_extract_with_pdfplumber_success(
        self, mock_pdfplumber, extractor, tmp_path
    ):
        """Test successful text extraction using PDFPlumber."""
        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_text("dummy content")

        mock_pdf = Mock()
        mock_page = Mock()
        mock_page.extract_text.return_value = "Extracted text from PDFPlumber"
        mock_pdf.pages = [mock_page]
        mock_pdfplumber.open.return_value.__enter__.return_value = mock_pdf

        result = extractor._extract_with_pdfplumber(str(pdf_file))

        assert result == "Extracted text from PDFPlumber"
        mock_pdfplumber.open.assert_called_once_with(str(pdf_file))

    @patch("ocrinvoice.core.text_extractor.pdfplumber")
    def test_extract_with_pdfplumber_multiple_pages(
        self, mock_pdfplumber, extractor, tmp_path
    ):
        """Test text extraction from multiple pages using PDFPlumber."""
        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_text("dummy content")

        mock_pdf = Mock()
        mock_page1 = Mock()
        mock_page1.extract_text.return_value = "Page 1 text"
        mock_page2 = Mock()
        mock_page2.extract_text.return_value = "Page 2 text"
        mock_pdf.pages = [mock_page1, mock_page2]
        mock_pdfplumber.open.return_value.__enter__.return_value = mock_pdf

        result = extractor._extract_with_pdfplumber(str(pdf_file))

        assert result == "Page 1 text\nPage 2 text"

    @patch("ocrinvoice.core.text_extractor.pdfplumber")
    def test_extract_with_pdfplumber_empty_pdf(
        self, mock_pdfplumber, extractor, tmp_path
    ):
        """Test text extraction from empty PDF using PDFPlumber."""
        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_text("dummy content")

        mock_pdf = Mock()
        mock_page = Mock()
        mock_page.extract_text.return_value = ""
        mock_pdf.pages = [mock_page]
        mock_pdfplumber.open.return_value.__enter__.return_value = mock_pdf

        result = extractor._extract_with_pdfplumber(str(pdf_file))

        assert result == ""

    @patch("ocrinvoice.core.text_extractor.pdfplumber")
    def test_extract_with_pdfplumber_file_not_found(self, mock_pdfplumber, extractor):
        """Test PDFPlumber extraction with non-existent file."""
        mock_pdfplumber.open.side_effect = FileNotFoundError("File not found")

        with pytest.raises(FileNotFoundError, match="File not found"):
            extractor._extract_with_pdfplumber("nonexistent.pdf")

    @patch("ocrinvoice.core.text_extractor.pdfplumber")
    def test_extract_with_pdfplumber_invalid_pdf(
        self, mock_pdfplumber, extractor, tmp_path
    ):
        """Test PDFPlumber extraction with invalid PDF."""
        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_text("not a pdf")

        mock_pdfplumber.open.side_effect = Exception("Invalid PDF")

        with pytest.raises(Exception, match="Invalid PDF"):
            extractor._extract_with_pdfplumber(str(pdf_file))


class TestTextExtractorPyPDF2Extraction:
    """Test TextExtractor PyPDF2 extraction methods."""

    @pytest.fixture
    def extractor(self):
        """Create a TextExtractor instance for testing."""
        return TextExtractor()

    @patch("ocrinvoice.core.text_extractor.PyPDF2")
    def test_extract_with_pypdf2_success(self, mock_pypdf2, extractor, tmp_path):
        """Test successful text extraction using PyPDF2."""
        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_text("dummy content")

        mock_reader = Mock()
        mock_page = Mock()
        mock_page.extract_text.return_value = "Extracted text from PyPDF2"
        mock_reader.pages = [mock_page]
        mock_pypdf2.PdfReader.return_value = mock_reader

        result = extractor._extract_with_pypdf2(str(pdf_file))

        assert result == "Extracted text from PyPDF2"
        mock_pypdf2.PdfReader.assert_called_once_with(str(pdf_file))

    @patch("ocrinvoice.core.text_extractor.PyPDF2")
    def test_extract_with_pypdf2_multiple_pages(self, mock_pypdf2, extractor, tmp_path):
        """Test text extraction from multiple pages using PyPDF2."""
        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_text("dummy content")

        mock_reader = Mock()
        mock_page1 = Mock()
        mock_page1.extract_text.return_value = "Page 1 text"
        mock_page2 = Mock()
        mock_page2.extract_text.return_value = "Page 2 text"
        mock_reader.pages = [mock_page1, mock_page2]
        mock_pypdf2.PdfReader.return_value = mock_reader

        result = extractor._extract_with_pypdf2(str(pdf_file))

        assert result == "Page 1 text\nPage 2 text"

    @patch("ocrinvoice.core.text_extractor.PyPDF2")
    def test_extract_with_pypdf2_empty_pdf(self, mock_pypdf2, extractor, tmp_path):
        """Test text extraction from empty PDF using PyPDF2."""
        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_text("dummy content")

        mock_reader = Mock()
        mock_page = Mock()
        mock_page.extract_text.return_value = ""
        mock_reader.pages = [mock_page]
        mock_pypdf2.PdfReader.return_value = mock_reader

        result = extractor._extract_with_pypdf2(str(pdf_file))

        assert result == ""

    @patch("ocrinvoice.core.text_extractor.PyPDF2")
    def test_extract_with_pypdf2_file_not_found(self, mock_pypdf2, extractor):
        """Test PyPDF2 extraction with non-existent file."""
        mock_pypdf2.PdfReader.side_effect = FileNotFoundError("File not found")

        with pytest.raises(FileNotFoundError, match="File not found"):
            extractor._extract_with_pypdf2("nonexistent.pdf")

    @patch("ocrinvoice.core.text_extractor.PyPDF2")
    def test_extract_with_pypdf2_invalid_pdf(self, mock_pypdf2, extractor, tmp_path):
        """Test PyPDF2 extraction with invalid PDF."""
        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_text("not a pdf")

        mock_pypdf2.PdfReader.side_effect = Exception("Invalid PDF")

        with pytest.raises(Exception, match="Invalid PDF"):
            extractor._extract_with_pypdf2(str(pdf_file))


class TestTextExtractorFallbackExtraction:
    """Test TextExtractor fallback extraction methods."""

    @pytest.fixture
    def extractor(self):
        """Create a TextExtractor instance for testing."""
        return TextExtractor()

    def test_extract_with_fallback_success(self, extractor, tmp_path):
        """Test successful fallback text extraction."""
        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_text("dummy content")

        result = extractor._extract_with_fallback(str(pdf_file))

        # Fallback should return empty string for non-PDF files
        assert result == ""

    def test_extract_with_fallback_file_not_found(self, extractor):
        """Test fallback extraction with non-existent file."""
        with pytest.raises(FileNotFoundError):
            extractor._extract_with_fallback("nonexistent.pdf")


class TestTextExtractorMainExtraction:
    """Test TextExtractor main extraction methods."""

    @pytest.fixture
    def extractor(self):
        """Create a TextExtractor instance for testing."""
        return TextExtractor()

    def test_extract_text_success_with_pdfplumber(self, extractor, tmp_path):
        """Test successful text extraction using PDFPlumber."""
        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_text("dummy content")

        with patch.object(extractor, "_extract_with_pdfplumber") as mock_extract:
            mock_extract.return_value = "Extracted text"

            result = extractor.extract_text(str(pdf_file))

            assert result == "Extracted text"
            mock_extract.assert_called_once_with(str(pdf_file))

    def test_extract_text_fallback_to_pypdf2(self, extractor, tmp_path):
        """Test text extraction with fallback to PyPDF2."""
        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_text("dummy content")

        with patch.object(extractor, "_extract_with_pdfplumber") as mock_pdfplumber:
            mock_pdfplumber.side_effect = Exception("PDFPlumber failed")

            with patch.object(extractor, "_extract_with_pypdf2") as mock_pypdf2:
                mock_pypdf2.return_value = "PyPDF2 extracted text"

                result = extractor.extract_text(str(pdf_file))

                assert result == "PyPDF2 extracted text"
                mock_pdfplumber.assert_called_once_with(str(pdf_file))
                mock_pypdf2.assert_called_once_with(str(pdf_file))

    def test_extract_text_fallback_to_fallback_method(self, extractor, tmp_path):
        """Test text extraction with fallback to fallback method."""
        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_text("dummy content")

        with patch.object(extractor, "_extract_with_pdfplumber") as mock_pdfplumber:
            mock_pdfplumber.side_effect = Exception("PDFPlumber failed")

            with patch.object(extractor, "_extract_with_pypdf2") as mock_pypdf2:
                mock_pypdf2.side_effect = Exception("PyPDF2 failed")

                with patch.object(extractor, "_extract_with_fallback") as mock_fallback:
                    mock_fallback.return_value = "Fallback extracted text"

                    result = extractor.extract_text(str(pdf_file))

                    assert result == "Fallback extracted text"
                    mock_pdfplumber.assert_called_once_with(str(pdf_file))
                    mock_pypdf2.assert_called_once_with(str(pdf_file))
                    mock_fallback.assert_called_once_with(str(pdf_file))

    def test_extract_text_all_methods_fail(self, extractor, tmp_path):
        """Test text extraction when all methods fail."""
        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_text("dummy content")

        with patch.object(extractor, "_extract_with_pdfplumber") as mock_pdfplumber:
            mock_pdfplumber.side_effect = Exception("PDFPlumber failed")

            with patch.object(extractor, "_extract_with_pypdf2") as mock_pypdf2:
                mock_pypdf2.side_effect = Exception("PyPDF2 failed")

                with patch.object(extractor, "_extract_with_fallback") as mock_fallback:
                    mock_fallback.side_effect = Exception("Fallback failed")

                    with pytest.raises(
                        Exception, match="All text extraction methods failed"
                    ):
                        extractor.extract_text(str(pdf_file))

    def test_extract_text_with_custom_methods(self, extractor, tmp_path):
        """Test text extraction with custom extraction methods."""
        extractor.extraction_methods = ["pypdf2", "fallback"]
        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_text("dummy content")

        with patch.object(extractor, "_extract_with_pypdf2") as mock_pypdf2:
            mock_pypdf2.return_value = "PyPDF2 extracted text"

            result = extractor.extract_text(str(pdf_file))

            assert result == "PyPDF2 extracted text"
            mock_pypdf2.assert_called_once_with(str(pdf_file))

    def test_extract_text_file_not_found(self, extractor):
        """Test text extraction with non-existent file."""
        with pytest.raises(FileNotFoundError):
            extractor.extract_text("nonexistent.pdf")

    def test_extract_text_invalid_file(self, extractor, tmp_path):
        """Test text extraction with invalid file."""
        text_file = tmp_path / "test.txt"
        text_file.write_text("not a pdf")

        with pytest.raises(ValueError, match="File is not a PDF"):
            extractor.extract_text(str(text_file))


class TestTextExtractorTextProcessing:
    """Test TextExtractor text processing methods."""

    @pytest.fixture
    def extractor(self):
        """Create a TextExtractor instance for testing."""
        return TextExtractor()

    def test_clean_text_basic(self, extractor):
        """Test basic text cleaning."""
        raw_text = "  This   is   a   test   text  \n\n\n"
        result = extractor._clean_text(raw_text)

        assert result == "This is a test text"

    def test_clean_text_with_special_characters(self, extractor):
        """Test text cleaning with special characters."""
        raw_text = "Invoice #123\nTotal: $1,234.56\nDate: 2023-01-15"
        result = extractor._clean_text(raw_text)

        assert result == "Invoice #123 Total: $1,234.56 Date: 2023-01-15"

    def test_clean_text_empty(self, extractor):
        """Test text cleaning with empty text."""
        result = extractor._clean_text("")
        assert result == ""

    def test_clean_text_whitespace_only(self, extractor):
        """Test text cleaning with whitespace-only text."""
        result = extractor._clean_text("   \n\t   ")
        assert result == ""

    def test_is_text_sufficient_true(self, extractor):
        """Test text sufficiency check with sufficient text."""
        text = "This is a sufficient amount of text for extraction"
        result = extractor._is_text_sufficient(text)
        assert result is True

    def test_is_text_sufficient_false(self, extractor):
        """Test text sufficiency check with insufficient text."""
        text = "Short"
        result = extractor._is_text_sufficient(text)
        assert result is False

    def test_is_text_sufficient_empty(self, extractor):
        """Test text sufficiency check with empty text."""
        result = extractor._is_text_sufficient("")
        assert result is False


class TestTextExtractorErrorHandling:
    """Test TextExtractor error handling and recovery."""

    @pytest.fixture
    def extractor(self):
        """Create a TextExtractor instance for testing."""
        return TextExtractor()

    def test_handle_extraction_error_with_retry(self, extractor, tmp_path):
        """Test extraction error handling with retry mechanism."""
        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_text("dummy content")

        with patch.object(extractor, "_extract_with_pdfplumber") as mock_pdfplumber:
            mock_pdfplumber.side_effect = [
                Exception("First failure"),
                Exception("Second failure"),
                "Success on third try",
            ]

            result = extractor.extract_text(str(pdf_file), max_retries=3)

            assert result == "Success on third try"
            assert mock_pdfplumber.call_count == 3

    def test_handle_extraction_error_max_retries_exceeded(self, extractor, tmp_path):
        """Test extraction error handling when max retries are exceeded."""
        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_text("dummy content")

        with patch.object(extractor, "_extract_with_pdfplumber") as mock_pdfplumber:
            mock_pdfplumber.side_effect = Exception("Always fails")

            with pytest.raises(Exception, match="Always fails"):
                extractor.extract_text(str(pdf_file), max_retries=2)

            assert mock_pdfplumber.call_count == 2


class TestTextExtractorPerformance:
    """Test TextExtractor performance characteristics."""

    @pytest.fixture
    def extractor(self):
        """Create a TextExtractor instance for testing."""
        return TextExtractor()

    def test_large_pdf_processing(self, extractor, tmp_path):
        """Test processing of large PDF files."""
        # Create a large dummy PDF file
        pdf_file = tmp_path / "large.pdf"
        pdf_file.write_text("x" * 1000000)  # 1MB of content

        with patch.object(extractor, "_extract_with_pdfplumber") as mock_extract:
            mock_extract.return_value = "Large text content"

            result = extractor.extract_text(str(pdf_file))

            assert result == "Large text content"

    def test_multiple_concurrent_requests(self, extractor, tmp_path):
        """Test handling of multiple concurrent extraction requests."""
        import threading

        results = []
        errors = []

        def extraction_worker():
            try:
                pdf_file = tmp_path / f"test_{threading.current_thread().name}.pdf"
                pdf_file.write_text("dummy content")

                with patch.object(
                    extractor, "_extract_with_pdfplumber"
                ) as mock_extract:
                    mock_extract.return_value = (
                        f"Result {threading.current_thread().name}"
                    )
                    result = extractor.extract_text(str(pdf_file))
                    results.append(result)
            except Exception as e:
                errors.append(e)

        threads = []
        for i in range(5):
            thread = threading.Thread(target=extraction_worker)
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        assert len(results) == 5
        assert len(errors) == 0


class TestTextExtractorIntegration:
    """Integration tests for TextExtractor."""

    @pytest.fixture
    def extractor(self):
        """Create a TextExtractor instance for testing."""
        return TextExtractor()

    def test_full_extraction_workflow(self, extractor, tmp_path):
        """Test complete text extraction workflow."""
        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_text("dummy content")

        with patch.object(extractor, "_extract_with_pdfplumber") as mock_extract:
            mock_extract.return_value = "Sample invoice text"

            result = extractor.extract_text(str(pdf_file))

            assert result == "Sample invoice text"
            mock_extract.assert_called_once_with(str(pdf_file))

    def test_extraction_with_text_cleaning(self, extractor, tmp_path):
        """Test text extraction with cleaning workflow."""
        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_text("dummy content")

        with patch.object(extractor, "_extract_with_pdfplumber") as mock_extract:
            mock_extract.return_value = "  Raw   text   with   extra   spaces  \n\n"

            result = extractor.extract_text(str(pdf_file))

            assert result == "Raw text with extra spaces"
            mock_extract.assert_called_once_with(str(pdf_file))
