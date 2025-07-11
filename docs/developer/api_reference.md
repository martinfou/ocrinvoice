# API Reference

This document provides a comprehensive reference for the Invoice OCR Parser internal APIs.

## 📚 Overview

The Invoice OCR Parser provides a modular API architecture with clear separation of concerns:

- **Core Modules**: Text extraction, OCR processing, image preprocessing
- **Parser Modules**: Document-specific parsing logic
- **Utility Modules**: Helper functions and utilities
- **Business Logic**: Business rules and data management
- **CLI Interface**: Command-line interface components

## 🏗️ Core API Modules

### Text Extractor (`src/ocrinvoice/core/text_extractor.py`)

The TextExtractor class handles text extraction from PDF documents.

#### Class: `TextExtractor`

```python
class TextExtractor:
    """Extract text from PDF documents using multiple strategies."""

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize the text extractor.

        Args:
            config: Configuration dictionary
        """
```

#### Methods

##### `extract_text(pdf_path: Union[str, Path], max_retries: int = 3) -> str`

Extract text from a PDF file using multiple strategies.

**Parameters:**
- `pdf_path`: Path to the PDF file
- `max_retries`: Maximum number of retry attempts

**Returns:**
- Extracted text string

**Raises:**
- `FileNotFoundError`: If the PDF file doesn't exist
- `ValueError`: If the PDF file is invalid

**Example:**
```python
from ocrinvoice.core.text_extractor import TextExtractor

extractor = TextExtractor()
text = extractor.extract_text("invoice.pdf")
print(f"Extracted {len(text)} characters")
```

##### `extract_text_by_page(pdf_path: Union[str, Path]) -> List[str]`

Extract text from each page separately.

**Parameters:**
- `pdf_path`: Path to the PDF file

**Returns:**
- List of text strings, one per page

**Example:**
```python
extractor = TextExtractor()
pages_text = extractor.extract_text_by_page("invoice.pdf")
for i, page_text in enumerate(pages_text):
    print(f"Page {i+1}: {len(page_text)} characters")
```

##### `is_text_based_pdf(pdf_path: Union[str, Path]) -> bool`

Check if PDF contains extractable text.

**Parameters:**
- `pdf_path`: Path to the PDF file

**Returns:**
- True if PDF contains text, False if image-based

**Example:**
```python
extractor = TextExtractor()
if extractor.is_text_based_pdf("invoice.pdf"):
    print("PDF contains native text")
else:
    print("PDF requires OCR processing")
```

### OCR Engine (`src/ocrinvoice/core/ocr_engine.py`)

The OCREngine class interfaces with Tesseract OCR for text recognition.

#### Class: `OCREngine`

```python
class OCREngine:
    """Interface with Tesseract OCR engine for text recognition."""

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize the OCR engine.

        Args:
            config: Configuration dictionary
        """
```

#### Methods

##### `extract_text(image: np.ndarray, config: Optional[str] = None) -> str`

Extract text from an image using OCR.

**Parameters:**
- `image`: Input image as numpy array
- `config`: Optional OCR configuration string

**Returns:**
- Extracted text string

**Example:**
```python
import cv2
from ocrininvoice.core.ocr_engine import OCREngine

engine = OCREngine()
image = cv2.imread("invoice_page.png")
text = engine.extract_text(image)
print(f"OCR extracted: {text}")
```

##### `extract_text_with_confidence(image: np.ndarray) -> Tuple[str, float]`

Extract text with confidence score.

**Parameters:**
- `image`: Input image as numpy array

**Returns:**
- Tuple of (text, confidence_score)

**Example:**
```python
engine = OCREngine()
image = cv2.imread("invoice_page.png")
text, confidence = engine.extract_text_with_confidence(image)
print(f"Text: {text}")
print(f"Confidence: {confidence:.2f}")
```

##### `get_ocr_info() -> Dict[str, Any]`

Get information about the OCR engine.

**Returns:**
- Dictionary with OCR engine information

