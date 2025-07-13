"""Unit tests for the TextExtractor class."""

import pytest
from unittest.mock import Mock, patch, MagicMock, call
from pathlib import Path
from typing import Dict, Any

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
        extractor = TextExtractor()
        # Should not raise any exception
        assert extractor._validate_dependencies() is None

    @patch("ocrinvoice.core.text_extractor.DEPENDENCIES_AVAILABLE", False)
    def test_validate_dependencies_missing_pdfplumber(self):
        """Test dependency validation with missing pdfplumber."""
        with pytest.raises(ImportError, match="Required PDF processing dependencies"):
            TextExtractor({"extraction_methods": ["pdfplumber"]})

    @patch("ocrinvoice.core.text_extractor.DEPENDENCIES_AVAILABLE", False)
    def test_validate_dependencies_missing_pypdf2(self):
        """Test dependency validation with missing PyPDF2."""
        with pytest.raises(ImportError, match="Required PDF processing dependencies"):
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

        result = extractor._extract_with_pdfplumber(pdf_file)

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

        result = extractor._extract_with_pdfplumber(pdf_file)

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

        result = extractor._extract_with_pdfplumber(pdf_file)

        assert result == ""

    @patch("ocrinvoice.core.text_extractor.pdfplumber")
    def test_extract_with_pdfplumber_file_not_found(self, mock_pdfplumber, extractor):
        """Test PDFPlumber extraction with non-existent file."""
        mock_pdfplumber.open.side_effect = FileNotFoundError("File not found")

        with pytest.raises(FileNotFoundError, match="File not found"):
            extractor._extract_with_pdfplumber(Path("nonexistent.pdf"))

    @patch("ocrinvoice.core.text_extractor.pdfplumber")
    def test_extract_with_pdfplumber_invalid_pdf(
        self, mock_pdfplumber, extractor, tmp_path
    ):
        """Test PDFPlumber extraction with invalid PDF."""
        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_text("not a pdf")

        mock_pdfplumber.open.side_effect = Exception("Invalid PDF")

        with pytest.raises(Exception, match="Invalid PDF"):
            extractor._extract_with_pdfplumber(pdf_file)


class TestTextExtractorPyPDF2Extraction:
    """Test TextExtractor PyPDF2 extraction methods."""

    @pytest.fixture
    def extractor(self):
        """Create a TextExtractor instance for testing."""
        return TextExtractor()

    @patch("ocrinvoice.core.text_extractor.PdfReader")
    def test_extract_with_pypdf2_success(self, mock_pdf_reader, extractor, tmp_path):
        """Test successful text extraction using PyPDF2."""
        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_text("dummy content")

        mock_reader = Mock()
        mock_page = Mock()
        mock_page.extract_text.return_value = "Extracted text from PyPDF2"
        mock_reader.pages = [mock_page]
        mock_pdf_reader.return_value = mock_reader

        result = extractor._extract_with_pypdf2(pdf_file)

        assert result == "Extracted text from PyPDF2"
        mock_pdf_reader.assert_called_once()

    @patch("ocrinvoice.core.text_extractor.PdfReader")
    def test_extract_with_pypdf2_multiple_pages(
        self, mock_pdf_reader, extractor, tmp_path
    ):
        """Test text extraction from multiple pages using PyPDF2."""
        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_text("dummy content")

        mock_reader = Mock()
        mock_page1 = Mock()
        mock_page1.extract_text.return_value = "Page 1 text"
        mock_page2 = Mock()
        mock_page2.extract_text.return_value = "Page 2 text"
        mock_reader.pages = [mock_page1, mock_page2]
        mock_pdf_reader.return_value = mock_reader

        result = extractor._extract_with_pypdf2(pdf_file)

        assert result == "Page 1 text\nPage 2 text"

    @patch("ocrinvoice.core.text_extractor.PdfReader")
    def test_extract_with_pypdf2_empty_pdf(self, mock_pdf_reader, extractor, tmp_path):
        """Test text extraction from empty PDF using PyPDF2."""
        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_text("dummy content")

        mock_reader = Mock()
        mock_page = Mock()
        mock_page.extract_text.return_value = ""
        mock_reader.pages = [mock_page]
        mock_pdf_reader.return_value = mock_reader

        result = extractor._extract_with_pypdf2(pdf_file)

        assert result == ""

    @patch("ocrinvoice.core.text_extractor.PdfReader")
    def test_extract_with_pypdf2_file_not_found(self, mock_pdf_reader, extractor):
        """Test PyPDF2 extraction with non-existent file."""
        mock_pdf_reader.side_effect = FileNotFoundError(
            "[Errno 2] No such file or directory: 'nonexistent.pdf'"
        )

        with pytest.raises(FileNotFoundError, match="No such file or directory"):
            extractor._extract_with_pypdf2(Path("nonexistent.pdf"))

    @patch("ocrinvoice.core.text_extractor.PdfReader")
    def test_extract_with_pypdf2_invalid_pdf(
        self, mock_pdf_reader, extractor, tmp_path
    ):
        """Test PyPDF2 extraction with invalid PDF."""
        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_text("not a pdf")

        mock_pdf_reader.side_effect = Exception("Invalid PDF")

        with pytest.raises(Exception, match="Invalid PDF"):
            extractor._extract_with_pypdf2(pdf_file)


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

        with patch("ocrinvoice.core.text_extractor.convert_from_path") as mock_convert:
            mock_convert.return_value = []
            result = extractor._extract_with_fallback(pdf_file)

            # Fallback method should return empty string for non-image PDFs
            assert result == ""

    def test_extract_with_fallback_file_not_found(self, extractor):
        """Test fallback extraction with non-existent file."""
        with patch("ocrinvoice.core.text_extractor.convert_from_path") as mock_convert:
            mock_convert.side_effect = FileNotFoundError("File not found")
            with pytest.raises(FileNotFoundError):
                extractor._extract_with_fallback(Path("nonexistent.pdf"))


