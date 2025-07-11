# Basic Usage Examples

This guide provides practical examples of how to use the Invoice OCR Parser for common scenarios.

## Quick Examples

### Parse a Single Invoice

```bash
# Basic parse - outputs to console
ocrinvoice parse invoice.pdf

# Save to file
ocrinvoice parse invoice.pdf --output result.json

# Show raw extracted text
ocrinvoice parse invoice.pdf --show-text

# Verbose output for debugging
ocrinvoice parse invoice.pdf --verbose
```

### Process Multiple Invoices

```bash
# Process all PDFs in a directory
ocrinvoice batch invoices/ --output results.csv

# Process recursively (including subfolders)
ocrinvoice batch invoices/ --recursive --output all_results.csv

# Different output formats
ocrinvoice batch invoices/ --format json --output results.json
ocrinvoice batch invoices/ --format xml --output results.xml
```

## Real-World Scenarios

### Scenario 1: Monthly Invoice Processing

**Situation:** You have a folder of monthly invoices that need to be processed.

```bash
# Create organized directory structure
mkdir -p invoices/2024/01
mkdir -p invoices/2024/02

# Process January invoices
ocrinvoice batch invoices/2024/01/ --output january_2024.csv

# Process February invoices
ocrinvoice batch invoices/2024/02/ --output february_2024.csv

# Process all invoices for the year
ocrinvoice batch invoices/2024/ --recursive --output 2024_invoices.csv
```

### Scenario 2: Business Name Standardization

**Situation:** You want consistent business names across all your invoices.

```bash
# First, see what business names are currently extracted
ocrinvoice batch invoices/ --output temp.csv
cat temp.csv | cut -d',' -f1 | sort | uniq

# Add aliases for common variations
ocrinvoice aliases add "Hydro Quebec" "HYDRO-QUÉBEC"
ocrinvoice aliases add "Hydro-Quebec" "HYDRO-QUÉBEC"
ocrinvoice aliases add "Hydro Quebec Inc" "HYDRO-QUÉBEC"

ocrinvoice aliases add "RBC Bank" "ROYAL BANK OF CANADA"
ocrinvoice aliases add "Royal Bank" "ROYAL BANK OF CANADA"

# Test the aliases
ocrinvoice aliases test "Hydro Quebec Inc"
ocrinvoice aliases test "RBC Bank Statement"

# Re-process with standardized names
ocrinvoice batch invoices/ --output standardized_invoices.csv
```

### Scenario 3: Multi-Language Documents

**Situation:** You have invoices in both English and French.

```bash
# Set up multi-language support
export OCRINVOICE_OCR_LANGUAGE="eng+fra"

# Process all documents
ocrinvoice batch invoices/ --output multilingual_results.csv

# Or process by language
mkdir -p invoices/english invoices/french
# Move files to appropriate directories, then:
ocrinvoice batch invoices/english/ --output english_invoices.csv
ocrinvoice batch invoices/french/ --output french_invoices.csv
```

### Scenario 4: Quality Control

**Situation:** You want to ensure high-quality extraction results.

```bash
# Enable debug mode for detailed analysis
export OCRINVOICE_PARSER_DEBUG="true"
export OCRINVOICE_PARSER_CONFIDENCE_THRESHOLD="0.8"

# Process with verbose output
ocrinvoice batch invoices/ --verbose --output high_quality_results.csv

# Check for low-confidence results
cat high_quality_results.csv | grep ",0\.[0-6]"  # Find results with confidence < 0.7
```

### Scenario 5: Integration with Other Tools

**Situation:** You want to integrate the parser with other data processing tools.

```bash
# Generate JSON for API integration
ocrinvoice batch invoices/ --format json --output api_data.json

# Generate CSV for spreadsheet analysis
ocrinvoice batch invoices/ --format csv --output spreadsheet_data.csv

# Generate XML for enterprise systems
ocrinvoice batch invoices/ --format xml --output enterprise_data.xml

# Pipe to other tools
ocrinvoice parse invoice.pdf | jq '.total'  # Extract just the total
ocrinvoice parse invoice.pdf | jq '.company'  # Extract just the company name
```

## Advanced Examples

### Custom Configuration

```bash
# Create custom configuration
mkdir -p ~/.ocrinvoice
cat > ~/.ocrinvoice/config.yaml << EOF
ocr:
  dpi: 400
  language: eng+fra+spa
  confidence_threshold: 0.8

parser:
  debug: true
  confidence_threshold: 0.9

business:
  alias_file: ~/.ocrinvoice/custom_aliases.json
EOF

# Use custom configuration
ocrinvoice parse invoice.pdf
```

### Batch Processing with Error Handling

