# OCR Invoice Parser - Desktop GUI Guide

> **Complete guide to using the OCR Invoice Parser desktop application**

The OCR Invoice Parser now includes a powerful desktop GUI application that provides an intuitive interface for processing PDF invoices with advanced file management capabilities.

## 🚀 Quick Start

### Launching the GUI

```bash
# Launch the desktop application
python -m src.ocrinvoice.gui.ocr_main_window
```

The application will open with three main tabs:
- **Single PDF**: Process individual PDF invoices
- **File Naming**: Manage file naming templates and preview
- **Settings**: Configure application settings

## 📄 Single PDF Processing

### Loading a PDF

1. **Select PDF**: Click "Select PDF" or drag and drop a PDF file
2. **Processing**: The application will automatically start OCR processing
3. **Progress**: Watch the progress bar during processing
4. **Results**: View extracted data in the data panel

### Data Review

The extracted data is displayed in an editable table showing:
- **Company Name**: Extracted business name
- **Total Amount**: Invoice total with currency formatting
- **Invoice Date**: Formatted date
- **Invoice Number**: Invoice identifier
- **Parser Type**: Type of document processed
- **Confidence**: Overall extraction confidence
- **Validation Status**: Whether the extraction is valid

### Data Export

- **Export Data**: Click to save extracted data in JSON/CSV format
- **Clear Data**: Reset the data panel for new processing

## 🏷️ File Naming System (Sprint 3)

The File Naming tab provides comprehensive file management capabilities with custom templates and live preview.

### Template Builder

#### Creating Custom Templates

1. **Template Format**: Enter your desired naming pattern
2. **Add Fields**: Use the dropdown to add template variables:
   - `{documentType}`: Document type (facture, relevé, etc.)
   - `{company}`: Company name
   - `{date}`: Invoice date
   - `{total}`: Total amount
   - `{invoice_number}`: Invoice number
   - Custom text

#### Template Presets

Choose from predefined templates:
- **Default**: `{documentType}_{company}_{date}_{total}.pdf`
- **Simple**: `{company}_{date}.pdf`
- **Detailed**: `{date}_{company}_{total}_{invoice_number}.pdf`
- **Custom**: Create your own pattern

### Live Preview

The preview section shows:
- **Original Filename**: Current file name
- **New Filename**: Preview of renamed file
- **Template Variables**: Available data for the template
- **Options**: Current settings (rename enabled, dry run, backup)

### File Management Options

#### Document Type
Select the document type for your template:
- `facture` (Invoice)
- `relevé` (Statement)
- `invoice` (English)
- `statement` (English)

#### Renaming Options
- **Enable File Renaming**: Toggle file renaming on/off
- **Create Backup**: Create backup of original file before renaming
- **Dry Run**: Preview rename operations without executing

#### Backup Settings
- **Backup Location**: Choose custom backup directory (optional)
- **Same Folder**: Default backup location

### Conflict Resolution

When a file with the same name already exists:
1. **Add Timestamp**: Automatically add timestamp to make filename unique
2. **Overwrite**: Replace existing file
3. **Cancel**: Abort the rename operation

### File Operations

#### Rename File
- Click "Rename File" to apply the naming template
- The system will check for conflicts and handle them appropriately
- Success/failure messages are displayed

#### Open Folder
- Click "Open Folder" to open the directory containing the file
- Works on macOS, Windows, and Linux

## ⚙️ Settings Configuration

### OCR Settings
- **Language**: Select OCR language (eng, fra, spa, deu)
- **Default**: English

### Output Settings
- **Output Directory**: Set default output location for processed files
- **Browse**: Select directory using file dialog

### Business Settings
- **Business Alias File**: Path to business alias configuration
- **Browse**: Select alias file using file dialog

### Save/Cancel
- **Save Settings**: Apply configuration changes
- **Cancel**: Discard changes and revert to previous settings

## 🔧 Advanced Features

### Template Validation