**Example:**
```python
engine = OCREngine()
info = engine.get_ocr_info()
print(f"Tesseract version: {info['version']}")
print(f"Available languages: {info['languages']}")
```

### Image Processor (`src/ocrinvoice/core/image_processor.py`)

The ImageProcessor class handles image preprocessing for optimal OCR results.

#### Class: `ImageProcessor`

```python
class ImageProcessor:
    """Process images for optimal OCR results."""

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize the image processor.

        Args:
            config: Configuration dictionary
        """
```

#### Methods

##### `preprocess_image(image: np.ndarray, method: str = "standard") -> np.ndarray`

Preprocess an image using the specified method.

**Parameters:**
- `image`: Input image as numpy array
- `method`: Preprocessing method ("standard", "otsu", "enhanced_contrast", "denoised", "morphological")

**Returns:**
- Preprocessed image as numpy array

**Example:**
```python
import cv2
from ocrininvoice.core.image_processor import ImageProcessor

processor = ImageProcessor()
image = cv2.imread("invoice_page.png")
processed = processor.preprocess_image(image, method="enhanced_contrast")
cv2.imwrite("processed.png", processed)
```

##### `convert_pdf_to_images(pdf_path: Union[str, Path], dpi: int = 300) -> List[np.ndarray]`

Convert PDF pages to images.

**Parameters:**
- `pdf_path`: Path to the PDF file
- `dpi`: Resolution for image conversion

**Returns:**
- List of images as numpy arrays

**Example:**
```python
processor = ImageProcessor()
images = processor.convert_pdf_to_images("invoice.pdf", dpi=300)
print(f"Converted {len(images)} pages to images")
```

## 🔍 Parser API Modules

### Base Parser (`src/ocrinvoice/parsers/base_parser.py`)

Abstract base class for all document parsers.

#### Class: `BaseParser`

```python
class BaseParser(ABC):
    """Abstract base class for document parsers."""

    def __init__(self, config: Dict[str, Any]) -> None:
        """Initialize the base parser.

        Args:
            config: Configuration dictionary
        """
```

#### Abstract Methods

##### `parse(pdf_path: Union[str, Path]) -> Dict[str, Any]`

Parse a document and extract structured data.

**Parameters:**
- `pdf_path`: Path to the PDF file

**Returns:**
- Dictionary containing extracted data

**Example:**
```python
from ocrininvoice.parsers.base_parser import BaseParser

class MyParser(BaseParser):
    def parse(self, pdf_path):
        # Implementation here
        return {"success": True, "data": {}}
```

##### `extract_company(text: str) -> Optional[str]`

Extract company name from text.

**Parameters:**
- `text`: Input text

**Returns:**
- Extracted company name or None

##### `extract_total(text: str) -> Optional[str]`

Extract total amount from text.

**Parameters:**
- `text`: Input text

**Returns:**
- Extracted total amount or None

##### `extract_date(text: str) -> Optional[str]`

Extract date from text.

**Parameters:**
- `text`: Input text

**Returns:**
- Extracted date in ISO format or None

#### Concrete Methods

##### `preprocess_text(text: str) -> str`

Preprocess extracted text for parsing.

**Parameters:**
- `text`: Raw extracted text

**Returns:**
- Preprocessed text

**Example:**
```python
parser = MyParser(config)
raw_text = "  Raw   text  with   extra   spaces  "
cleaned_text = parser.preprocess_text(raw_text)
# Result: "Raw text with extra spaces"
```

##### `calculate_confidence(extracted_data: Dict[str, Any], text: str) -> float`

Calculate confidence score for extracted data.

**Parameters:**
- `extracted_data`: Dictionary of extracted data
- `text`: Original text used for extraction

**Returns:**
- Confidence score between 0.0 and 1.0

**Example:**
```python
parser = MyParser(config)
data = {"company": "HYDRO-QUÉBEC", "total": "137.50"}
confidence = parser.calculate_confidence(data, original_text)
print(f"Confidence: {confidence:.2f}")
```

### Invoice Parser (`src/ocrinvoice/parsers/invoice_parser.py`)

