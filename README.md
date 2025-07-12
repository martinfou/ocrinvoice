# Invoice OCR Parser

> **Extract structured data from PDF invoices with advanced OCR and intelligent parsing**

A powerful command-line tool and desktop GUI that converts scanned PDF invoices into structured data (JSON, CSV, XML) using advanced OCR techniques, fuzzy matching, and intelligent business name recognition.

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

## 🖥️ GUI Application

**NEW: Desktop GUI with File Management Features!**

Launch the GUI application for an intuitive desktop experience:

```bash
# Launch the GUI
python -m src.ocrinvoice.gui.ocr_main_window
```

### GUI Features (Sprint 3 Completed ✅)

- **📄 Single PDF Processing**: Load and process individual PDF invoices
- **🏷️ File Naming System**: Custom templates with live preview
- **⚙️ Template Builder**: Visual interface for creating naming patterns
- **🔍 Live Preview**: Real-time filename preview with validation
- **🛡️ Conflict Resolution**: Smart handling of duplicate filenames
- **💾 Backup Options**: Configurable backup settings
- **✅ Validation**: Real-time template and filename validation
- **📁 File Management**: Open folders, manage processed files

### GUI Workflow

1. **Load PDF**: Drag & drop or browse for PDF files
2. **OCR Processing**: Automatic data extraction with progress indicator
3. **Review Data**: View extracted information in editable table
4. **File Naming**: Configure custom naming templates with live preview
5. **Rename Files**: Apply naming with conflict resolution
6. **Export Data**: Save results in JSON/CSV format

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

# Launch GUI for alias management
ocrinvoice gui

# View configuration
ocrinvoice config
```

## 📚 Documentation

### For Users
- **[Getting Started](docs/user_guide/getting_started.md)** - Complete installation and setup guide
- **[CLI Reference](docs/user_guide/cli_reference.md)** - All commands and options
- **[GUI Guide](docs/user_guide/gui_guide.md)** - Desktop GUI usage guide
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
- **[Development Plan](docs/architecture/ocr_gui_development_plan.md)** - Sprint planning and progress

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

# GUI: Custom templates with live preview
# Template: {documentType}_{company}_{date}_{total}.pdf
# Preview: facture_HYDRO-QUÉBEC_2023-01-15_137.50.pdf
```

## 📁 Project Structure

```
ocrinvoice/
├── src/ocrinvoice/              # Main package
│   ├── cli/                     # Command line interface
│   ├── gui/                     # Desktop GUI application
│   │   ├── widgets/             # GUI components
│   │   │   ├── pdf_preview.py   # PDF preview widget
│   │   │   ├── data_panel.py    # Data display widget
│   │   │   └── file_naming.py   # File naming widget (NEW)
│   │   ├── ocr_main_window.py   # Main GUI window
│   │   └── dialogs/             # Modal dialogs
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
    │   ├── getting_started.md   # Installation and setup
    │   ├── cli_reference.md     # Command line reference
    │   ├── gui_guide.md         # Desktop GUI guide
    │   ├── configuration.md     # Configuration guide
    │   └── troubleshooting.md   # Common issues
    ├── architecture/            # Technical architecture
    └── developer/               # Developer resources
```

## 🚨 Quick Troubleshooting

**"Tesseract not found"** → Install Tesseract OCR (see [Getting Started](docs/user_guide/getting_started.md))

**"No data extracted"** → Try `ocrinvoice parse invoice.pdf --show-text --verbose`

**"Business name not recognized"** → Add alias: `ocrinvoice aliases add "Company Name" "CANONICAL_NAME"`

**"GUI not launching"** → Ensure PyQt6 is installed: `pip install PyQt6`

## 📊 Performance

- **Speed**: ~2-5 seconds per page
- **Accuracy**: 90%+ for standard invoice formats
- **OCR Correction**: 95%+ accuracy for common errors
- **Batch Processing**: Optimized for multiple files
- **GUI Responsiveness**: Non-blocking OCR processing with progress indicators

## 🎉 Recent Updates (Sprint 3)

### ✅ File Management & Naming System
- **Template Builder**: Visual interface for creating custom naming patterns
- **Live Preview**: Real-time filename preview with validation
- **Conflict Resolution**: Smart handling of duplicate filenames
- **Backup Options**: Configurable backup settings
- **Validation**: Real-time template and filename validation
- **File Management**: Open folders, manage processed files

### 🔧 Technical Improvements
- **Background Processing**: Non-blocking OCR with progress indicators
- **Error Handling**: Comprehensive error handling with user feedback
- **Integration**: Seamless integration with existing CLI functionality
- **Data Compatibility**: GUI reads/writes same formats as CLI

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch**
3. **Add tests** for new functionality
4. **Submit a pull request**

See [Contributing Guidelines](docs/developer/contributing.md) for detailed instructions.

## 📄 License

MIT License - see LICENSE file for details.

---

**Ready to extract invoice data?** Start with `python -m src.ocrinvoice.gui.ocr_main_window` for the GUI or `ocrinvoice parse your-invoice.pdf` for CLI! ✨
