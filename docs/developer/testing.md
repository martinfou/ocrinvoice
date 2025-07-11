# Testing Guide

This guide covers testing practices, tools, and standards for the Invoice OCR Parser project.

## 🧪 Testing Overview

### Testing Philosophy

- **Comprehensive Coverage**: Aim for 90%+ test coverage
- **Quality Assurance**: Tests ensure code quality and prevent regressions
- **Documentation**: Tests serve as living documentation
- **Confidence**: Tests provide confidence for refactoring and changes

### Testing Pyramid

```
    /\
   /  \     E2E Tests (Few)
  /____\    Integration Tests (Some)
 /______\   Unit Tests (Many)
```

- **Unit Tests**: Test individual functions and classes
- **Integration Tests**: Test component interactions
- **End-to-End Tests**: Test complete workflows

## 🛠️ Testing Tools

### Core Testing Framework

- **pytest**: Primary testing framework
- **pytest-cov**: Coverage reporting
- **pytest-mock**: Mocking and patching
- **pytest-parametrize**: Parameterized testing

### Additional Tools

- **coverage**: Code coverage analysis
- **tox**: Multi-environment testing
- **pre-commit**: Automated quality checks

## 📁 Test Structure

### Directory Organization

```
tests/
├── unit/                        # Unit tests
│   ├── test_cli/                # CLI command tests
│   ├── test_core/               # Core functionality tests
│   ├── test_parsers/            # Parser tests
│   ├── test_utils/              # Utility tests
│   └── test_business/           # Business logic tests
├── integration/                 # Integration tests
├── fixtures/                    # Test data and fixtures
│   ├── sample_invoice.pdf       # Sample invoice for testing
│   ├── expected_results.json    # Expected test results
│   └── config/                  # Test configuration files
└── conftest.py                  # Pytest configuration and fixtures
```

### Test File Naming

- **Unit Tests**: `test_<module_name>.py`
- **Integration Tests**: `test_integration_<feature>.py`
- **Fixtures**: Descriptive names with appropriate extensions

## 🧩 Unit Testing

### Test Class Structure

```python
import pytest
from pathlib import Path
from ocrinvoice.parsers.invoice_parser import InvoiceParser


class TestInvoiceParser:
    """Test cases for InvoiceParser class."""

    def setup_method(self):
        """Set up test fixtures for each test method."""
        self.parser = InvoiceParser()
        self.test_file = Path("tests/fixtures/sample_invoice.pdf")

    def teardown_method(self):
        """Clean up after each test method."""
        # Cleanup code here
        pass

    def test_parse_invoice_success(self):
        """Test successful invoice parsing."""
        # Arrange
        expected_fields = ["company", "total", "date", "confidence"]

        # Act
        result = self.parser.parse(self.test_file)

        # Assert
        assert result["success"] is True
        for field in expected_fields:
            assert field in result
        assert isinstance(result["confidence"], float)
        assert 0.0 <= result["confidence"] <= 1.0

    def test_parse_invoice_file_not_found(self):
        """Test parsing with non-existent file."""
        # Arrange
        non_existent_file = "non_existent_file.pdf"

        # Act & Assert
        with pytest.raises(FileNotFoundError):
            self.parser.parse(non_existent_file)

    @pytest.mark.parametrize("confidence_threshold,expected_success", [
        (0.5, True),
        (0.9, False),
        (0.0, True),
        (1.0, False),
    ])
    def test_parse_with_confidence_threshold(self, confidence_threshold, expected_success):
        """Test parsing with different confidence thresholds."""
        # Arrange
        self.parser.confidence_threshold = confidence_threshold

        # Act
        result = self.parser.parse(self.test_file)

        # Assert
        assert result["success"] == expected_success
```

### Test Method Naming

Use descriptive test method names that explain what is being tested:

```python
def test_extract_company_name_with_valid_input(self):
    """Test company name extraction with valid input."""

def test_extract_company_name_with_empty_input(self):
    """Test company name extraction with empty input."""

def test_extract_company_name_with_ocr_errors(self):
    """Test company name extraction with OCR errors."""

def test_extract_total_amount_with_currency_symbol(self):
    """Test total amount extraction with currency symbol."""

def test_extract_total_amount_with_decimal_comma(self):
    """Test total amount extraction with decimal comma format."""
```

