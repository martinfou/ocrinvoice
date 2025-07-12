# OCR Invoice Parser GUI Applications

> **PyQt6 Desktop Applications for OCR Invoice Processing and Business Management**

This guide covers the two main GUI applications in the OCR Invoice Parser project:

1. **OCR Invoice Parser GUI** - Main application for processing PDF invoices with OCR
2. **Business Aliases GUI Manager** - Application for managing business name aliases

## OCR Invoice Parser GUI

The main OCR GUI application for processing PDF invoices and extracting structured data.

### Current Development Status: Sprint 2 - OCR Integration ✅ **COMPLETED**

The OCR GUI has completed Sprint 2 and now provides full OCR functionality:

- ✅ Basic PyQt6 application structure
- ✅ Navigation framework with tabs
- ✅ Main window with menu bar and status bar
- ✅ Single PDF processing tab with full OCR integration
- ✅ Settings tab with configuration options
- ✅ Integration with existing OCR functionality
- ✅ Background OCR processing with progress indicators
- ✅ Business alias system integration
- ✅ Data extraction and display
- ✅ Compact drag-and-drop interface
- ✅ Error handling and user feedback

### Key Features Available

#### PDF Processing
- **File Selection**: Browse or drag-and-drop PDF files
- **PDF Preview**: View PDF with zoom and pan capabilities
- **OCR Processing**: Background processing with progress bar
- **Data Extraction**: Extract company, total, date, invoice number
- **Business Alias Integration**: Automatic company name matching

#### Data Display
- **Extracted Data Panel**: Clean table display of extracted fields
- **Confidence Indicators**: Shows confidence levels for each field
- **Editable Fields**: Modify extracted data if needed
- **Export Capabilities**: Export data functionality (ready for implementation)

#### User Interface
- **Compact Design**: Optimized layout with reduced drag-and-drop area
- **Responsive Layout**: Splitter-based PDF preview and data panel
- **Progress Feedback**: Real-time progress indicators
- **Error Handling**: User-friendly error messages
- **Settings Integration**: OCR language and configuration options

### Running the OCR GUI

```bash
# Launch the OCR GUI (fully functional)
python -m ocrinvoice.gui.ocr_main_window

# Or from the project root
python src/ocrinvoice/gui/ocr_main_window.py
```

### Using the OCR GUI

1. **Launch the application** using the command above
2. **Select a PDF invoice** using the "Select PDF" button or drag-and-drop
3. **Wait for OCR processing** - progress bar will show processing status
4. **Review extracted data** in the right panel
5. **Edit data if needed** - fields are editable
6. **Export data** using the "Export Data" button (when implemented)

### Supported File Types
- **PDF invoices** (single page or multi-page)
- **Standard invoice formats** (tested with Rona, Gagnon examples)
- **Various OCR qualities** (handles both high and low confidence extractions)

---

## Business Aliases GUI Manager

A comprehensive desktop GUI application for managing business aliases used by the OCR invoice parser, providing an intuitive interface for alias management, import/export operations, and analytics.

## 🚀 Quick Start

### Prerequisites

1. **Python 3.8+** installed on your system
2. **Virtual Environment** (recommended)

### Installation

1. **Clone the repository** (if not already done):
   ```bash
   git clone <repository-url>
   cd ocrinvoice
   ```

2. **Create and activate virtual environment**:
   ```bash
   # Create virtual environment
   python3 -m venv venv

   # Activate virtual environment
   # On macOS/Linux:
   source venv/bin/activate
   # On Windows:
   venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -e .
   ```

### Running the GUI

#### Method 1: Using the main command (Recommended)
```bash
# Launch the GUI
ocrinvoice gui
```

#### Method 2: Using Python module
```bash
# From the project root directory
python -m ocrinvoice gui
```

## 🎯 Features

### Core Functionality
- **Alias Management**: Add, edit, delete business name aliases
- **Visual Interface**: Intuitive table-based interface
- **Real-time Search**: Instant filtering and search capabilities
- **Data Validation**: Built-in validation with helpful error messages
- **CLI Integration**: Seamless integration with existing CLI functionality

### User Interface
- **Main Window**: Clean, professional interface with menu bar and toolbar
- **Alias Table**: Sortable table with company names, canonical names, and metadata
- **Add/Edit Forms**: Modal dialogs for managing individual aliases
- **Status Bar**: Real-time information about data and operations
- **Context Menus**: Right-click actions for quick operations

### Data Management
- **JSON Storage**: Uses same format as CLI for compatibility
- **Auto-save**: Automatic saving of changes
- **Error Handling**: Graceful error handling with user-friendly messages
- **Backup Support**: Automatic backup creation before major operations

## 🛠️ Development

