# Development Setup Guide

> **Complete guide for setting up the OCR Invoice Parser development environment**

This guide covers setting up the development environment for the OCR Invoice Parser project, including both CLI and GUI components. **The MVP is now complete with all core features fully functional.**

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

# Test GUI (MVP Complete)
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
│   ├── gui/                     # GUI components (Sprint 4 ✅ COMPLETED)
│   │   ├── ocr_main_window.py   # Main GUI window
│   │   ├── widgets/             # GUI widgets
│   │   │   ├── pdf_preview.py   # PDF preview widget
│   │   │   ├── data_panel.py    # Data display widget
│   │   │   └── file_naming.py   # File naming widget (MVP Complete)
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

#### GUI Development (Sprint 4 ✅ COMPLETED)
- **`src/ocrinvoice/gui/ocr_main_window.py`**: Main application window with complete MVP
- **`src/ocrinvoice/gui/widgets/file_naming.py`**: File naming system (MVP Complete)
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
pytest tests/test_gui/                # GUI tests (MVP Complete)

# Run GUI tests specifically
pytest tests/test_gui/ -v

# Run with verbose output
pytest -v
```

### GUI Testing (Sprint 4 ✅ COMPLETED)

The project includes comprehensive GUI testing using `pytest-qt`:

```bash
# Install GUI testing dependencies
pip install pytest-qt

# Run GUI tests
pytest tests/test_gui/ -v

# Run specific GUI test
pytest tests/test_gui/test_ocr_main_window.py -v
pytest tests/test_gui/test_file_naming.py -v
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
├── test_gui/                       # GUI tests (Sprint 4 ✅ COMPLETED)
│   ├── test_ocr_main_window.py     # Main window tests
│   ├── test_file_naming.py         # File naming tests (MVP Complete)
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
```

### Pre-commit Configuration

The project uses pre-commit hooks for code quality:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
        language_version: python3
  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.3.0
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
```

## 🎨 GUI Development (Sprint 4 ✅ COMPLETED)

### GUI Architecture

The GUI is built with PyQt6 and follows modern design patterns:

```
┌─────────────────────────────────────────────────────────────────┐
│                    GUI Development Stack                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────┐    ┌─────────────────┐    ┌──────────────┐ │
│  │   PyQt6         │    │   Custom        │    │   Testing    │ │
│  │   Framework     │    │   Widgets       │    │   Framework  │ │
│  │                 │    │                 │    │              │ │
│  │ • QMainWindow   │    │ • FileNaming    │    │ • pytest-qt  │ │
│  │ • QTabWidget    │    │ • DataPanel     │    │ • QTest      │ │
│  │ • QTableWidget  │    │ • PDFPreview    │    │ • Mocking    │ │
│  │ • QProgressBar  │    │ • Custom        │    │ • Coverage   │ │
│  └─────────────────┘    └─────────────────┘    └──────────────┘ │
│           │                       │                       │     │
│           └───────────────────────┼───────────────────────┘     │
│                                   │                             │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                    Design Patterns                          │ │
│  │                                                             │ │
│  │ • Model-View-Controller    • Observer Pattern              │ │
│  │ • Signal/Slot Architecture • Factory Pattern               │ │
│  │ • Background Threading     • Strategy Pattern              │ │
│  └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### Key GUI Components

#### 1. Main Window (`ocr_main_window.py`)
- **Tab Management**: Single PDF, File Naming, Settings tabs
- **Status Bar**: Persistent filename display and status messages
- **Menu Bar**: Application menu and keyboard shortcuts
- **Theme**: Consistent blue/gray color scheme

#### 2. File Naming Widget (`file_naming.py`)
- **Template Builder**: Visual template creation interface
- **Live Preview**: Real-time filename preview with validation
- **Conflict Resolution**: Smart handling of duplicate filenames
- **Backup Options**: Configurable backup settings

#### 3. Data Panel (`data_panel.py`)
- **Table Display**: Clean table-based data presentation
- **Confidence Indicators**: Visual confidence scoring
- **Export Functions**: JSON/CSV export capabilities
- **Validation**: Real-time data validation

#### 4. PDF Preview (`pdf_preview.py`)
- **Image Display**: PDF page rendering
- **Zoom/Pan**: Interactive PDF navigation
- **Page Navigation**: Multi-page PDF support
- **Thumbnails**: Page thumbnail display

### GUI Development Workflow

#### 1. Widget Development
```python
# Example: Creating a custom widget
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtCore import pyqtSignal

class CustomWidget(QWidget):
    # Define signals for communication
    data_changed = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.connect_signals()

    def setup_ui(self):
        # Create UI components
        layout = QVBoxLayout()
        self.setLayout(layout)

    def connect_signals(self):
        # Connect signals to slots
        pass
```

#### 2. Signal/Slot Architecture
```python
# Example: Signal/slot connections
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.connect_signals()

    def connect_signals(self):
        # Connect widget signals to main window slots
        self.file_naming_widget.rename_requested.connect(self.handle_rename)
        self.data_panel.export_requested.connect(self.handle_export)
```

#### 3. Background Processing
```python
# Example: Background OCR processing
from PyQt6.QtCore import QThread, pyqtSignal