### Assertion Best Practices

```python
# Use specific assertions
assert result["success"] is True  # Instead of assert result["success"]
assert len(items) == 3  # Instead of assert len(items) > 0

# Use descriptive assertion messages
assert result["company"] == "HYDRO-QUÉBEC", f"Expected 'HYDRO-QUÉBEC', got '{result['company']}'"

# Test for exceptions
with pytest.raises(ValueError, match="Invalid amount format"):
    parser.extract_total("invalid_amount")

# Test for specific exception types
with pytest.raises(FileNotFoundError):
    parser.parse("non_existent_file.pdf")
```

## 🔗 Integration Testing

### Integration Test Structure

```python
import pytest
from pathlib import Path
from ocrinvoice.cli.main import main


class TestCLIIntegration:
    """Integration tests for CLI functionality."""

    def test_parse_command_integration(self, tmp_path, capsys):
        """Test complete parse command workflow."""
        # Arrange
        output_file = tmp_path / "result.json"

        # Act
        result = main([
            "parse",
            "tests/fixtures/sample_invoice.pdf",
            "--output", str(output_file)
        ])

        # Assert
        assert result == 0  # Exit code 0 indicates success
        assert output_file.exists()

        # Check output content
        captured = capsys.readouterr()
        assert "company" in captured.out
        assert "total" in captured.out

    def test_batch_command_integration(self, tmp_path):
        """Test complete batch command workflow."""
        # Arrange
        output_file = tmp_path / "batch_results.csv"

        # Act
        result = main([
            "batch",
            "tests/fixtures/",
            "--output", str(output_file)
        ])

        # Assert
        assert result == 0
        assert output_file.exists()

        # Check CSV content
        with open(output_file) as f:
            content = f.read()
            assert "company,total,date" in content
```

### End-to-End Testing

```python
class TestEndToEnd:
    """End-to-end tests for complete workflows."""

    def test_complete_invoice_processing_workflow(self, tmp_path):
        """Test complete invoice processing from PDF to structured data."""
        # Arrange
        input_file = "tests/fixtures/sample_invoice.pdf"
        output_file = tmp_path / "processed.json"

        # Act - Simulate complete user workflow
        # 1. Parse invoice
        parse_result = main(["parse", input_file, "--output", str(output_file)])

        # 2. Verify output
        assert parse_result == 0
        assert output_file.exists()

        # 3. Check output format
        import json
        with open(output_file) as f:
            data = json.load(f)

        # Assert
        assert "company" in data
        assert "total" in data
        assert "date" in data
        assert "confidence" in data
        assert data["success"] is True
```

## 🎭 Mocking and Patching

### Mocking External Dependencies

```python
import pytest
from unittest.mock import Mock, patch, MagicMock
from ocrininvoice.core.ocr_engine import OCREngine


class TestOCREngine:
    """Test cases for OCR engine with mocked dependencies."""

    @patch('ocrinvoice.core.ocr_engine.pytesseract')
    def test_extract_text_with_mocked_tesseract(self, mock_tesseract):
        """Test OCR text extraction with mocked Tesseract."""
        # Arrange
        mock_tesseract.image_to_string.return_value = "Mocked OCR text"
        engine = OCREngine()

        # Act
        result = engine.extract_text("fake_image.png")

        # Assert
        assert result == "Mocked OCR text"
        mock_tesseract.image_to_string.assert_called_once()

    @patch('ocrinvoice.core.ocr_engine.pdfplumber')
    def test_extract_text_with_mocked_pdfplumber(self, mock_pdfplumber):
        """Test PDF text extraction with mocked pdfplumber."""
        # Arrange
        mock_pdf = Mock()
        mock_pdf.pages = [Mock()]
        mock_pdf.pages[0].extract_text.return_value = "Mocked PDF text"
        mock_pdfplumber.open.return_value.__enter__.return_value = mock_pdf

        # Act
        from ocrininvoice.core.text_extractor import TextExtractor
        extractor = TextExtractor()
        result = extractor.extract_text("fake_file.pdf")

        # Assert
        assert "Mocked PDF text" in result
```

### Mocking File System Operations

