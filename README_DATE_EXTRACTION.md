# Enhanced Invoice OCR Parser with Date Extraction

## Overview

The Invoice OCR Parser has been enhanced with robust date extraction capabilities and automatic file renaming using the format: `date_business_total`. This enhancement provides a comprehensive solution for processing invoices in both French and English, with advanced OCR error correction and intelligent date parsing.

## New Features

### 1. Date Extraction (`DateExtractor` class)

The new `DateExtractor` class provides robust date extraction from invoice text with the following capabilities:

#### Supported Date Formats
- **Numeric formats**: DD/MM/YYYY, MM/DD/YYYY, YYYY-MM-DD, DD.MM.YYYY
- **Text formats**: "15 janvier 2024", "March 20, 2024", "Jan 15, 2024"
- **Mixed formats**: "15/01/2024", "2024-01-15", "25.12.2023"

#### Language Support
- **French**: janvier, février, mars, avril, mai, juin, juillet, août, septembre, octobre, novembre, décembre
- **English**: January, February, March, April, May, June, July, August, September, October, November, December
- **Abbreviations**: jan, fév, mar, apr, jun, jul, aoû, sept, oct, nov, déc

#### OCR Error Correction
Automatically corrects common OCR misreadings:
- `l`, `I`, `i` → `1`
- `O`, `o` → `0`
- `S`, `s` → `5`
- `G`, `g` → `6`
- `B`, `b` → `8`
- `Z`, `z` → `2`
- `A`, `a` → `4`
- `E`, `e` → `3`
- `T`, `t` → `7`

#### Intelligent Date Detection
- **Priority-based matching**: Dates with keywords (e.g., "Date:", "Facturé") get higher priority
- **Context-aware parsing**: Understands different date formats based on context
- **Validation**: Ensures extracted dates are valid and within reasonable ranges (1900-2100)

### 2. Enhanced File Renaming

Files are now automatically renamed using the format: `date_business_total`

#### Naming Convention
- **Format**: `YYYYMMDD_BusinessName_TotalAmount.pdf`
- **Example**: `20240115_BMR_12550.pdf`

#### Features
- **Filesystem-safe**: Removes problematic characters and spaces
- **Duplicate handling**: Automatically adds suffixes for duplicate filenames
- **Fallback naming**: Uses "unknown", "nodate", "nototal" for missing information
- **Length limiting**: Truncates long business names to 50 characters

### 3. Enhanced Confidence Scoring

The confidence calculation now includes date extraction:
- **High confidence**: 6+ points (company + total + date + text quality)
- **Medium confidence**: 3-5 points
- **Low confidence**: 0-2 points

## Usage Examples

### Single File Processing with Auto-Rename

```python
from invoice_ocr_parser import InvoiceOCRParser

# Initialize parser
parser = InvoiceOCRParser(debug=True)

# Parse and rename a single file
result = parser.parse_invoice("invoice.pdf", auto_rename=True)

print(f"Original file: {result['file_path']}")
print(f"New file: {result['new_file_path']}")
print(f"Company: {result['company_name']}")
print(f"Total: {result['invoice_total']}")
print(f"Date: {result['invoice_date']}")
print(f"Confidence: {result['confidence']}")
```

### Batch Processing with Auto-Rename

```python
# Process all PDFs in a folder and rename them
results_df = parser.parse_and_rename_invoices("invoices_folder/")

# Or use the batch method with auto_rename parameter
results_df = parser.parse_invoices_batch("invoices_folder/", auto_rename=True)

# Save results to CSV
results_df.to_csv("processing_results.csv", index=False)
```

### Manual Date Extraction

```python
from invoice_ocr_parser import DateExtractor

# Extract date from text
text = """
FACTURE
Date: 15 janvier 2024
Client: BMR
Total à payer: 125.50$
"""

date = DateExtractor.extract_date_from_text(text)
print(f"Extracted date: {date}")  # Output: 2024-01-15
```

### Manual File Renaming

```python
# Rename a file manually
new_path = parser.rename_pdf(
    "old_invoice.pdf",
    company_name="BMR",
    invoice_total="125.50",
    invoice_date="2024-01-15"
)
print(f"Renamed to: {new_path}")  # Output: 20240115_BMR_12550.pdf
```

## Advanced Features

### 1. OCR Error Correction Testing

```python
from invoice_ocr_parser import DateExtractor

# Test OCR corrections
corrected = DateExtractor.ocr_correct_date("3l/0l/2024")
print(corrected)  # Output: 31/01/2024
```

### 2. Date Validation

```python
# Check if a date is valid
is_valid = DateExtractor._is_valid_date(2024, 1, 15)
print(is_valid)  # Output: True
```

### 3. Month Name Parsing

```python
# Parse month names
month_num = DateExtractor._parse_month("janvier")
print(month_num)  # Output: 1
```

## Configuration Options

### Parser Initialization

```python
parser = InvoiceOCRParser(
    tesseract_path="/usr/local/bin/tesseract",  # Custom Tesseract path
    debug=True,                                  # Enable debug logging
    use_database=True                           # Enable business database
)
```

### Processing Options

```python
# Parse with expected values for validation
result = parser.parse_invoice(
    "invoice.pdf",
    expected_total=125.50,
    expected_company="BMR",
    auto_rename=True
)
```

## Error Handling

The enhanced parser includes comprehensive error handling:

- **File not found**: Returns error with file path
- **OCR failures**: Falls back to text extraction
- **Invalid dates**: Returns None for date field
- **Duplicate filenames**: Automatically adds suffixes
- **Filesystem errors**: Logs errors and returns original path

## Performance Considerations

- **Date extraction**: Optimized to search only first 30 lines of text
- **OCR correction**: Fast string replacement operations
- **File renaming**: Minimal filesystem operations
- **Batch processing**: Efficient DataFrame operations

## Testing

Run the test suite to verify functionality:

```bash
python test_date_extraction.py
```

The test suite includes:
- Date extraction with various formats
- OCR error correction
- File renaming functionality
- Edge cases and error conditions

## Dependencies

The enhanced parser requires the same dependencies as the original:
- `opencv-python`
- `numpy`
- `pandas`
- `pillow`
- `pytesseract`
- `pdf2image`
- `pdfplumber`
- `PyPDF2`

## Migration from Previous Version

The enhanced parser is backward compatible. Existing code will continue to work, with the following additions:

1. **New return fields**: `invoice_date`, `new_file_path`
2. **New parameters**: `auto_rename` in `parse_invoice()` and `parse_invoices_batch()`
3. **New methods**: `parse_and_rename_invoices()`, `_clean_filename()`

## Best Practices

1. **Always check confidence**: Only auto-rename files with medium or high confidence
2. **Backup files**: Consider backing up original files before batch processing
3. **Test on sample**: Test the parser on a few files before processing large batches
4. **Monitor logs**: Enable debug logging to track extraction quality
5. **Validate results**: Review extracted dates and totals for accuracy

## Troubleshooting

### Common Issues

1. **No date extracted**: Check if date format is supported, enable debug logging
2. **OCR errors**: Verify Tesseract installation and language packs
3. **File renaming fails**: Check file permissions and disk space
4. **Low confidence**: Review OCR quality and text extraction

### Debug Mode

Enable debug logging for detailed information:

```python
parser = InvoiceOCRParser(debug=True)
```

This will show:
- OCR extraction details
- Date parsing steps
- Confidence calculation
- File renaming operations 