class OCRThread(QThread):
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, pdf_path):
        super().__init__()
        self.pdf_path = pdf_path

    def run(self):
        try:
            # Perform OCR processing
            result = self.process_pdf()
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))
```

### GUI Testing (Sprint 4 ✅ COMPLETED)

#### Test Structure
```python
# Example: GUI test
import pytest
from PyQt6.QtWidgets import QApplication
from src.ocrinvoice.gui.ocr_main_window import OCRMainWindow

@pytest.fixture
def app():
    return QApplication([])

@pytest.fixture
def main_window(app):
    window = OCRMainWindow()
    yield window
    window.close()

def test_main_window_creation(main_window):
    assert main_window is not None
    assert main_window.windowTitle() == "OCR Invoice Parser"

def test_file_naming_widget(main_window):
    # Test file naming functionality
    file_naming = main_window.file_naming_widget
    assert file_naming is not None
```

#### Running GUI Tests
```bash
# Run all GUI tests
pytest tests/test_gui/ -v

# Run specific GUI test file
pytest tests/test_gui/test_file_naming.py -v

# Run with coverage
pytest tests/test_gui/ --cov=src/ocrinvoice/gui
```

## 🔄 Integration Development

### CLI-GUI Integration

The GUI maintains full compatibility with the CLI:

```python
# Example: Using CLI components in GUI
from src.ocrinvoice.parsers.invoice_parser import InvoiceParser
from src.ocrinvoice.business.business_mapping_manager import BusinessMappingManager

class GUIProcessor:
    def __init__(self):
        # Use same components as CLI
        self.parser = InvoiceParser()
        self.business_manager = BusinessMappingManager()

    def process_pdf(self, pdf_path):
        # Same processing logic as CLI
        result = self.parser.parse(pdf_path)
        return result
```

### Data Format Compatibility

```python
# Example: Shared data formats
import json

def save_results(data, output_path):
    # Same format as CLI
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)

def load_results(input_path):
    # Same format as CLI
    with open(input_path, 'r') as f:
        return json.load(f)
```

## 🚀 Development Workflow

### 1. Feature Development

```bash
# Create feature branch
git checkout -b feature/new-feature

# Make changes
# Test changes
pytest tests/test_gui/ -v

# Run code quality checks
pre-commit run --all-files

# Commit changes
git add .
git commit -m "feat(gui): add new feature"
```

### 2. Testing Workflow

```bash
# Run all tests
pytest

# Run GUI tests specifically
pytest tests/test_gui/ -v

# Run with coverage
pytest --cov=src/ocrinvoice --cov-report=html

# Check code quality
black src/ tests/
flake8 src/ tests/
mypy src/
```

### 3. Documentation Updates

```bash
# Update user documentation
# Edit docs/user_guide/gui_guide.md

# Update developer documentation
# Edit docs/developer/development_setup.md

# Update architecture documentation
# Edit docs/architecture/system_architecture.md
```

## 🎯 MVP Development Status

### Completed Features (Sprint 4 ✅ COMPLETED)

#### Core Functionality
- ✅ **OCR Processing**: Background threading with progress indicators
- ✅ **Business Alias Integration**: Seamless integration with existing CLI system
- ✅ **Data Display**: Clean table-based display with confidence indicators
- ✅ **File Naming System**: Complete template builder with live preview
- ✅ **File Management**: Actual file renaming with backup and conflict resolution

#### User Experience
- ✅ **Consistent Theme**: Uniform blue/gray color scheme
- ✅ **Persistent Filename**: Current filename displayed in status bar
- ✅ **Keyboard Shortcuts**: Quick access to common functions
- ✅ **Tooltips**: Helpful information on hover
- ✅ **Error Handling**: User-friendly error messages and validation

#### Integration
- ✅ **CLI Compatibility**: Full compatibility with existing CLI functionality
- ✅ **Data Formats**: Same JSON/CSV formats as CLI
- ✅ **Configuration**: Shared settings between CLI and GUI
- ✅ **Testing**: Comprehensive test suite with GUI testing

### Development Guidelines

#### Code Standards
- **Python**: Follow PEP 8, use type hints
- **PyQt6**: Use modern PyQt6 patterns, proper signal/slot connections
- **Error Handling**: Graceful degradation, user-friendly error messages
- **Testing**: Unit tests for business logic, integration tests for GUI
- **Documentation**: Clear docstrings, proper documentation structure

#### GUI Development Best Practices
- **Responsive Design**: Interface adapts to different window sizes
- **Background Processing**: Never block the UI thread
- **Error Recovery**: Graceful handling of all error conditions
- **User Feedback**: Clear status messages and progress indicators
- **Accessibility**: Consider accessibility features in design

---

## 📚 Additional Resources

### Documentation
- [GUI User Guide](../user_guide/gui_guide.md) - Complete GUI usage guide
- [System Architecture](../architecture/system_architecture.md) - Technical architecture
- [Development Plan](../architecture/ocr_gui_development_plan.md) - Development roadmap

### External Resources
- [PyQt6 Documentation](https://doc.qt.io/qtforpython/) - PyQt6 reference
- [pytest-qt Documentation](https://pytest-qt.readthedocs.io/) - GUI testing guide
- [Qt Design Patterns](https://doc.qt.io/qt-6/design-patterns.html) - Qt design patterns

This development setup provides everything needed to work with the OCR Invoice Parser project, including the complete MVP GUI application with comprehensive testing and documentation.
