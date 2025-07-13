# OCR Invoice Parser GUI - User Guide

## Overview

The OCR Invoice Parser GUI is a desktop application that extracts structured data from PDF invoices using Optical Character Recognition (OCR). This guide covers all features available in the MVP (Minimum Viable Product) version.

## Getting Started

### System Requirements

- **Operating System**: Windows 10+, macOS 10.14+, or Linux
- **Python**: 3.8 or higher
- **Tesseract OCR**: Must be installed and available in system PATH
- **Memory**: At least 4GB RAM recommended
- **Storage**: 100MB free space

### Installation

#### Step 1: Create a Virtual Environment (Recommended)

It's recommended to create a virtual environment to isolate the project dependencies:

**Windows:**
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# Verify activation (you should see (venv) in your prompt)
```

**macOS/Linux:**
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Verify activation (you should see (venv) in your prompt)
```

#### Step 2: Install Tesseract OCR

**Windows:**
- Download from https://github.com/tesseract-ocr/tesseract
- Add Tesseract to your system PATH

**macOS:**
```bash
brew install tesseract
```

**Linux:**
```bash
sudo apt-get install tesseract-ocr
```

#### Step 3: Install Python Dependencies

This project uses `pyproject.toml` for dependency management (modern Python packaging). Install dependencies using:

```bash
# Install the project and its dependencies
pip install -e .

# Or install with development dependencies (for contributors)
pip install -e ".[dev]"
```

**Note**: The project doesn't use a traditional `requirements.txt` file. Instead, dependencies are defined in `pyproject.toml` at the root of the project. This is the modern Python standard for package management.

#### Step 4: Launch the Application

```bash
python run_ocr_gui.py
```

**Alternative Launch Methods:**
```bash
# If installed with pip install -e .
python -m ocrinvoice.gui.ocr_main_window

# Or use the provided launcher script
python run_ocr_gui.py
```

#### Step 5: Deactivate Virtual Environment (When Done)

When you're finished using the application, deactivate the virtual environment:

```bash
deactivate
```

### Scripts Folder

The project includes a `scripts/` folder with helpful utilities and automation tools:

#### Setup Scripts
**Windows:**
```bash
scripts\setup.bat
```

**macOS/Linux:**
```bash
chmod +x scripts/setup.sh
./scripts/setup.sh
```

These setup scripts will:
1. Create a virtual environment
2. Install Tesseract OCR (if not already installed)
3. Install Python dependencies
4. Launch the application

#### Additional Scripts

**`scripts/demo_mvp.py`** - Interactive demonstration of MVP features
```bash
python scripts/demo_mvp.py
```
This script provides a guided tour of all GUI features and capabilities.

**`scripts/install_dependencies.py`** - Advanced dependency installer
```bash
python scripts/install_dependencies.py
```
Handles complex dependency installation scenarios and provides detailed feedback.

**`scripts/validate_links.py`** - Documentation link validator
```bash
python scripts/validate_links.py
```
Validates links in documentation files (for developers).

### Quick Setup Script

### Troubleshooting Installation

#### Virtual Environment Issues
- **"python not found"**: Ensure Python 3.8+ is installed and in your PATH
- **"venv module not found"**: Install python3-venv package (Linux: `sudo apt-get install python3-venv`)
- **Activation fails**: Use the correct activation command for your OS

#### Dependency Installation Issues
- **"pip install -e . fails"**: Ensure you're in the project root directory
- **"build tools not found"**: Install build tools: `pip install build setuptools wheel`
- **"PyQt6 installation fails"**: On Linux, install system dependencies: `sudo apt-get install python3-pyqt6`

#### Tesseract Issues
- **"tesseract not found"**: Ensure Tesseract is installed and added to system PATH
- **"tesseract version"**: Verify installation by running `tesseract --version`

## Main Interface

The application has five main tabs:

### 1. Single PDF Tab

This is the primary interface for processing individual PDF invoices.

#### File Selection
- **Select PDF File Button**: Click to browse and select a PDF file
- **Drag & Drop Area**: Drag PDF files directly onto the application
- **Supported Formats**: PDF files (single or multi-page)

#### Processing Workflow
1. **Select a PDF**: Use the file browser or drag-and-drop
2. **OCR Processing**: The application automatically processes the PDF
3. **Review Results**: Check extracted data in the right panel
4. **Edit if Needed**: Double-click any value to edit it
5. **Real-time Preview**: See file name changes instantly as you edit
6. **Rename File**: Use the file naming template to rename the file