Specialized parser for invoice documents.

#### Class: `InvoiceParser`

```python
class InvoiceParser(BaseParser):
    """Specialized parser for invoice documents."""

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize the invoice parser.

        Args:
            config: Configuration dictionary
        """
```

#### Methods

##### `parse(pdf_path: Union[str, Path]) -> Dict[str, Any]`

Parse an invoice and extract structured data.

**Parameters:**
- `pdf_path`: Path to the invoice PDF

**Returns:**
- Dictionary with invoice data:
  - `company`: Company name
  - `total`: Invoice total amount
  - `date`: Invoice date
  - `invoice_number`: Invoice number
  - `confidence`: Extraction confidence
  - `success`: Whether parsing was successful

**Example:**
```python
from ocrininvoice.parsers.invoice_parser import InvoiceParser

parser = InvoiceParser()
result = parser.parse("invoice.pdf")

if result["success"]:
    print(f"Company: {result['company']}")
    print(f"Total: {result['total']}")
    print(f"Date: {result['date']}")
    print(f"Confidence: {result['confidence']:.2f}")
else:
    print("Parsing failed")
```

##### `extract_company_name(text: str) -> str`

Extract company name using multi-pass strategy.

**Parameters:**
- `text`: Input text

**Returns:**
- Extracted company name or "Unknown"

**Example:**
```python
parser = InvoiceParser()
company = parser.extract_company_name("Invoice from HYDRO-QUÉBEC")
print(f"Company: {company}")  # Output: Company: HYDRO-QUÉBEC
```

##### `extract_invoice_total(text: str) -> Optional[str]`

Extract invoice total using multi-strategy approach.

**Parameters:**
- `text`: Input text

**Returns:**
- Extracted total amount or None

**Example:**
```python
parser = InvoiceParser()
total = parser.extract_invoice_total("Total Amount: $137.50")
print(f"Total: {total}")  # Output: Total: 137.50
```

## 🛠️ Utility API Modules

### Fuzzy Matcher (`src/ocrinvoice/utils/fuzzy_matcher.py`)

The FuzzyMatcher class provides fuzzy string matching capabilities.

#### Class: `FuzzyMatcher`

```python
class FuzzyMatcher:
    """Provide fuzzy string matching capabilities."""

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize the fuzzy matcher.

        Args:
            config: Configuration dictionary
        """
```

#### Methods

##### `similarity(str1: str, str2: str) -> float`

Calculate similarity between two strings.

**Parameters:**
- `str1`: First string
- `str2`: Second string

**Returns:**
- Similarity score between 0.0 and 1.0

**Example:**
```python
from ocrininvoice.utils.fuzzy_matcher import FuzzyMatcher

matcher = FuzzyMatcher()
score = matcher.similarity("Hydro Quebec", "HYDRO-QUÉBEC")
print(f"Similarity: {score:.2f}")  # Output: Similarity: 0.85
```

##### `find_best_match(query: str, candidates: List[str]) -> Tuple[Optional[str], float]`

Find the best match for a query among candidates.

**Parameters:**
- `query`: Query string
- `candidates`: List of candidate strings

**Returns:**
- Tuple of (best_match, confidence_score)

**Example:**
```python
matcher = FuzzyMatcher()
candidates = ["HYDRO-QUÉBEC", "ROYAL BANK", "BELL CANADA"]
best_match, confidence = matcher.find_best_match("Hydro Quebec", candidates)
print(f"Best match: {best_match}")  # Output: Best match: HYDRO-QUÉBEC
print(f"Confidence: {confidence:.2f}")
```

##### `normalize_text(text: str) -> str`

Normalize text for better matching.

**Parameters:**
- `text`: Input text

**Returns:**
- Normalized text

**Example:**
```python
matcher = FuzzyMatcher()
normalized = matcher.normalize_text("  HYDRO-QUÉBEC  ")
print(f"Normalized: '{normalized}'")  # Output: Normalized: 'hydroquebec'
```

