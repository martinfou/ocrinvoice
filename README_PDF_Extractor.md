# PDF Text Extractor Tool

A tool to extract text from all PDFs in a directory and save the results to an Excel file for keyword review.

## Features

- Extracts text from all PDF files in a directory (including subdirectories)
- Saves results to a timestamped Excel file
- Supports both PyPDF2 and pdfplumber libraries
- Configurable path via command line or .env file
- Provides detailed statistics and progress tracking
- Auto-formats Excel output with proper column widths

## Installation

The tool uses the main project virtual environment (`venv`). Dependencies are already installed:

```bash
# Activate the main project environment
source venv/bin/activate

# Dependencies are already installed:
# - pandas
# - openpyxl
# - python-dotenv
# - PyPDF2
```

## Usage

### Basic Usage
```bash
# Activate the main project environment
source venv/bin/activate

# Use default path from .env file or fallback to /Volumes/T7/Dropbox/scan-snap/facture
python3 pdf_text_extractor_cli.py

# Specify a custom path
python3 pdf_text_extractor_cli.py /path/to/your/pdfs

# Show help
python3 pdf_text_extractor_cli.py --help
```

### Configuration

The tool will automatically create a `.env` file in the current directory if one doesn't exist, with the current directory as the default PDF path:

```
PDF_PATH=/your/default/pdf/path
```

If no `.env` file exists, the tool will create one with the current directory as the default path.

## Output

The tool creates an Excel file with the following columns:

- **filename**: Name of the PDF file
- **filepath**: Relative path from the search directory
- **filesize_mb**: File size in megabytes
- **text**: Extracted text content
- **text_length**: Number of characters in extracted text
- **extraction_time**: Timestamp when extraction was performed

## Example Output

```
📝 Created .env file with default path: /Volumes/T7/src/ocrinvoice
📁 Using path from .env/default: /Volumes/T7/src/ocrinvoice

🔍 Searching for PDF files in: /Volumes/T7/src/ocrinvoice
✅ Found 15 PDF file(s)

📄 Extracting text using PyPDF2...
  [1/15] Processing: invoice_001.pdf
  [2/15] Processing: receipt_2024.pdf
  ...

💾 Saving results to: pdf_texts_20241201_143022.xlsx
✅ Successfully extracted text from 15 PDF(s)
📊 Summary:
   - Total files processed: 15
   - Total text extracted: 45,230 characters
   - Output file: pdf_texts_20241201_143022.xlsx
```

## Next Steps

1. Open the generated Excel file
2. Review the 'text' column for potential keywords
3. Use Excel's search/filter features to find specific terms
4. Identify patterns in business names, amounts, dates, etc.

## Troubleshooting

- **No PDFs found**: Check that the directory path is correct and contains PDF files
- **Extraction errors**: Some PDFs may be image-based or password-protected
- **Missing dependencies**: Make sure to activate the main `venv` environment before running

## Dependencies

- pandas: Data manipulation and Excel export
- openpyxl: Excel file handling
- python-dotenv: Environment variable management
- PyPDF2: PDF text extraction (primary)
- pdfplumber: Alternative PDF extraction library (fallback)
