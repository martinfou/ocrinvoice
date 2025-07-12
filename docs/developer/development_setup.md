# Development Setup Guide

> **Complete guide for setting up the OCR Invoice Parser development environment**

This guide covers setting up the development environment for the OCR Invoice Parser project, including both CLI and GUI components.

## 🚀 Quick Setup

### Prerequisites

- **Python 3.8+** (3.9+ recommended)
- **Git** for version control
- **Tesseract OCR** (required for OCR functionality)
- **Virtual Environment** (recommended)

### 1. Clone the Repository

```bash
git clone <repository-url>
cd ocrinvoice
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
# Install the package in development mode
pip install -e .

# Install development dependencies
pip install -r requirements-dev.txt
```

### 4. Install Tesseract OCR

#### macOS
```bash
brew install tesseract
```

#### Ubuntu/Debian
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
```

#### Windows
Download from: https://github.com/UB-Mannheim/tesseract/wiki

### 5. Verify Installation

```bash
# Test CLI
ocrinvoice --help

# Test GUI
python -m src.ocrinvoice.gui.ocr_main_window

# Test imports
python -c "from src.ocrinvoice.parsers.invoice_parser import InvoiceParser; print('✓ Core imports work')"
python -c "from src.ocrinvoice.gui.widgets.file_naming import FileNamingWidget; print('✓ GUI imports work')"
```

## 🛠️ Development Environment

### Project Structure

```
ocrinvoice/
├── src/ocrinvoice/              # Main package
│   ├── cli/                     # Command line interface
│   │   ├── main.py              # CLI entry point
│   │   ├── commands/            # Command implementations
│   │   └── utils.py             # CLI utilities
│   ├── gui/                     # GUI components (Sprint 3 ✅)
│   │   ├── ocr_main_window.py   # Main GUI window
│   │   ├── widgets/             # GUI widgets
│   │   │   ├── pdf_preview.py   # PDF preview widget
│   │   │   ├── data_panel.py    # Data display widget
│   │   │   └── file_naming.py   # File naming widget (NEW)
│   │   └── dialogs/             # Modal dialogs
│   ├── core/                    # Core OCR functionality
│   │   ├── ocr_engine.py        # OCR engine
│   │   ├── image_processor.py   # Image processing
│   │   └── text_extractor.py    # Text extraction
│   ├── parsers/                 # Document parsers
│   │   ├── base_parser.py       # Base parser class
│   │   ├── invoice_parser.py    # Invoice parser
│   │   └── credit_card_parser.py # Credit card parser
│   ├── business/                # Business logic
│   │   └── business_mapping_manager.py # Alias management
│   ├── utils/                   # Utilities
│   │   ├── file_manager.py      # File operations
│   │   ├── fuzzy_matcher.py     # String matching
│   │   └── amount_normalizer.py # Amount processing
│   └── config.py                # Configuration management
├── config/                      # Configuration files
├── tests/                       # Test suite
├── docs/                        # Documentation
└── requirements-dev.txt         # Development dependencies
```

### Key Development Files

#### GUI Development (Sprint 3 Completed ✅)
- **`src/ocrinvoice/gui/ocr_main_window.py`**: Main application window
- **`src/ocrinvoice/gui/widgets/file_naming.py`**: File naming system (NEW)
- **`src/ocrinvoice/gui/widgets/pdf_preview.py`**: PDF preview widget
- **`src/ocrinvoice/gui/widgets/data_panel.py`**: Data display widget

#### Core Development
- **`src/ocrinvoice/parsers/invoice_parser.py`**: Main parsing logic
- **`src/ocrinvoice/core/ocr_engine.py`**: OCR processing
- **`src/ocrinvoice/business/business_mapping_manager.py`**: Business logic
- **`src/ocrinvoice/utils/file_manager.py`**: File operations

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/ocrinvoice

# Run specific test categories
pytest tests/unit/                    # Unit tests
pytest tests/integration/             # Integration tests
pytest tests/test_gui/                # GUI tests

# Run GUI tests specifically
pytest tests/test_gui/ -v

# Run with verbose output
pytest -v
```

### GUI Testing

The project includes comprehensive GUI testing using `pytest-qt`:

```bash
# Install GUI testing dependencies
pip install pytest-qt

# Run GUI tests
pytest tests/test_gui/ -v

# Run specific GUI test
pytest tests/test_gui/test_ocr_main_window.py -v
```

### Test Structure

```
tests/
├── unit/                           # Unit tests
│   ├── test_core/                  # Core functionality tests
│   ├── test_parsers/               # Parser tests
│   ├── test_business/              # Business logic tests
│   └── test_utils/                 # Utility tests
├── integration/                    # Integration tests
├── test_gui/                       # GUI tests (Sprint 3 ✅)
│   ├── test_ocr_main_window.py     # Main window tests
│   ├── test_file_naming.py         # File naming tests (NEW)
│   └── test_widgets/               # Widget tests
└── conftest.py                     # Test configuration
```

## 🔧 Development Tools

### Code Quality

```bash
# Run pre-commit hooks
pre-commit run --all-files

# Format code
black src/ tests/

# Lint code
flake8 src/ tests/

# Type checking
mypy src/

# Run all quality checks
pre-commit run --all-files
```

### Pre-commit Hooks

The project uses pre-commit hooks for code quality:

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

### IDE Configuration

#### VS Code
Create `.vscode/settings.json`:
```json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": ["tests"],
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black"
}
```

#### PyCharm
- Set project interpreter to virtual environment
- Configure pytest as test runner
- Enable code inspection

## 🚀 Development Workflow

### 1. Feature Development

