# Invoice OCR Parser

> **Extract structured data from PDF invoices with advanced OCR and intelligent parsing**

A powerful command-line tool that converts scanned PDF invoices into structured data (JSON, CSV, XML) using advanced OCR techniques, fuzzy matching, and intelligent business name recognition.

## 🚀 Quick Start

### Installation

```bash
# Clone and install
git clone <repository-url>
cd ocrinvoice
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e .

# Install Tesseract OCR (required)
brew install tesseract  # macOS
sudo apt-get install tesseract-ocr  # Ubuntu/Debian
# Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki
```

### Your First Parse

```bash
# Parse an invoice
ocrinvoice parse invoice.pdf

# Output:
{
  "company": "HYDRO-QUÉBEC",
  "total": 137.50,
  "date": "2023-01-15",
  "invoice_number": "INV-2023-001",
  "confidence": 0.85
}
```

## 📖 Basic Usage

```bash
# Parse single invoice
ocrinvoice parse invoice.pdf --output result.json

# Process multiple invoices
ocrinvoice batch invoices/ --output results.csv

# Rename files based on extracted data
ocrinvoice parse invoice.pdf --rename
ocrinvoice batch invoices/ --rename --dry-run

# Manage business aliases
ocrinvoice aliases add "Hydro Quebec" "HYDRO-QUÉBEC"
ocrinvoice aliases list

# View configuration
ocrinvoice config
```

## 📚 Documentation

### For Users
- **[Getting Started](docs/user_guide/getting_started.md)** - Complete installation and setup guide
- **[CLI Reference](docs/user_guide/cli_reference.md)** - All commands and options
- **[Configuration](docs/user_guide/configuration.md)** - System configuration guide
- **[Troubleshooting](docs/user_guide/troubleshooting.md)** - Common issues and solutions

### For Developers
- **[Development Setup](docs/developer/development_setup.md)** - Development environment setup
- **[Contributing Guidelines](docs/developer/contributing.md)** - How to contribute
- **[Testing Guide](docs/developer/testing.md)** - Testing practices and tools
- **[API Reference](docs/developer/api_reference.md)** - Internal API documentation

### For Technical Stakeholders
- **[System Architecture](docs/architecture/system_architecture.md)** - High-level system design
- **[Feature Analysis](docs/architecture/feature_analysis.md)** - Business and technical analysis
- **[Technical Deep Dive](docs/architecture/technical_deep_dive.md)** - Implementation details

## 🎯 What It Extracts

| Field | Description | Example |
|-------|-------------|---------|
| **Company** | Business name | "HYDRO-QUÉBEC" |
| **Total** | Invoice amount | 137.50 |
| **Date** | Invoice date | "2023-01-15" |
| **Invoice Number** | Invoice ID | "INV-2023-001" |
| **Confidence** | Extraction confidence | 0.85 |

## 🗂️ File Organization

Automatically rename your PDF files based on extracted data:

```bash
# Single file: 2023-01-15_HYDRO-QUÉBEC_137.50.pdf
ocrinvoice parse invoice.pdf --rename

# Batch processing with preview
ocrinvoice batch invoices/ --rename --dry-run
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
├── tests/                       # Test suite
└── docs/                        # Documentation
    ├── README.md                # Documentation index
    ├── user_guide/              # End user documentation
    ├── architecture/            # Technical architecture
    └── developer/               # Developer resources
```

## 🚨 Quick Troubleshooting

**"Tesseract not found"** → Install Tesseract OCR (see [Getting Started](docs/user_guide/getting_started.md))

**"No data extracted"** → Try `ocrinvoice parse invoice.pdf --show-text --verbose`

**"Business name not recognized"** → Add alias: `ocrinvoice aliases add "Company Name" "OFFICIAL_NAME"`

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

See [Contributing Guidelines](docs/developer/contributing.md) for detailed instructions.

## 📄 License

MIT License - see LICENSE file for details.

---

**Ready to extract invoice data?** Start with `ocrinvoice parse your-invoice.pdf` and see the magic happen! ✨
