# Getting Started Guide

Welcome to the Invoice OCR Parser! This guide will help you get up and running quickly.

## Prerequisites

Before you begin, make sure you have:

- **Python 3.8+** installed
- **Tesseract OCR** installed (see installation instructions below)
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

## Your First Invoice Parse

### Step 1: Prepare Your Invoice

Make sure your PDF invoice is:
- Scanned at 300 DPI or higher
- In a readable format (not heavily skewed or damaged)
- Contains clear text (not handwritten)

### Step 2: Run the Parser

```bash
# Basic parse
ocrinvoice parse your-invoice.pdf
```

### Step 3: Review the Results

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

## Next Steps

Once you've successfully parsed your first invoice:

1. **Try batch processing** multiple invoices
2. **Set up business aliases** for consistent naming
3. **Configure the system** for your specific needs
4. **Explore advanced features** like OCR correction

## Getting Help

- Run `ocrinvoice --help` for command overview
- Run `ocrinvoice parse --help` for specific command help
- Check the [Troubleshooting Guide](./troubleshooting.md) for common issues
- Review the [CLI Reference](./cli_reference.md) for complete command documentation
- See the [Configuration Guide](./configuration.md) for system setup
