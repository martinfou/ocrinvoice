# Getting Started Guide

Welcome to the Invoice OCR Parser! This guide will help you get up and running quickly with both the command-line interface (CLI) and the graphical user interface (GUI).

## Prerequisites

Before you begin, make sure you have:

- **Python 3.8+** installed
- **Tesseract OCR** installed (see installation instructions below)
- **PyQt6** (for GUI version)
- Basic familiarity with command line tools

## Installation

### Step 1: Install Python Dependencies

```bash
# Clone the repository
git clone <repository-url>
cd ocrinvoice

# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install the package
pip install -e .
```

### Step 2: Install Tesseract OCR

**macOS:**
```bash
brew install tesseract
```

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
sudo apt-get install tesseract-ocr-fra  # For French language support
```

**Windows:**
1. Download the installer from [GitHub releases](https://github.com/UB-Mannheim/tesseract/wiki)
2. Run the installer
3. Add Tesseract to your PATH environment variable

**Verify Installation:**
```bash
tesseract --version
```

## Running the Application

### Option 1: Graphical User Interface (GUI) - Recommended for Beginners

The GUI provides an intuitive interface for processing PDF invoices:

```bash
# Launch the GUI application
python run_ocr_gui.py
```

**GUI Features:**
- Drag-and-drop PDF file support
- Real-time PDF preview
- Interactive data editing
- Visual confidence indicators
- File naming templates
- Settings configuration

**Quick Start with GUI:**
1. Launch the application
2. Drag a PDF invoice onto the drop area
3. Review extracted data in the right panel
4. Edit any incorrect fields
5. Use the File Naming tab to rename the file

### Option 2: Command Line Interface (CLI)

For advanced users and batch processing:

```bash
# Basic parse
ocrinvoice parse your-invoice.pdf
```

## Your First Invoice Parse

### Using the GUI (Recommended)

1. **Launch the GUI**: `python run_ocr_gui.py`
2. **Select a PDF**: Use the file browser or drag-and-drop
3. **Review Results**: Check the extracted data table
4. **Edit if Needed**: Modify any incorrect fields
5. **Rename File**: Use the File Naming tab to rename

### Using the CLI

1. **Prepare Your Invoice**: Ensure it's scanned at 300 DPI or higher
2. **Run the Parser**: `ocrinvoice parse your-invoice.pdf`
3. **Review the Results**: Check the JSON output

### Expected Results

You should see output like this:
```json
{
  "company": "HYDRO-QUÉBEC",
  "total": 137.50,
  "date": "2023-01-15",
  "invoice_number": "INV-2023-001",
  "confidence": 0.85
}
```

## Understanding the Output

| Field | Description | Example |
|-------|-------------|---------|
| `company` | Business name | "HYDRO-QUÉBEC" |
| `total` | Invoice amount (decimal) | 137.50 |
| `date` | Invoice date (YYYY-MM-DD) | "2023-01-15" |
| `invoice_number` | Invoice identifier | "INV-2023-001" |
| `confidence` | Extraction confidence (0.0-1.0) | 0.85 |

**Confidence Indicators (GUI):**
- 🟢 **Green**: High confidence (80%+)
- 🟡 **Yellow**: Medium confidence (60-79%)
- 🔴 **Red**: Low confidence (<60%)

## Common First-Time Issues

### Issue: "Tesseract not found"
**Solution:** Install Tesseract OCR (see installation instructions above)

### Issue: "No data extracted"
**Solutions:**
```bash
# Check if text can be extracted
ocrinvoice parse invoice.pdf --show-text

# Try with verbose output
ocrinvoice parse invoice.pdf --verbose
```

### Issue: "Business name not recognized"
**Solution:** Add the business to your aliases
```bash
ocrinvoice aliases add "Company Name" "OFFICIAL_NAME"
```

### Issue: GUI won't start
**Solutions:**
1. Ensure PyQt6 is installed: `pip install PyQt6`
2. Check Python version: `python --version`
3. Verify all dependencies: `pip list`

## Next Steps

Once you've successfully parsed your first invoice:

### GUI Users:
1. **Explore the interface** - try all three tabs
2. **Set up file naming templates** in the File Naming tab
3. **Configure settings** in the Settings tab
4. **Try different PDF files** to test accuracy
5. **Use keyboard shortcuts** for faster navigation

### CLI Users:
1. **Try batch processing** multiple invoices
2. **Set up business aliases** for consistent naming
3. **Configure the system** for your specific needs
4. **Explore advanced features** like OCR correction
5. **Try file renaming** to automatically organize your invoices

## File Renaming Feature

### GUI Method:
1. Go to the **File Naming** tab
2. Configure your naming template
3. Click **Rename File** to apply

### CLI Method:
```bash
# Rename a single file
ocrinvoice parse invoice.pdf --rename

# Preview what would be renamed (dry run)
ocrinvoice parse invoice.pdf --rename --dry-run

# Rename multiple files
ocrinvoice batch invoices/ --rename
```

Files are renamed using the format: `{date}_{company}_{total}.pdf`

**Example:** `2023-01-15_HYDRO-QUÉBEC_137.50.pdf`

## Performance Tips

1. **File Size**: Smaller PDF files process faster
2. **Text Quality**: Clear, high-resolution text improves accuracy
3. **System Resources**: Close other applications to free up memory
4. **Batch Processing**: For multiple files, use the CLI version

## Getting Help

- **GUI Users**: Press `F1` in the application for keyboard shortcuts
- **CLI Users**: Run `ocrinvoice --help` for command overview
- Run `ocrinvoice parse --help` for specific command help
- Check the [Troubleshooting Guide](./troubleshooting.md) for common issues
- Review the [CLI Reference](./cli_reference.md) for complete command documentation
- See the [Configuration Guide](./configuration.md) for system setup
- Read the [GUI Guide](./gui_guide.md) for detailed GUI instructions