```bash
#!/bin/bash
# Script for robust batch processing

INPUT_DIR="invoices"
OUTPUT_FILE="results.csv"
ERROR_LOG="errors.log"

echo "Starting batch processing..."

# Process with error logging
ocrinvoice batch "$INPUT_DIR" --output "$OUTPUT_FILE" 2> "$ERROR_LOG"

# Check for errors
if [ -s "$ERROR_LOG" ]; then
    echo "Errors occurred during processing:"
    cat "$ERROR_LOG"
else
    echo "Processing completed successfully!"
fi

# Show summary
echo "Results saved to: $OUTPUT_FILE"
echo "Total records: $(wc -l < "$OUTPUT_FILE")"
```

### Automated Processing Script

```bash
#!/bin/bash
# Automated invoice processing script

# Configuration
INPUT_DIR="/path/to/invoices"
OUTPUT_DIR="/path/to/results"
DATE=$(date +%Y%m%d)

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Process invoices
echo "Processing invoices from $INPUT_DIR..."

ocrinvoice batch "$INPUT_DIR" \
    --recursive \
    --format csv \
    --output "$OUTPUT_DIR/invoices_$DATE.csv"

# Generate summary
echo "Processing complete!"
echo "Results: $OUTPUT_DIR/invoices_$DATE.csv"
echo "Records processed: $(wc -l < "$OUTPUT_DIR/invoices_$DATE.csv")"
```

### Data Analysis Examples

```bash
# Extract and analyze totals
ocrinvoice batch invoices/ --format csv --output data.csv

# Find highest invoice
cat data.csv | tail -n +2 | cut -d',' -f2 | sort -n | tail -1

# Find most common companies
cat data.csv | tail -n +2 | cut -d',' -f1 | sort | uniq -c | sort -nr

# Calculate total amount
cat data.csv | tail -n +2 | cut -d',' -f2 | paste -sd+ | bc

# Find invoices above threshold
cat data.csv | tail -n +2 | awk -F',' '$2 > 1000 {print $0}'
```

## Output Format Examples

### JSON Output
```json
{
  "company": "HYDRO-QUÉBEC",
  "total": 137.50,
  "date": "2023-01-15",
  "invoice_number": "INV-2023-001",
  "confidence": 0.85
}
```

### CSV Output
```csv
company,total,date,invoice_number,confidence
HYDRO-QUÉBEC,137.50,2023-01-15,INV-2023-001,0.85
ROYAL BANK OF CANADA,250.00,2023-01-16,INV-2023-002,0.92
```

### XML Output
```xml
<?xml version="1.0" encoding="UTF-8"?>
<invoices>
  <invoice>
    <company>HYDRO-QUÉBEC</company>
    <total>137.50</total>
    <date>2023-01-15</date>
    <invoice_number>INV-2023-001</invoice_number>
    <confidence>0.85</confidence>
  </invoice>
</invoices>
```

## Troubleshooting Examples

### Debug a Problematic File

```bash
# Step 1: Check if file is readable
ocrinvoice parse problem.pdf --show-text

# Step 2: Enable verbose output
ocrinvoice parse problem.pdf --verbose

# Step 3: Enable debug mode
export OCRINVOICE_PARSER_DEBUG="true"
ocrinvoice parse problem.pdf

# Step 4: Check configuration
ocrinvoice config
```

### Test Business Alias Matching

```bash
# Test various company name variations
ocrinvoice aliases test "Hydro Quebec Inc"
ocrinvoice aliases test "Hydro-Quebec"
ocrinvoice aliases test "HYDRO QUEBEC"

# Add missing aliases
ocrinvoice aliases add "Hydro Quebec Inc" "HYDRO-QUÉBEC"

# Verify the alias was added
ocrinvoice aliases list
```

### Validate Output

```bash
# Validate JSON output
ocrinvoice parse invoice.pdf --format json --output result.json
python -m json.tool result.json

# Check CSV structure
ocrinvoice parse invoice.pdf --format csv --output result.csv
head -5 result.csv
wc -l result.csv
```

## Best Practices

### File Organization
```bash
# Organize by date
mkdir -p invoices/{2023,2024}/{01,02,03,04,05,06,07,08,09,10,11,12}

# Organize by company
mkdir -p invoices/{hydro_quebec,rbc,other}

# Organize by status
mkdir -p invoices/{processed,pending,errors}
```

### Regular Maintenance
```bash
# Weekly maintenance script
#!/bin/bash

# Update business aliases
ocrinvoice aliases list > aliases_backup.txt

# Run tests
ocrinvoice test

# Check configuration
ocrinvoice config > config_backup.txt

# Process pending invoices
ocrinvoice batch invoices/pending/ --output processed_$(date +%Y%m%d).csv
```

### Quality Assurance
```bash
# Check for low-confidence results
ocrinvoice batch invoices/ --output results.csv
awk -F',' '$5 < 0.7 {print "Low confidence: " $0}' results.csv

# Verify business names
cut -d',' -f1 results.csv | sort | uniq > extracted_companies.txt
echo "Review these company names for accuracy:"
cat extracted_companies.txt
```

---

These examples should help you get started with common use cases. For more advanced scenarios, check the troubleshooting guide and CLI reference. 