### Project Structure
```
src/ocrinvoice/
├── cli/                    # Command line interface
│   └── main.py            # Main CLI entry point with --gui support
├── gui/                    # GUI components
│   ├── main_window.py      # Main application window
│   ├── alias_table.py      # Custom table widget
│   ├── alias_form.py       # Add/edit forms
│   └── dialogs/            # Modal dialogs
├── business/               # Business logic
│   └── business_alias_manager.py  # Alias management backend
└── utils/                  # Shared utilities
```

### Key Components

#### Main Window (`gui/main_window.py`)
- **QMainWindow**-based application window
- **Menu Bar**: File, Edit, Tools, View, Help menus
- **Toolbar**: Quick access buttons for common actions
- **Status Bar**: Shows alias count and operation status
- **Central Widget**: Alias table with search functionality

#### Alias Table (`gui/alias_table.py`)
- **QTableWidget** with custom sorting and filtering
- **Context Menus**: Right-click actions for quick operations
- **Keyboard Navigation**: Full keyboard support
- **Selection Management**: Multi-select capabilities

#### Alias Form (`gui/alias_form.py`)
- **Modal Dialog** for adding/editing aliases
- **Real-time Validation**: Immediate feedback on input errors
- **Preview Functionality**: Shows how alias will work
- **Auto-complete**: Suggests existing canonical names

### CLI Integration

The GUI is fully integrated with the existing CLI system:

```bash
# Launch GUI
ocrinvoice gui

# Launch GUI with debug output
ocrinvoice gui --debug

# Launch GUI with verbose output
ocrinvoice gui --verbose
```

## 🔧 Troubleshooting

### Common Issues

#### 1. "No module named 'PIL'" Error
```bash
# Install Pillow (PIL)
pip install Pillow
```

#### 2. "No module named 'PyQt6'" Error
```bash
# Install PyQt6
pip install PyQt6
```

#### 3. Import Errors
```bash
# Make sure you're in the virtual environment
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate     # Windows

# Reinstall the package
pip install -e .
```

#### 4. GUI Not Starting
```bash
# Check if the package is properly installed
python -c "import ocrinvoice.gui.main_window; print('GUI module found')"

# Try running with debug output
ocrinvoice gui --debug
```

### Debug Mode

Run the GUI with debug output to see detailed information:

```bash
ocrinvoice gui --debug
```

This will show:
- Module loading information
- Configuration details
- Error details if any issues occur

## 📋 Development Status

### ✅ Completed (Phase 1 - MVP)
- [x] Project structure setup
- [x] Basic PyQt6 application skeleton
- [x] Main window layout with menu bar and toolbar
- [x] Alias table widget with sorting and filtering
- [x] Add/edit alias forms with validation
- [x] Basic CRUD operations (Create, Read, Update, Delete)
- [x] Real-time search functionality
- [x] Status bar with alias count
- [x] CLI integration with `--gui` flag
- [x] Error handling and user feedback
- [x] Data validation and preview functionality
- [x] Context menus and keyboard shortcuts
- [x] Auto-save functionality

### 🚧 In Progress
- [ ] Import/export functionality
- [ ] Advanced filtering options
- [ ] Bulk operations
- [ ] Statistics and analytics

### 📋 Planned (Phase 2)
- [ ] CSV/Excel import/export
- [ ] Advanced search and filtering
- [ ] Bulk alias operations
- [ ] Usage statistics dashboard
- [ ] Theme support
- [ ] User preferences

### 🔮 Future (Phase 3)
- [ ] Performance optimization
- [ ] Accessibility features
- [ ] Plugin system
- [ ] Cloud sync capabilities
- [ ] Advanced analytics

## 🧪 Testing

### Running Tests
```bash
# Run all tests
pytest

# Run GUI-specific tests
pytest tests/test_gui/

# Run with coverage
pytest --cov=src/ocrinvoice/gui
```

### GUI Testing
The GUI includes automated tests using `pytest-qt`:

```bash
# Install test dependencies
pip install pytest-qt

# Run GUI tests
pytest tests/test_gui/ -v
```

## 📚 Documentation

- **Technical Specification**: `docs/architecture/business_aliases_gui_spec.md`
- **API Documentation**: Generated from docstrings
- **User Guide**: This README file

## 🤝 Contributing

1. **Follow the specification** in `docs/architecture/business_aliases_gui_spec.md`
2. **Maintain CLI compatibility** - GUI should use same data formats
3. **Write tests** for new functionality
4. **Follow code standards** - black, flake8, mypy
5. **Update documentation** when adding features

## 📄 License

This project is part of the OCR Invoice Parser system. See the main project license for details.

---

**Ready to manage your business aliases with ease!** 🎉