#### Real-time File Naming
- **Live Updates**: As you edit data in the table, the file name preview updates automatically
- **Instant Feedback**: See exactly how your changes affect the final file name
- **Template Integration**: Changes are reflected in all file naming templates
- **Status Updates**: Status bar shows when data has been updated

#### Data Display
The right panel shows extracted data in an **editable table format**:

| Field | Value | Confidence |
|-------|-------|------------|
| Company Name | Extracted company | 🟢 95% |
| Total Amount | $123.45 | 🟢 92% |
| Invoice Date | 2025-01-15 | 🟡 78% |
| Invoice Number | INV-001 | 🔴 45% |

**Editable Fields**:
- **Value Column**: Double-click any value to edit it
- **Real-time Updates**: Changes automatically update the file name preview
- **Smart Formatting**: Currency and percentage values are automatically formatted
- **Field Names & Confidence**: These columns are read-only for data integrity

**Confidence Indicators**:
- 🟢 **Green**: High confidence (80%+)
- 🟡 **Yellow**: Medium confidence (60-79%)
- 🔴 **Red**: Low confidence (<60%)

**Editing Tips**:
- **Company Names**: Edit to correct OCR errors or improve accuracy
- **Amounts**: Enter numbers with or without currency symbols (e.g., "123.45" or "$123.45")
- **Dates**: Use standard date formats (e.g., "2025-01-15")
- **Invoice Numbers**: Correct any OCR misreads
- **Confidence**: Shows OCR confidence but cannot be edited (maintains data integrity)

#### Action Buttons
- **💾 Export Data**: Export extracted data to JSON/CSV (coming in future sprints)
- **🗑️ Clear Data**: Clear all extracted data
- **📝 Rename File**: Rename the current file using the template

### 2. File Naming Tab

Configure how processed files are renamed.

#### Template Builder
- **Template Field**: Shows the current naming template
- **Available Fields**: List of fields that can be used in templates
- **Live Preview**: Shows how the current file will be renamed

#### Template Variables
- `{company}`: Company name
- `{date}`: Invoice date
- `{total}`: Total amount
- `{invoice_number}`: Invoice number
- `{original_name}`: Original filename

#### Example Templates
- `{date}_{company}_{total}.pdf` → `2025-01-15_Rona_$123.45.pdf`
- `{company}_{total}_{invoice_number}.pdf` → `Rona_$123.45_INV-001.pdf`

#### File Management
- **Rename File**: Apply the template to rename the current file
- **Open Containing Folder**: Open the folder containing the processed file
- **Backup Options**: Create backup copies before renaming

### 3. Business Aliases Tab

Manage business name aliases for improved OCR accuracy.

#### Alias Management
- **Add Alias**: Create new company name mappings
- **Edit Alias**: Modify existing aliases
- **Delete Alias**: Remove aliases
- **Search Aliases**: Find specific aliases quickly

#### Alias Table Features
- **Company Name**: The name as it appears on invoices
- **Canonical Name**: The official business name (dropdown selection)
- **Match Type**: Exact, Partial, or Fuzzy matching
- **Usage Statistics**: Track how often aliases are used

#### Canonical Name Selection
- **Dropdown Only**: Select from existing official names only
- **Data Integrity**: Prevents invalid canonical name references
- **Auto-completion**: Quick selection from available options

### 4. Official Names Tab

Manage canonical business names that all aliases resolve to.

#### Official Name Management
- **Add Official Name**: Create new canonical business names
- **Edit Official Name**: Modify existing official names
- **Delete Official Name**: Remove official names (cascades to aliases)
- **Search Official Names**: Find specific official names quickly

#### Official Name Table Features
- **Official Name**: The canonical business name
- **Usage Count**: How many aliases reference this name
- **Last Used**: When this name was last referenced

#### Cascade Updates
- **Automatic Updates**: When you edit an official name, all related aliases are updated
- **Impact Warnings**: Shows which aliases will be affected by changes
- **Data Integrity**: Ensures all aliases reference valid official names

### 5. Settings Tab

Configure application settings and preferences.

#### OCR Settings
- **Output Directory**: Where processed files are saved
- **Business Alias File**: JSON file containing company name mappings
- **OCR Language**: Language for OCR processing (default: English)