```bash
# Create feature branch
git checkout -b feature/new-feature

# Make changes
# ... edit files ...

# Run tests
pytest

# Run quality checks
pre-commit run --all-files

# Commit changes
git add .
git commit -m "feat: add new feature"
```

### 2. GUI Development

For GUI development, use the interactive development approach:

```bash
# Launch GUI for testing
python -m src.ocrinvoice.gui.ocr_main_window

# In another terminal, run tests
pytest tests/test_gui/ -v
```

### 3. Sprint Development

The project follows sprint-based development:

```bash
# Create sprint branch
git checkout -b sprint-4-new-features

# Develop features
# ... implement features ...

# Update documentation
# ... update docs ...

# Test thoroughly
pytest
python -m src.ocrinvoice.gui.ocr_main_window

# Commit with detailed message
git commit -m "feat(sprint-4): implement new features

- Add feature A with tests
- Update documentation
- Fix bug in component B
- Test with real PDF files"
```

## 🔍 Debugging

### CLI Debugging

```bash
# Run with debug output
ocrinvoice parse invoice.pdf --debug --verbose

# Run with logging
python -c "
import logging
logging.basicConfig(level=logging.DEBUG)
from src.ocrinvoice.cli.commands.parse import parse_command
result = parse_command('invoice.pdf')
print(result)
"
```

### GUI Debugging

```bash
# Run GUI with debug output
python -m src.ocrinvoice.gui.ocr_main_window --debug

# Test specific widgets
python -c "
from src.ocrinvoice.gui.widgets.file_naming import FileNamingWidget
widget = FileNamingWidget()
print('File naming widget created successfully')
"
```

### Common Debugging Scenarios

#### OCR Issues
```bash
# Test OCR engine directly
python -c "
from src.ocrinvoice.core.ocr_engine import OCREngine
engine = OCREngine()
print('OCR engine initialized')
"
```

#### GUI Issues
```bash
# Test GUI components
python -c "
from PyQt6.QtWidgets import QApplication
import sys
from src.ocrinvoice.gui.widgets.file_naming import FileNamingWidget

app = QApplication(sys.argv)
widget = FileNamingWidget()
widget.show()
print('GUI widget displayed successfully')
"
```

## 📚 Documentation

### Building Documentation

```bash
# Install documentation tools
pip install sphinx sphinx-rtd-theme

# Build documentation
cd docs
make html

# View documentation
open _build/html/index.html
```

### Documentation Structure

```
docs/
├── README.md                      # Main documentation index
├── user_guide/                    # User documentation
│   ├── getting_started.md         # Installation guide
│   ├── cli_reference.md           # CLI documentation
│   ├── gui_guide.md               # GUI documentation (Sprint 3 ✅)
│   ├── configuration.md           # Configuration guide
│   └── troubleshooting.md         # Troubleshooting guide
├── architecture/                  # Technical documentation
│   ├── system_architecture.md     # System design
│   ├── ocr_gui_development_plan.md # Development plan (Sprint 3 ✅)
│   └── technical_deep_dive.md     # Implementation details
└── developer/                     # Developer documentation
    ├── development_setup.md       # This file
    ├── contributing.md            # Contributing guidelines
    ├── testing.md                 # Testing guide
    └── api_reference.md           # API documentation
```

## 🎯 Sprint 3 Development Notes

### Completed Features (Sprint 3 ✅)

#### File Naming System
- **Template Builder**: Visual interface for creating naming patterns
- **Live Preview**: Real-time filename preview with validation
- **Conflict Resolution**: Smart handling of duplicate filenames
- **Backup Options**: Configurable backup settings
- **Validation**: Real-time template and filename validation

#### GUI Integration
- **Background Processing**: Non-blocking OCR with progress indicators
- **Error Handling**: Comprehensive error handling with user feedback
- **Data Compatibility**: GUI reads/writes same formats as CLI
- **Settings Integration**: Shared settings between CLI and GUI

### Development Guidelines

#### GUI Development
- Use PyQt6 for all GUI components
- Implement background threading for long operations
- Provide real-time feedback and progress indicators
- Maintain compatibility with CLI data formats
- Follow the established widget patterns

#### File Management
- Use existing `FileManager` from CLI
- Implement validation for all user inputs
- Provide clear error messages and recovery options
- Support both single file and batch operations
- Maintain backup and conflict resolution features

## 🚨 Troubleshooting

### Common Issues

#### Import Errors
```bash
# Check virtual environment
which python
# Should point to venv/bin/python

# Reinstall package
pip install -e . --force-reinstall
```

#### GUI Not Starting
```bash
# Check PyQt6 installation
python -c "from PyQt6.QtWidgets import QApplication; print('PyQt6 OK')"

# Check GUI imports
python -c "from src.ocrinvoice.gui.ocr_main_window import OCRMainWindow; print('GUI imports OK')"
```

#### OCR Issues
```bash
# Check Tesseract installation
tesseract --version

# Test OCR functionality
python -c "
from src.ocrinvoice.core.ocr_engine import OCREngine
engine = OCREngine()
print('OCR engine OK')
"
```

#### Test Failures
```bash
# Run tests with verbose output
pytest -v --tb=short

# Run specific failing test
pytest tests/test_specific.py::test_function -v -s
```

### Getting Help

- **Check Documentation**: Review relevant documentation files
- **Run Tests**: Ensure all tests pass
- **Check Logs**: Review error messages and debug output
- **Git Issues**: Check for known issues in the repository
- **Community**: Reach out to the development team

---

**Ready to develop?** Set up your environment and start contributing to the OCR Invoice Parser project! 🚀
