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

1. **Install Tesseract OCR**:
   - **Windows**: Download from https://github.com/tesseract-ocr/tesseract
   - **macOS**: `brew install tesseract`
   - **Linux**: `sudo apt-get install tesseract-ocr`

2. **Install Python Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Launch the Application**:
   ```bash
   python run_ocr_gui.py
   ```

## Main Interface

The application has three main tabs:

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
4. **Edit if Needed**: Modify any extracted fields
5. **Rename File**: Use the file naming template to rename the file

#### Data Display
The right panel shows extracted data in a table format:

| Field | Value | Confidence |
|-------|-------|------------|
| Company Name | Extracted company | 🟢 95% |
| Total Amount | $123.45 | 🟢 92% |
| Invoice Date | 2025-01-15 | 🟡 78% |
| Invoice Number | INV-001 | 🔴 45% |

**Confidence Indicators**:
- 🟢 **Green**: High confidence (80%+)
- 🟡 **Yellow**: Medium confidence (60-79%)
- 🔴 **Red**: Low confidence (<60%)

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

### 3. Settings Tab

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
| `Ctrl+3` | Switch to Settings tab |
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

## Business Alias System

The application integrates with the existing business alias system:

- **Automatic Mapping**: Company names are automatically mapped to aliases
- **Alias File**: Configure custom business name mappings
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