#### File Management Settings
- **Default Template**: Default file naming template
- **Backup Files**: Whether to create backup copies
- **Overwrite Protection**: Handle file conflicts

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+O` | Open PDF file |
| `Ctrl+E` | Export data |
| `Ctrl+Q` | Quit application |
| `Ctrl+1` | Switch to Single PDF tab |
| `Ctrl+2` | Switch to File Naming tab |
| `Ctrl+3` | Switch to Business Aliases tab |
| `Ctrl+4` | Switch to Official Names tab |
| `Ctrl+5` | Switch to Settings tab |
| `F1` | Show keyboard shortcuts help |

## PDF Preview Features

When viewing a PDF in the preview panel:

| Shortcut | Action |
|----------|--------|
| `Ctrl++` | Zoom in |
| `Ctrl+-` | Zoom out |
| `Ctrl+0` | Reset zoom to 100% |
| `Ctrl+Wheel` | Zoom with mouse wheel |
| Mouse drag | Pan around the document |

## Troubleshooting

### Common Issues

#### 1. "Tesseract not found" Error
**Problem**: OCR engine is not installed or not in PATH
**Solution**:
1. Install Tesseract OCR for your operating system
2. Add Tesseract to your system PATH
3. Restart the application

#### 2. "PDF corrupted" Error
**Problem**: The PDF file is corrupted or not a valid PDF
**Solution**:
1. Verify the file opens in a PDF viewer
2. Try to obtain a new copy of the file
3. Check if the file is password-protected

#### 3. Low OCR Accuracy
**Problem**: Extracted data has low confidence scores
**Solution**:
1. Ensure the PDF has clear, high-resolution text
2. Check that the PDF is not scanned at a low resolution
3. Verify the text is not rotated or skewed
4. Try processing a different page if multi-page

#### 4. Application Freezes
**Problem**: Application becomes unresponsive during processing
**Solution**:
1. Wait for processing to complete (large files take longer)
2. Check available system memory
3. Try with a smaller PDF file
4. Restart the application if necessary

### Performance Tips

1. **File Size**: Smaller PDF files process faster
2. **Text Quality**: Clear, high-resolution text improves accuracy
3. **System Resources**: Close other applications to free up memory
4. **Batch Processing**: For multiple files, use the CLI version (coming in future sprints)

## Data Export

The MVP version includes basic data export functionality:

- **JSON Format**: Structured data export
- **CSV Format**: Tabular data export
- **Export Location**: Choose where to save exported files

*Note: Full export functionality will be available in future sprints*

## Business Alias & Official Names System

The application integrates with the existing business alias and official names system:

- **Automatic Mapping**: Company names are automatically mapped to aliases
- **Official Names**: Canonical business names that all aliases resolve to
- **Data Integrity**: Ensures all aliases reference valid official names
- **Cascade Updates**: Changes to official names automatically update related aliases
- **Fallback**: Unknown companies are marked as "Unknown"

## File Management

### Supported Operations
- **File Renaming**: Automatic renaming based on templates
- **Backup Creation**: Optional backup copies before renaming
- **Conflict Resolution**: Handle duplicate filenames
- **Folder Access**: Quick access to processed files

### File Formats
- **Input**: PDF files only
- **Output**: Renamed PDF files
- **Data**: JSON/CSV export files

## Integration with CLI

The GUI is fully compatible with the existing CLI version:

- **Shared Configuration**: Both use the same settings
- **Data Compatibility**: Same data formats and structures
- **Alias System**: Shared business alias mappings
- **File Operations**: Compatible file naming and management

## Future Features

The following features are planned for future sprints:

### Phase 2: Batch Processing
- Process multiple PDF files at once
- Batch progress tracking
- Batch error handling and reporting

### Phase 3: Advanced Features
- PDF text search functionality
- Advanced filtering and sorting
- Custom field extraction rules

### Phase 4: Enterprise Features
- Performance optimizations
- Advanced reporting
- API integration capabilities

## Support

For technical support or feature requests:

1. **Documentation**: Check this user guide first
2. **Troubleshooting**: Review the troubleshooting section
3. **Issues**: Report bugs or issues through the project repository
4. **Feature Requests**: Submit feature requests for future sprints

## Version Information

- **Current Version**: 1.0.0 (MVP)
- **Development Phase**: Sprint 4 - MVP Polish & Testing
- **Compatibility**: Compatible with CLI version 1.0.0

---

*This user guide covers the MVP version of the OCR Invoice Parser GUI. For the latest features and updates, please refer to the project documentation.*
