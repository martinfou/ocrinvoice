# Invoice OCR Parser Test Suite

A comprehensive testing system for validating and improving the accuracy of the invoice OCR parser.

## Overview

The test suite allows you to:
- **Add test cases** with expected company names and invoice totals
- **Run automated tests** against your PDF invoices
- **Generate detailed reports** showing accuracy and performance
- **Iteratively improve** the parser based on test results

## Quick Start

### 1. Auto-Generate Test Cases from Your Facture Folder

```bash
# Generate test cases from your facture folder
python quick_test_setup.py

# With interactive review
python quick_test_setup.py --review
```

This will:
- Scan your facture folder for PDF files
- Parse filenames to extract expected company names and totals
- Create a `auto_test_data.json` file with test cases
- Optionally allow you to review and edit the expected values

### 2. Run the Test Suite

```bash
# Run all tests and generate report
python test_suite.py --run

# Run with custom report filename
python test_suite.py --run --report my_test_results.csv
```

### 3. Add Individual Test Cases

```bash
# Add a single test case
python test_suite.py --pdf "path/to/invoice.pdf" --company "COMPANY NAME" --total 123.45

# Interactive mode to add multiple test cases
python test_suite.py --add
```

## Test Data Format

Test cases are stored in JSON format:

```json
{
  "tests": [
    {
      "pdf_path": "/path/to/invoice.pdf",
      "expected_company": "COMPANY NAME",
      "expected_total": 123.45,
      "description": "Optional description",
      "added_date": "2025-01-27T10:00:00"
    }
  ]
}
```

## Test Results

The test suite generates detailed reports including:

### Summary Statistics
- **Total Tests**: Number of test cases run
- **Company Matches**: Percentage of correctly identified companies
- **Total Matches**: Percentage of correctly identified invoice totals
- **Both Match**: Percentage where both company and total are correct
- **Errors**: Number of processing errors

### Detailed CSV Report
Each test result includes:
- `pdf_path`: Path to the PDF file
- `expected_company`: Expected company name
- `expected_total`: Expected invoice total
- `actual_company`: Extracted company name
- `actual_total`: Extracted invoice total
- `company_match`: Whether company name matches (True/False)
- `total_match`: Whether total matches (True/False)
- `extraction_method`: Method used (text_extraction/ocr)
- `confidence`: Confidence level (high/medium/low)
- `processing_time`: Time taken to process
- `error`: Any error messages

## Workflow for Improving Accuracy

### 1. Initial Setup
```bash
# Generate initial test cases
python quick_test_setup.py --review

# Run initial tests
python test_suite.py --run
```

### 2. Analyze Results
- Review the CSV report to identify patterns in failures
- Look for common issues:
  - Company names not being extracted correctly
  - Invoice totals being missed or misidentified
  - OCR quality issues
  - Specific file formats causing problems

### 3. Improve the Parser
Based on test results, you can:
- **Add new patterns** to `invoice_ocr_parser.py`:
  ```python
  # Add custom company patterns
  parser.company_patterns.append(r'YOUR_CUSTOM_PATTERN')
  
  # Add custom total patterns
  parser.total_patterns.append(r'YOUR_CUSTOM_TOTAL_PATTERN')
  ```
- **Adjust OCR settings** for better text recognition
- **Add preprocessing steps** for specific file types

### 4. Re-run Tests
```bash
# After making improvements
python test_suite.py --run
```

### 5. Iterate
Continue the cycle of testing → analyzing → improving → testing until you reach desired accuracy.

## Advanced Usage

### Custom Test Data Files
```bash
# Use a custom test data file
python test_suite.py --run --test-data my_custom_tests.json
```

### Batch Processing
```bash
# Process multiple folders
for folder in folder1 folder2 folder3; do
    python quick_test_setup.py --folder "$folder" --output "${folder}_tests.json"
    python test_suite.py --run --test-data "${folder}_tests.json" --report "${folder}_results.csv"
done
```

### Continuous Integration
You can integrate the test suite into your development workflow:
```bash
# Run tests and fail if accuracy drops below threshold
python test_suite.py --run --min-accuracy 0.85
```

## Troubleshooting

### Common Issues

1. **Test cases not being parsed correctly**:
   - Review the filename patterns in `quick_test_setup.py`
   - Add custom patterns for your specific naming convention
   - Use interactive mode to manually correct expected values

2. **Poor OCR results**:
   - Ensure Tesseract is installed and configured correctly
   - Check that PDFs are scanned at sufficient resolution (300 DPI+)
   - Consider preprocessing images for better OCR results

3. **Memory issues with large test suites**:
   - Process tests in smaller batches
   - Use SSD storage for faster processing
   - Monitor system resources during testing

### Performance Tips

- **Use SSD storage** for faster PDF processing
- **Process in batches** for large numbers of files
- **Monitor memory usage** for very large PDFs
- **Consider multiprocessing** for batch operations

## Example Workflow

Here's a complete example workflow:

```bash
# 1. Set up environment
./setup.sh

# 2. Generate initial test cases
python quick_test_setup.py --review

# 3. Run initial tests
python test_suite.py --run

# 4. Review results and identify issues
# (Open test_report.csv in Excel/Google Sheets)

# 5. Make improvements to parser
# (Edit invoice_ocr_parser.py based on findings)

# 6. Re-run tests
python test_suite.py --run

# 7. Compare results
# (Compare old vs new test reports)

# 8. Add more test cases as needed
python test_suite.py --add
```

## File Structure

```
ocrinvoice/
├── test_suite.py              # Main test suite
├── quick_test_setup.py        # Auto-generate test cases
├── sample_test_data.json      # Example test data format
└── TEST_SUITE_README.md       # This documentation

/Volumes/T7/Dropbox/scan-snap/facture/ocr-test-data/
├── test_data.json             # Test cases (auto-generated)
├── auto_test_data.json        # Auto-generated test cases
└── test_report.csv            # Test results
```

## Contributing

When adding new test cases or improving the parser:

1. **Document your changes** in the test descriptions
2. **Add representative test cases** for different invoice types
3. **Maintain test data quality** by reviewing auto-generated cases
4. **Share successful patterns** that improve accuracy

This test suite is designed to help you iteratively improve the accuracy of your invoice OCR parser through systematic testing and validation. 