```python
import pytest
from unittest.mock import patch, mock_open
from pathlib import Path


class TestFileOperations:
    """Test file operations with mocked file system."""

    @patch('builtins.open', new_callable=mock_open, read_data='{"test": "data"}')
    def test_load_config_from_file(self, mock_file):
        """Test configuration loading from file."""
        # Arrange
        from ocrininvoice.config import ConfigManager

        # Act
        config = ConfigManager()
        result = config.load_from_file("fake_config.json")

        # Assert
        assert result["test"] == "data"
        mock_file.assert_called_once_with("fake_config.json", "r")

    @patch('pathlib.Path.exists')
    def test_file_validation(self, mock_exists):
        """Test file existence validation."""
        # Arrange
        mock_exists.return_value = False

        # Act & Assert
        with pytest.raises(FileNotFoundError):
            # Your file validation code here
            pass
```

## 📊 Coverage Testing

### Coverage Configuration

Create a `.coveragerc` file:

```ini
[run]
source = src/ocrinvoice
omit =
    */tests/*
    */__pycache__/*
    */venv/*
    setup.py

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
    if 0:
    if __name__ == .__main__.:
    class .*\bProtocol\):
    @(abc\.)?abstractmethod
```

### Running Coverage Tests

```bash
# Run tests with coverage
pytest --cov=src/ocrinvoice --cov-report=term-missing

# Generate HTML coverage report
pytest --cov=src/ocrinvoice --cov-report=html

# Generate XML coverage report for CI
pytest --cov=src/ocrinvoice --cov-report=xml

# Check minimum coverage threshold
pytest --cov=src/ocrinvoice --cov-fail-under=90
```

### Coverage Analysis

```python
# In your test code, you can check coverage of specific functions
def test_specific_function_coverage(self):
    """Test that specific function is fully covered."""
    # This test ensures the function is called
    result = some_function()
    assert result is not None
```

## 🔄 Parameterized Testing

### Using pytest.mark.parametrize

```python
import pytest


class TestAmountNormalizer:
    """Test cases for amount normalization."""

    @pytest.mark.parametrize("input_amount,expected", [
        ("$123.45", "123.45"),
        ("123,45", "123.45"),
        ("123.45", "123.45"),
        ("$1,234.56", "1234.56"),
        ("1.234,56", "1234.56"),
    ])
    def test_normalize_amount_formats(self, input_amount, expected):
        """Test amount normalization with different formats."""
        # Arrange
        from ocrininvoice.utils.amount_normalizer import AmountNormalizer
        normalizer = AmountNormalizer()

        # Act
        result = normalizer.normalize_amount(input_amount)

        # Assert
        assert result == expected

    @pytest.mark.parametrize("input_text,expected_company", [
        ("HYDRO-QUÉBEC Invoice", "HYDRO-QUÉBEC"),
        ("Invoice from Hydro Quebec", "HYDRO-QUÉBEC"),
        ("Hydro-Quebec Services", "HYDRO-QUÉBEC"),
        ("Unknown Company Invoice", "Unknown"),
    ])
    def test_extract_company_variations(self, input_text, expected_company):
        """Test company extraction with various input formats."""
        # Arrange
        from ocrininvoice.parsers.invoice_parser import InvoiceParser
        parser = InvoiceParser()

        # Act
        result = parser.extract_company(input_text)

        # Assert
        assert result == expected_company
```

## 🧪 Test Fixtures

### Pytest Fixtures

```python
import pytest
from pathlib import Path
from ocrininvoice.parsers.invoice_parser import InvoiceParser


@pytest.fixture
def sample_invoice_parser():
    """Provide a configured invoice parser for testing."""
    parser = InvoiceParser()
    parser.confidence_threshold = 0.7
    return parser


@pytest.fixture
def sample_pdf_file():
    """Provide a sample PDF file for testing."""
    return Path("tests/fixtures/sample_invoice.pdf")


@pytest.fixture
def mock_ocr_engine():
    """Provide a mocked OCR engine for testing."""
    with patch('ocrinvoice.core.ocr_engine.OCREngine') as mock:
        mock.return_value.extract_text.return_value = "Mocked OCR text"
        yield mock


class TestWithFixtures:
    """Test cases using fixtures."""

    def test_parse_with_fixtures(self, sample_invoice_parser, sample_pdf_file):
        """Test parsing using fixtures."""
        # Act
        result = sample_invoice_parser.parse(sample_pdf_file)

        # Assert
        assert result["success"] is True

    def test_ocr_integration(self, sample_invoice_parser, mock_ocr_engine):
        """Test OCR integration using mocked engine."""
        # Act
        result = sample_invoice_parser.parse("fake_file.pdf")

        # Assert
        assert "Mocked OCR text" in result.get("raw_text", "")
```