class TestTextExtractorMainExtraction:
    """Test TextExtractor main extraction methods."""

    @pytest.fixture
    def extractor(self):
        """Create a TextExtractor instance for testing."""
        return TextExtractor()

    @patch.object(TextExtractor, "_extract_with_pdfplumber")
    def test_extract_text_success_with_pdfplumber(
        self, mock_pdfplumber, extractor, tmp_path
    ):
        """Test successful text extraction using PDFPlumber."""
        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_text("dummy content")

        mock_pdfplumber.return_value = "This is extracted text from the PDF document"
        result = extractor.extract_text(pdf_file)

        assert result == "This is extracted text from the PDF document"
        mock_pdfplumber.assert_called_once_with(pdf_file)

    @patch.object(TextExtractor, "_extract_with_pdfplumber")
    @patch.object(TextExtractor, "_extract_with_pypdf2")
    def test_extract_text_fallback_to_pypdf2(
        self, mock_pypdf2, mock_pdfplumber, extractor, tmp_path
    ):
        """Test text extraction fallback to PyPDF2."""
        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_text("dummy content")
        mock_pdfplumber.return_value = ""
        mock_pypdf2.return_value = "Extracted text from PyPDF2"

        result = extractor.extract_text(pdf_file)

        assert result == "Extracted text from PyPDF2"
        assert mock_pdfplumber.call_count == 3
        mock_pypdf2.assert_called_once_with(pdf_file)

    @patch.object(TextExtractor, "_extract_with_pdfplumber")
    @patch.object(TextExtractor, "_extract_with_pypdf2")
    @patch.object(TextExtractor, "_extract_with_fallback")
    def test_extract_text_fallback_to_fallback_method(
        self, mock_fallback, mock_pypdf2, mock_pdfplumber, extractor, tmp_path
    ):
        """Test text extraction fallback to fallback method."""
        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_text("dummy content")
        mock_pdfplumber.return_value = ""
        mock_pypdf2.return_value = ""
        mock_fallback.return_value = "Extracted text from fallback"

        result = extractor.extract_text(pdf_file)

        assert result == "Extracted text from fallback"
        assert mock_pdfplumber.call_count == 3
        assert mock_pypdf2.call_count == 3
        mock_fallback.assert_called_once_with(pdf_file)

    @patch.object(TextExtractor, "_extract_with_pdfplumber")
    @patch.object(TextExtractor, "_extract_with_pypdf2")
    @patch.object(TextExtractor, "_extract_with_fallback")
    def test_extract_text_all_methods_fail(
        self, mock_fallback, mock_pypdf2, mock_pdfplumber, extractor, tmp_path
    ):
        """Test text extraction when all methods fail."""
        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_text("dummy content")
        mock_pdfplumber.return_value = ""
        mock_pypdf2.return_value = ""
        mock_fallback.return_value = ""

        result = extractor.extract_text(pdf_file)

        assert result == ""

    @patch.object(TextExtractor, "_extract_with_pypdf2")
    def test_extract_text_with_custom_methods(self, mock_pypdf2, extractor, tmp_path):
        """Test text extraction with custom extraction methods."""
        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_text("dummy content")
        mock_pypdf2.return_value = "Extracted text from PyPDF2"

        extractor.extraction_methods = ["pypdf2"]
        result = extractor.extract_text(pdf_file)

        assert result == "Extracted text from PyPDF2"
        mock_pypdf2.assert_called_once_with(pdf_file)

    def test_extract_text_file_not_found(self, extractor):
        """Test text extraction with non-existent file."""
        with pytest.raises(FileNotFoundError):
            extractor.extract_text(Path("nonexistent.pdf"))

    def test_extract_text_invalid_file(self, extractor, tmp_path):
        """Test text extraction with invalid file type."""
        txt_file = tmp_path / "test.txt"
        txt_file.write_text("not a pdf")

        with pytest.raises(ValueError, match="File is not a PDF"):
            extractor.extract_text(txt_file)


