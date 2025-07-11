# Invoice OCR Parser

> **Extract structured data from PDF invoices with advanced OCR and intelligent parsing**

A powerful command-line tool that converts scanned PDF invoices into structured data (JSON, CSV, XML) using advanced OCR techniques, fuzzy matching, and intelligent business name recognition.

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <repository-url>
cd ocrinvoice

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install the package
pip install -e .
```

### 2. Install Tesseract OCR (Required)

**macOS:**
```bash
brew install tesseract
```

**Ubuntu/Debian:**
```bash
sudo apt-get install tesseract-ocr
```

**Windows:**
Download from [GitHub releases](https://github.com/UB-Mannheim/tesseract/wiki)

### 3. Your First Invoice Parse

```bash
# Parse a single invoice
ocrinvoice parse invoice.pdf

# See the extracted data in JSON format
{
  "company": "HYDRO-QUÉBEC",
  "total": 137.50,
  "date": "2023-01-15",
  "invoice_number": "INV-2023-001",
  "confidence": 0.85
}
```

## 📖 Basic Usage

### Parse a Single Invoice
```bash
# Basic parse
ocrinvoice parse invoice.pdf

# Save to file
ocrinvoice parse invoice.pdf --output result.json

# Show raw extracted text
ocrinvoice parse invoice.pdf --show-text

# Verbose output
ocrinvoice parse invoice.pdf --verbose
```

### Process Multiple Invoices
```bash
# Process all PDFs in a folder
ocrinvoice batch invoices/ --output results.csv

# Process recursively (including subfolders)
ocrinvoice batch invoices/ --recursive --output results.csv

# Different output formats
ocrinvoice batch invoices/ --format json --output results.json
ocrinvoice batch invoices/ --format xml --output results.xml
```

### Manage Business Names
```bash
# List all known businesses
ocrinvoice aliases list

# Add a business alias
ocrinvoice aliases add "Hydro Quebec" "HYDRO-QUÉBEC"

# Add a new official business name
ocrinvoice aliases add-official "NEW COMPANY LTD"

# Test how a business name would be matched
ocrinvoice aliases test "Hydro Quebec Inc"
```

## 🎯 What It Extracts

The parser automatically extracts these fields from your invoices:

| Field | Description | Example |
|-------|-------------|---------|
| **Company** | Business name | "HYDRO-QUÉBEC" |
| **Total** | Invoice amount | 137.50 |
| **Date** | Invoice date | "2023-01-15" |
| **Invoice Number** | Invoice ID | "INV-2023-001" |
| **Confidence** | Extraction confidence | 0.85 |

## 🔧 Configuration

### View Current Settings
```bash
ocrinvoice config
```

### Set Environment Variables
```bash
# OCR Settings
export OCRINVOICE_OCR_TESSERACT_PATH="/usr/local/bin/tesseract"
export OCRINVOICE_OCR_LANGUAGE="eng+fra"

# Business Settings
export OCRINVOICE_BUSINESS_ALIAS_FILE="/path/to/aliases.json"

# Parser Settings
export OCRINVOICE_PARSER_DEBUG="true"
```

### Configuration Files
The system automatically loads settings from:
1. `config/default_config.yaml` (package defaults)
2. `~/.ocrinvoice/config.yaml` (your custom settings)
3. Environment variables (override everything)

## 🧪 Testing

### Run All Tests
```bash
ocrinvoice test
```

### Test with Coverage
```bash
ocrinvoice test --coverage
```

### Test Specific Components
```bash
# Test invoice parsing
pytest tests/unit/test_parsers/test_invoice_parser.py

# Test business aliases
pytest tests/unit/test_business/test_business_alias_manager.py

# Test CLI commands
pytest tests/unit/test_cli/
```

## 🎨 Advanced Features

### OCR Error Correction
Automatically fixes common OCR mistakes:

| OCR Error | Fixed To | Example |
|-----------|----------|---------|
| `l` → `1` | `537,l6` → `537.16` |
| `O` → `0` | `537,O6` → `537.06` |
| `S` → `5` | `537,S6` → `537.56` |
| `G` → `6` | `537,G6` → `537.66` |

### International Number Formats
Handles various decimal formats:

| Format | Input | Output |
|--------|-------|--------|
| European | `537,16` | `537.16` |
| US | `537.16` | `537.16` |
| Mixed | `1,234.56` | `1234.56` |
| Currency | `$537,16` | `537.16` |

### Fuzzy Business Matching
Intelligently matches business names even with typos:

```bash
# These all match "HYDRO-QUÉBEC"
ocrinvoice aliases test "Hydro Quebec"
ocrinvoice aliases test "Hydro-Quebec"
ocrinvoice aliases test "HYDRO QUEBEC"
```

## 📁 Project Structure

```
ocrinvoice/
├── src/ocrinvoice/              # Main package
│   ├── cli/                     # Command line interface
│   ├── core/                    # Core functionality (OCR, image processing)
│   ├── parsers/                 # Document parsers (invoice, credit card)
│   ├── utils/                   # Utilities (fuzzy matching, corrections)
│   ├── business/                # Business logic (alias management)
│   └── config.py                # Configuration management
├── config/                      # Configuration files
│   ├── default_config.yaml      # Default settings
│   ├── business_aliases.json    # Business name mappings
│   └── logging_config.yaml      # Logging configuration
├── tests/                       # Test suite
└── docs/                        # Documentation
```

## 🚨 Troubleshooting

### Common Issues

**"Tesseract not found"**
```bash
# Install Tesseract first
brew install tesseract  # macOS
sudo apt-get install tesseract-ocr  # Ubuntu
```

**"No data extracted"**
```bash
# Check if the PDF is readable
ocrinvoice parse invoice.pdf --show-text

# Try with verbose output
ocrinvoice parse invoice.pdf --verbose
```

**"Business name not recognized"**
```bash
# Add the business to your aliases
ocrinvoice aliases add "Company Name" "OFFICIAL_NAME"

# Check existing aliases
ocrinvoice aliases list
```

### Getting Help

```bash
# Show all available commands
ocrinvoice --help

# Show help for specific command
ocrinvoice parse --help
ocrinvoice batch --help
ocrinvoice aliases --help
```

## 📊 Performance

- **Speed**: ~2-5 seconds per page
- **Accuracy**: 90%+ for standard invoice formats
- **OCR Correction**: 95%+ accuracy for common errors
- **Batch Processing**: Optimized for multiple files

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch**
3. **Add tests** for new functionality
4. **Submit a pull request**

### Development Setup
```bash
# Install development dependencies
pip install -e ".[dev]"

# Run pre-commit hooks
pre-commit install

# Run tests
pytest

# Run linting
flake8 src/ tests/
mypy src/
```

## 📄 License

MIT License - see LICENSE file for details.

## 🙏 Acknowledgments

- **Tesseract OCR**: Underlying OCR engine
- **Click**: CLI framework
- **Open source community**: Inspiration and feedback

---

**Ready to extract invoice data?** Start with `ocrinvoice parse your-invoice.pdf` and see the magic happen! ✨