### Amount Normalizer (`src/ocrinvoice/utils/amount_normalizer.py`)

The AmountNormalizer class handles monetary amount processing and normalization.

#### Class: `AmountNormalizer`

```python
class AmountNormalizer:
    """Normalize and process monetary amounts."""

    def __init__(self, default_currency: str = "USD") -> None:
        """Initialize the amount normalizer.

        Args:
            default_currency: Default currency code
        """
```

#### Methods

##### `normalize_amount(amount_str: str) -> Optional[str]`

Normalize a monetary amount string.

**Parameters:**
- `amount_str`: Raw amount string

**Returns:**
- Normalized amount string or None if invalid

**Example:**
```python
from ocrininvoice.utils.amount_normalizer import AmountNormalizer

normalizer = AmountNormalizer()
amount = normalizer.normalize_amount("$1,234.56")
print(f"Normalized: {amount}")  # Output: Normalized: 1234.56
```

##### `extract_amounts_from_text(text: str) -> List[str]`

Extract all monetary amounts from text.

**Parameters:**
- `text`: Input text

**Returns:**
- List of normalized amount strings

**Example:**
```python
normalizer = AmountNormalizer()
text = "Invoice total: $137.50, Tax: $12.34"
amounts = normalizer.extract_amounts_from_text(text)
print(f"Amounts: {amounts}")  # Output: Amounts: ['137.50', '12.34']
```

##### `validate_amount(amount_str: str) -> bool`

Validate if a string represents a valid monetary amount.

**Parameters:**
- `amount_str`: Amount string to validate

**Returns:**
- True if valid amount, False otherwise

**Example:**
```python
normalizer = AmountNormalizer()
is_valid = normalizer.validate_amount("$123.45")
print(f"Valid: {is_valid}")  # Output: Valid: True
```

### File Manager (`src/ocrinvoice/utils/file_manager.py`)

The FileManager class handles automatic file renaming based on extracted invoice data.

#### Class: `FileManager`

```python
class FileManager:
    """Manage file operations including automatic renaming based on extracted data."""

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize the file manager.

        Args:
            config: Configuration dictionary
        """
```

#### Methods

##### `generate_filename(data: Dict[str, Any], format_template: str = "{date}_{company}_{total}.pdf") -> Optional[str]`

Generate a filename based on extracted data.

**Parameters:**
- `data`: Dictionary containing extracted invoice data
- `format_template`: Template string for filename format

**Returns:**
- Generated filename or None if required data is missing

**Example:**
```python
from ocrinvoice.utils.file_manager import FileManager

manager = FileManager()
data = {
    "date": "2023-01-15",
    "company": "HYDRO-QUÉBEC",
    "total": 137.50
}
filename = manager.generate_filename(data)
print(f"Generated filename: {filename}")  # Output: Generated filename: 2023-01-15_HYDRO-QUÉBEC_137.50.pdf
```

##### `rename_file(original_path: Union[str, Path], new_filename: str, safe_mode: bool = True, dry_run: bool = False) -> bool`

Rename a file with the new filename.

**Parameters:**
- `original_path`: Path to the original file
- `new_filename`: New filename to use
- `safe_mode`: If True, append numbers to avoid conflicts
- `dry_run`: If True, only show what would be done without making changes

**Returns:**
- True if successful, False otherwise

**Example:**
```python
manager = FileManager()
success = manager.rename_file(
    "invoice.pdf",
    "2023-01-15_HYDRO-QUÉBEC_137.50.pdf",
    safe_mode=True,
    dry_run=False
)
print(f"Rename successful: {success}")
```

##### `process_rename(data: Dict[str, Any], file_path: Union[str, Path], config: Optional[Dict[str, Any]] = None) -> bool`

Process file renaming based on extracted data and configuration.

**Parameters:**
- `data`: Dictionary containing extracted invoice data
- `file_path`: Path to the file to rename
- `config`: Optional configuration dictionary

**Returns:**
- True if renaming was successful or not needed, False if failed