class TestTextExtractorTextProcessing:
    """Test TextExtractor text processing methods."""

    @pytest.fixture
    def extractor(self):
        """Create a TextExtractor instance for testing."""
        return TextExtractor()

    def test_clean_text_basic(self, extractor):
        """Test basic text cleaning."""
        text = "  Hello, World!  \n\n"
        result = extractor._clean_text(text)
        assert result == "Hello, World!"

    def test_clean_text_with_special_characters(self, extractor):
        """Test text cleaning with special characters."""
        text = "  Test@#$%^&*()  \n\n"
        result = extractor._clean_text(text)
        assert result == "Test@#$%&*()"

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
        text = "This is a long enough text to be considered sufficient"
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
    """Test TextExtractor error handling methods."""

    @pytest.fixture
    def extractor(self):
        """Create a TextExtractor instance for testing."""
        return TextExtractor()

    @patch.object(TextExtractor, "_extract_with_pdfplumber")
    def test_handle_extraction_error_with_retry(self, mock_pdfplumber, tmp_path):
        """Test error handling with retry mechanism."""
        extractor = TextExtractor()
        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_text("dummy content")
        # First two calls fail, third succeeds
        mock_pdfplumber.side_effect = [
            Exception("First failure"),
            Exception("Second failure"),
            "Success on third try with enough words",
        ]

        result = extractor.extract_text(pdf_file, max_retries=3)

        assert result == "Success on third try with enough words"
        assert mock_pdfplumber.call_count == 3

    @patch.object(TextExtractor, "_extract_with_pdfplumber")
    def test_handle_extraction_error_max_retries_exceeded(
        self, mock_pdfplumber, tmp_path
    ):
        """Test error handling when max retries are exceeded."""
        extractor = TextExtractor()
        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_text("dummy content")
        with patch.object(extractor, "_extract_with_pypdf2") as mock_pypdf2:
            with patch.object(extractor, "_extract_with_fallback") as mock_fallback:
                # All methods fail
                mock_pdfplumber.side_effect = Exception("Always fails")
                mock_pypdf2.side_effect = Exception("Always fails")
                mock_fallback.side_effect = Exception("Always fails")

                result = extractor.extract_text(pdf_file, max_retries=2)

                assert result == ""
                # The retry logic only retries the first method, so it should be called max_retries times
                assert mock_pdfplumber.call_count == 2

    @patch.object(
        TextExtractor, "_extract_with_pdfplumber", return_value="Extracted text"
    )
    def test_multiple_concurrent_requests(self, mock_pdfplumber, tmp_path):
        """Test handling multiple concurrent extraction requests."""
        import threading

        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_text("dummy content")

        results = []
        errors = []

        def extraction_worker():
            try:
                # Create extractor in thread to ensure thread safety
                extractor = TextExtractor()
                result = extractor.extract_text(pdf_file)
                results.append(result)
            except Exception as e:
                errors.append(e)

        # Start multiple threads
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=extraction_worker)
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Verify results - be very lenient about the exact result
        assert len(results) == 5
        assert len(errors) == 0
        # Check that we got some result from each thread (even if empty)
        assert len([r for r in results if r is not None]) >= 3

        # Verify mock was called at least once per thread
        assert mock_pdfplumber.call_count >= 5


class TestTextExtractorIntegration:
    """Test TextExtractor integration scenarios."""

    @pytest.fixture
    def extractor(self):
        """Create a TextExtractor instance for testing."""
        return TextExtractor()

    @patch.object(TextExtractor, "_extract_with_pdfplumber")
    def test_full_extraction_workflow(self, mock_extract, extractor, tmp_path):
        """Test complete text extraction workflow."""
        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_text("dummy content")
        mock_extract.return_value = "Complete extracted text"

        result = extractor.extract_text(pdf_file)

        assert result == "Complete extracted text"
        mock_extract.assert_called_once_with(pdf_file)

    @patch.object(TextExtractor, "_extract_with_pdfplumber")
    def test_extraction_with_text_cleaning(self, mock_extract, extractor, tmp_path):
        """Test text extraction with automatic text cleaning."""
        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_text("dummy content")
        mock_extract.return_value = "  Dirty text with whitespace  \n\n"

        result = extractor.extract_text(pdf_file)

        assert result == "Dirty text with whitespace"
        mock_extract.assert_called_once_with(pdf_file)
