# Invoice OCR Parser

A Python tool to extract company names and invoice totals from scanned PDF invoices using OCR (Optical Character Recognition).

## Features

- **Multi-method text extraction**: First tries direct text extraction, then falls back to OCR
- **Company name detection**: Uses pattern matching to identify company names
- **Invoice total extraction**: Finds currency amounts and identifies the total
- **Batch processing**: Process entire folders of PDF invoices
- **Comprehensive reporting**: Detailed results with confidence levels and processing times
- **Error handling**: Robust error handling with detailed logging

## Requirements

### System Dependencies

1. **Tesseract OCR** (required for OCR functionality):
   ```bash
   # macOS (using Homebrew)
   brew install tesseract
   
   # Ubuntu/Debian
   sudo apt-get install tesseract-ocr
   
   # Windows
   # Download from: https://github.com/UB-Mannheim/tesseract/wiki
   ```

2. **Poppler** (required for PDF to image conversion):
   ```bash
   # macOS (using Homebrew)
   brew install poppler
   
   # Ubuntu/Debian
   sudo apt-get install poppler-utils
   
   # Windows
   # Download from: http://blog.alivate.com.au/poppler-windows/
   ```

### Python Dependencies

Install the required Python packages:

```bash
pip install -r requirements.txt
```

## Installation

### Quick Setup (Recommended)

1. Clone or download this repository
2. Run one of the setup scripts:

   **Option 1: Shell script (macOS/Linux)**
   ```bash
   ./setup.sh
   ```

   **Option 2: Batch file (Windows)**
   ```cmd
   setup.bat
   ```

   **Option 3: Python script (cross-platform)**
   ```bash
   python setup.py
   ```

3. Activate the virtual environment:
   ```bash
   # On macOS/Linux:
   source venv/bin/activate
   
   # On Windows:
   venv\Scripts\activate.bat
   ```

### Manual Setup

If you prefer to set up manually:

1. Clone or download this repository
2. Install system dependencies (Tesseract and Poppler)
3. Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate.bat
   ```
4. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Command Line Usage

Process all PDFs in a folder:
```bash
python invoice_ocr_parser.py /path/to/invoices output_results.csv
```

### Python Script Usage

```python
from invoice_ocr_parser import InvoiceOCRParser

# Initialize parser
parser = InvoiceOCRParser()

# Parse a single invoice
result = parser.parse_invoice("path/to/invoice.pdf")
print(f"Company: {result['company_name']}")
print(f"Total: ${result['invoice_total']}")

# Parse all invoices in a folder
results_df = parser.parse_invoices_batch("/path/to/invoices", "results.csv")
```

### Test the Parser

Run the test script to see the parser in action:
```bash
python test_parser.py
```

## How It Works

### 1. Text Extraction Methods

The parser uses multiple methods to extract text from PDFs:

1. **Direct text extraction** (pdfplumber): For text-based PDFs
2. **PyPDF2 fallback**: Alternative text extraction method
3. **OCR processing**: For scanned/image-based PDFs

### 2. Company Name Detection

The parser looks for company names using:
- Pattern matching for common company suffixes (INC, LLC, CORP, etc.)
- Header area analysis (first 10 lines)
- Text prominence analysis

### 3. Invoice Total Detection

The parser identifies invoice totals by:
- Looking for "TOTAL", "AMOUNT", "DUE" keywords
- Finding currency amounts ($, CAD, USD, etc.)
- Selecting the largest amount as the total

### 4. Confidence Levels

- **High**: Direct text extraction successful
- **Medium**: OCR processing required
- **Low**: Errors occurred during processing

## Output Format

The parser returns a dictionary with the following fields:

```python
{
    'file_path': 'path/to/invoice.pdf',
    'company_name': 'Company Name',
    'invoice_total': 123.45,
    'extraction_method': 'text_extraction',  # or 'ocr'
    'confidence': 'high',  # 'high', 'medium', or 'low'
    'processing_time': 2.34,  # seconds
    'error': None  # error message if any
}
```

## CSV Output

When using batch processing, results are saved to a CSV file with columns:
- `file_path`: Path to the PDF file
- `company_name`: Extracted company name
- `invoice_total`: Extracted invoice total
- `extraction_method`: Method used for extraction
- `confidence`: Confidence level
- `processing_time`: Time taken to process
- `error`: Any error messages

## Configuration

### Tesseract Path

If Tesseract is not in your system PATH, specify the path:

```python
parser = InvoiceOCRParser(tesseract_path="/usr/local/bin/tesseract")
```

### Custom Patterns

You can modify the patterns in the `InvoiceOCRParser` class:

```python
# Add custom company name patterns
parser.company_patterns.append(r'YOUR_CUSTOM_PATTERN')

# Add custom total patterns
parser.total_patterns.append(r'YOUR_CUSTOM_TOTAL_PATTERN')
```

## Troubleshooting

### Common Issues

1. **Tesseract not found**:
   - Ensure Tesseract is installed and in PATH
   - Or specify the path when initializing the parser

2. **Poppler not found**:
   - Install poppler-utils package
   - Ensure it's in your system PATH

3. **Poor OCR results**:
   - Ensure PDFs are scanned at 300 DPI or higher
   - Check that images are clear and well-lit
   - Try preprocessing images manually if needed

4. **Memory issues with large PDFs**:
   - Process PDFs one at a time for large files
   - Reduce DPI setting in `convert_pdf_to_images()` if needed

### Performance Tips

- Use SSD storage for faster PDF processing
- Process in batches for large numbers of files
- Monitor memory usage for very large PDFs
- Consider using multiprocessing for batch operations

## Example Results

```
Processing complete!
Total files processed: 50
Successful extractions: 45
Company names found: 42
Totals found: 40

Sample results:
File: invoice1.pdf, Company: ABC Corporation, Total: $1,234.56
File: invoice2.pdf, Company: XYZ Inc, Total: $567.89
File: invoice3.pdf, Company: DEF LLC, Total: $890.12
```

## License

This project is open source and available under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests. 