**Example:**
```python
manager = FileManager()
data = {
    "date": "2023-01-15",
    "company": "HYDRO-QUÉBEC",
    "total": 137.50
}
success = manager.process_rename(data, "invoice.pdf")
print(f"Process successful: {success}")
```

## 🏢 Business Logic API Modules

### Business Alias Manager (`src/ocrinvoice/business/business_alias_manager.py`)

The BusinessAliasManager class handles business name aliases and matching.

#### Class: `BusinessAliasManager`

```python
class BusinessAliasManager:
    """Manage business name aliases and matching."""

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize the business alias manager.

        Args:
            config: Configuration dictionary
        """
```

#### Methods

##### `add_alias(alias: str, official_name: str) -> None`

Add a business alias mapping.

**Parameters:**
- `alias`: Alias name
- `official_name`: Official business name

**Example:**
```python
from ocrininvoice.business.business_alias_manager import BusinessAliasManager

manager = BusinessAliasManager()
manager.add_alias("Hydro Quebec", "HYDRO-QUÉBEC")
manager.add_alias("RBC Bank", "ROYAL BANK OF CANADA")
```

##### `find_match(text: str) -> Optional[str]`

Find the best business name match for given text.

**Parameters:**
- `text`: Input text to match

**Returns:**
- Matched official business name or None

**Example:**
```python
manager = BusinessAliasManager()
match = manager.find_match("Invoice from Hydro Quebec")
print(f"Match: {match}")  # Output: Match: HYDRO-QUÉBEC
```

##### `list_aliases() -> Dict[str, str]`

List all configured aliases.

**Returns:**
- Dictionary mapping aliases to official names

**Example:**
```python
manager = BusinessAliasManager()
aliases = manager.list_aliases()
for alias, official in aliases.items():
    print(f"{alias} -> {official}")
```

##### `test_matching(text: str) -> str`

Test how a business name would be matched.

**Parameters:**
- `text`: Text to test

**Returns:**
- Description of how the text would be matched

**Example:**
```python
manager = BusinessAliasManager()
result = manager.test_matching("Hydro Quebec Inc")
print(result)  # Output: "Would match 'HYDRO-QUÉBEC' via alias 'Hydro Quebec'"
```

## 🖥️ CLI API Modules

### CLI Main (`src/ocrinvoice/cli/main.py`)

The main CLI entry point and command routing.

#### Function: `main(args: Optional[List[str]] = None) -> int`

Main CLI entry point.

**Parameters:**
- `args`: Command line arguments (defaults to sys.argv[1:])

**Returns:**
- Exit code (0 for success, non-zero for errors)

**Example:**
```python
from ocrininvoice.cli.main import main

# Run CLI with arguments
exit_code = main(["parse", "invoice.pdf", "--output", "result.json"])
print(f"Exit code: {exit_code}")
```

### CLI Commands

#### Parse Command (`src/ocrinvoice/cli/commands/parse.py`)

```python
class ParseCommand:
    """Parse a single invoice file."""

    def execute(self, args: Namespace) -> int:
        """Execute the parse command.

        Args:
            args: Parsed command line arguments

        Returns:
            Exit code
        """
```

#### Batch Command (`src/ocrinvoice/cli/commands/batch.py`)

```python
class BatchCommand:
    """Process multiple invoice files in batch."""

    def execute(self, args: Namespace) -> int:
        """Execute the batch command.

        Args:
            args: Parsed command line arguments

        Returns:
            Exit code
        """
```

#### Aliases Command (`src/ocrinvoice/cli/commands/aliases.py`)

```python
class AliasesCommand:
    """Manage business name aliases."""

    def execute(self, args: Namespace) -> int:
        """Execute the aliases command.

        Args:
            args: Parsed command line arguments

        Returns:
            Exit code
        """
```

## ⚙️ Configuration API

### Configuration Manager (`src/ocrinvoice/config.py`)

The configuration management system.

#### Function: `load_config() -> Dict[str, Any]`

Load configuration from multiple sources.