The system provides real-time validation:
- **Required Fields**: Ensures all necessary template variables are present
- **Invalid Characters**: Checks for forbidden filename characters
- **File Extension**: Ensures template ends with `.pdf`
- **Length Limits**: Validates filename length (max 260 characters)

### Error Handling

Comprehensive error handling includes:
- **File Loading Errors**: Clear messages for invalid PDFs
- **OCR Processing Errors**: Detailed error information
- **Template Validation**: Real-time feedback on template issues
- **File Operation Errors**: Graceful handling of file system errors

### Integration with CLI

The GUI maintains full compatibility with the CLI:
- **Same Data Formats**: GUI reads/writes same JSON/CSV formats
- **Shared Configuration**: Settings are compatible between CLI and GUI
- **Business Aliases**: Uses same alias system as CLI
- **File Management**: Same naming patterns and options

## 📋 Workflow Examples

### Example 1: Basic Invoice Processing

1. **Launch GUI**: `python -m src.ocrinvoice.gui.ocr_main_window`
2. **Load PDF**: Drag and drop invoice.pdf
3. **Review Data**: Check extracted information
4. **Configure Naming**: Set template to `{company}_{date}.pdf`
5. **Rename File**: Apply naming with conflict resolution
6. **Export Data**: Save results as JSON

### Example 2: Custom Template

1. **Create Template**: `{documentType}_{company}_{total}_{invoice_number}.pdf`
2. **Set Document Type**: Choose "facture"
3. **Live Preview**: See `facture_HYDRO-QUÉBEC_137.50_INV-001.pdf`
4. **Enable Backup**: Check backup option
5. **Rename**: Apply with backup creation

### Example 3: Batch Preparation

1. **Configure Template**: Set up naming pattern for batch processing
2. **Test with Single File**: Verify template works correctly
3. **Save Settings**: Store configuration for batch use
4. **Use CLI for Batch**: Apply same settings to batch processing

## 🚨 Troubleshooting

### Common Issues

**GUI won't launch**
```bash
# Install PyQt6
pip install PyQt6

# Check Python version (requires 3.8+)
python --version
```

**PDF won't load**
- Ensure file is a valid PDF
- Check file permissions
- Try a different PDF file

**OCR processing fails**
- Verify Tesseract is installed
- Check OCR language settings
- Review error messages in status bar

**Template validation errors**
- Ensure template ends with `.pdf`
- Check for invalid characters (`<>:"/\|?*`)
- Include required template variables

**File naming conflicts**
- Use timestamp option for unique names
- Check file permissions in target directory
- Verify template generates valid filenames

### Getting Help

- **Status Bar**: Check for error messages and status updates
- **Error Dialogs**: Read detailed error information
- **Validation Feedback**: Review template validation messages
- **Logs**: Check console output for debugging information

## 🎯 Best Practices

### Template Design
- **Keep it Simple**: Start with basic templates
- **Use Descriptive Names**: Include key information in filename
- **Test First**: Use dry run to preview results
- **Backup Important Files**: Enable backup for critical documents

### File Management
- **Organize by Date**: Include dates in templates for chronological sorting
- **Company Prefixes**: Use company names for easy identification
- **Consistent Formatting**: Maintain consistent naming across projects
- **Regular Backups**: Use backup features for important files

### Performance
- **Single File Processing**: Use GUI for individual files
- **Batch Processing**: Use CLI for large numbers of files
- **Memory Management**: Close large PDFs when done
- **Regular Updates**: Keep application and dependencies updated

## 🔄 Integration with CLI

The GUI and CLI work seamlessly together:

### Shared Configuration
```bash
# CLI uses same settings as GUI
ocrinvoice parse invoice.pdf --rename
```

### Data Compatibility
```bash
# GUI can read CLI-generated data
# CLI can process GUI-configured files
```

### Workflow Integration
```bash
# Configure in GUI, use in CLI
# Process in CLI, review in GUI
# Export from GUI, import to CLI
```

---

**Ready to get started?** Launch the GUI with `python -m src.ocrinvoice.gui.ocr_main_window` and begin processing your invoices with the powerful file management system! 🚀