## 🚀 Performance Testing

### Performance Test Structure

```python
import pytest
import time
from pathlib import Path


class TestPerformance:
    """Performance tests for critical functions."""

    def test_parse_performance(self):
        """Test that parsing completes within acceptable time."""
        # Arrange
        from ocrininvoice.parsers.invoice_parser import InvoiceParser
        parser = InvoiceParser()
        test_file = Path("tests/fixtures/sample_invoice.pdf")

        # Act
        start_time = time.time()
        result = parser.parse(test_file)
        end_time = time.time()

        # Assert
        processing_time = end_time - start_time
        assert processing_time < 5.0  # Should complete within 5 seconds
        assert result["success"] is True

    def test_batch_processing_performance(self):
        """Test batch processing performance."""
        # Arrange
        from ocrininvoice.cli.commands.batch import BatchCommand
        command = BatchCommand()

        # Act
        start_time = time.time()
        result = command.process_directory("tests/fixtures/", "test_output.csv")
        end_time = time.time()

        # Assert
        processing_time = end_time - start_time
        assert processing_time < 30.0  # Should complete within 30 seconds
        assert result["success"] is True
```

## 🔍 Debugging Tests

### Debugging Failed Tests

```python
# Add debugging output to tests
def test_debug_example(self):
    """Example test with debugging output."""
    # Arrange
    parser = InvoiceParser()

    # Act
    result = parser.parse("test_file.pdf")

    # Debug output
    print(f"Result: {result}")
    print(f"Result type: {type(result)}")
    print(f"Result keys: {result.keys() if isinstance(result, dict) else 'Not a dict'}")

    # Assert
    assert result["success"] is True
```

### Using pytest.set_trace()

```python
def test_with_breakpoint(self):
    """Test with debugging breakpoint."""
    # Arrange
    parser = InvoiceParser()

    # Act
    result = parser.parse("test_file.pdf")

    # Debug breakpoint
    pytest.set_trace()  # This will pause execution for debugging

    # Assert
    assert result["success"] is True
```

## 📋 Test Checklist

### Before Running Tests

- [ ] Virtual environment is activated
- [ ] Dependencies are installed (`pip install -e ".[dev]"`)
- [ ] Tesseract OCR is installed and accessible
- [ ] Test fixtures are available

### Running Tests

```bash
# Run all tests
pytest

# Run tests with verbose output
pytest -v

# Run tests with coverage
pytest --cov=src/ocrinvoice

# Run specific test file
pytest tests/unit/test_parsers/test_invoice_parser.py

# Run specific test method
pytest tests/unit/test_parsers/test_invoice_parser.py::TestInvoiceParser::test_parse_invoice_success

# Run tests in parallel (if pytest-xdist is installed)
pytest -n auto

# Run tests and stop on first failure
pytest -x

# Run tests and show local variables on failure
pytest -l
```

### Quality Checks

```bash
# Run all quality checks
pre-commit run --all-files

# Run specific checks
black src/ tests/
flake8 src/ tests/
mypy src/
```

## 🎯 Best Practices

### Test Organization

1. **Group Related Tests**: Use test classes to group related tests
2. **Descriptive Names**: Use clear, descriptive test method names
3. **Arrange-Act-Assert**: Follow the AAA pattern for test structure
4. **One Assertion Per Test**: Focus each test on one specific behavior

### Test Data Management

1. **Use Fixtures**: Create reusable test data with fixtures
2. **Minimal Test Data**: Use the smallest amount of data needed
3. **Clean Test Data**: Ensure test data is cleaned up after tests
4. **Realistic Data**: Use realistic test data that represents actual use cases

### Test Maintenance

1. **Keep Tests Simple**: Write simple, focused tests
2. **Avoid Test Interdependence**: Tests should not depend on each other
3. **Update Tests with Code**: Update tests when code changes
4. **Review Test Coverage**: Regularly review and improve test coverage

---

*For more information about testing, see the [Development Setup Guide](./development_setup.md) and [Contributing Guidelines](./contributing.md).*