**Returns:**
- Merged configuration dictionary

**Example:**
```python
from ocrininvoice.config import load_config

config = load_config()
print(f"OCR path: {config['ocr']['tesseract_path']}")
print(f"Debug mode: {config['debug']}")
```

#### Configuration Sources (in order of precedence):

1. **Environment Variables**: Highest priority
2. **User Config**: `~/.ocrinvoice/config.yaml`
3. **Package Defaults**: `config/default_config.yaml`
4. **Hard-coded Defaults**: Lowest priority

#### Environment Variables:

```bash
# OCR Settings
export OCRINVOICE_OCR_TESSERACT_PATH="/usr/local/bin/tesseract"
export OCRINVOICE_OCR_LANGUAGE="eng+fra"
export OCRINVOICE_OCR_DPI="300"

# Parser Settings
export OCRINVOICE_PARSER_DEBUG="true"
export OCRINVOICE_PARSER_CONFIDENCE_THRESHOLD="0.8"

# Business Settings
export OCRINVOICE_BUSINESS_ALIAS_FILE="/path/to/aliases.json"
```

## 🔧 Error Handling

### Common Exceptions

#### `FileNotFoundError`
Raised when a required file is not found.

**Example:**
```python
try:
    parser.parse("non_existent.pdf")
except FileNotFoundError as e:
    print(f"File not found: {e}")
```

#### `ValueError`
Raised when input data is invalid.

**Example:**
```python
try:
    normalizer.normalize_amount("invalid_amount")
except ValueError as e:
    print(f"Invalid amount: {e}")
```

#### `OCRProcessingError`
Raised when OCR processing fails.

**Example:**
```python
try:
    engine.extract_text(image)
except OCRProcessingError as e:
    print(f"OCR failed: {e}")
```

## 📊 Performance Considerations

### Memory Usage

- **Text Extraction**: 50-200MB per document
- **Image Processing**: 100-500MB per image
- **Batch Processing**: Scales with number of documents

### Processing Speed

- **Single Document**: 2-5 seconds
- **Batch Processing**: 10-50 documents per minute
- **OCR Processing**: 1-3 seconds per page

### Optimization Tips

1. **Reuse Parser Instances**: Create parser once, reuse for multiple documents
2. **Batch Processing**: Use batch commands for multiple files
3. **Memory Management**: Process documents in chunks for large batches
4. **Caching**: Enable caching for repeated operations

## 🔗 Integration Examples

### Basic Integration

```python
from ocrininvoice.parsers.invoice_parser import InvoiceParser
from ocrininvoice.config import load_config

# Load configuration
config = load_config()

# Create parser
parser = InvoiceParser(config)

# Parse invoice
result = parser.parse("invoice.pdf")

# Process results
if result["success"]:
    print(f"Company: {result['company']}")
    print(f"Total: {result['total']}")
    print(f"Date: {result['date']}")
    print(f"Confidence: {result['confidence']:.2f}")
else:
    print("Parsing failed")
```

### Custom Parser Integration

```python
from ocrininvoice.parsers.base_parser import BaseParser
from ocrininvoice.core.text_extractor import TextExtractor
from ocrininvoice.utils.amount_normalizer import AmountNormalizer

class CustomParser(BaseParser):
    def __init__(self, config):
        super().__init__(config)
        self.text_extractor = TextExtractor(config)
        self.amount_normalizer = AmountNormalizer()

    def parse(self, pdf_path):
        # Extract text
        text = self.text_extractor.extract_text(pdf_path)

        # Extract data
        company = self.extract_company(text)
        total = self.extract_total(text)
        date = self.extract_date(text)

        # Calculate confidence
        confidence = self.calculate_confidence({
            "company": company,
            "total": total,
            "date": date
        }, text)

        return {
            "success": confidence >= self.confidence_threshold,
            "company": company,
            "total": total,
            "date": date,
            "confidence": confidence
        }
```

---

*For more information about the API, see the [Architecture Documentation](../architecture/) and [Development Setup Guide](./development_setup.md).*
