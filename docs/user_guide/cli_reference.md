# CLI Reference Guide

This guide provides detailed information about all available CLI commands and their options.

## Command Overview

```bash
ocrinvoice [OPTIONS] COMMAND [ARGS]...
```

## Global Options

| Option | Description |
|--------|-------------|
| `--help` | Show help message and exit |
| `--version` | Show version and exit |
| `--verbose` | Enable verbose output |
| `--debug` | Enable debug mode |

## Commands

### `parse` - Parse a Single Document

Extract structured data from a single PDF document.

```bash
ocrinvoice parse [OPTIONS] PDF_PATH
```

**Arguments:**
- `PDF_PATH`: Path to the PDF file to parse

**Options:**
| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--output` | `-o` | Output file path | stdout |
| `--format` | `-f` | Output format (json, csv, xml) | json |
| `--parser` | `-p` | Parser type (invoice, credit_card) | invoice |
| `--verbose` | `-v` | Enable verbose output | False |
| `--show-text` | `-t` | Show extracted raw text | False |
| `--rename` | `-r` | Rename PDF file based on extracted data | False |
| `--dry-run` | `-d` | Show what would be renamed without actually renaming | False |

**Examples:**
```bash
# Basic parse
ocrinvoice parse invoice.pdf

# Save to file
ocrinvoice parse invoice.pdf --output result.json

# Different format
ocrinvoice parse invoice.pdf --format csv --output result.csv

# Show raw text
ocrinvoice parse invoice.pdf --show-text

# Verbose output
ocrinvoice parse invoice.pdf --verbose

# Credit card statement
ocrinvoice parse statement.pdf --parser credit_card

# Rename file based on extracted data
ocrinvoice parse invoice.pdf --rename

# Dry run to see what would be renamed
ocrinvoice parse invoice.pdf --rename --dry-run
```

### `batch` - Process Multiple Documents

Process multiple PDF documents in a directory.

```bash
ocrinvoice batch [OPTIONS] INPUT_PATH
```

**Arguments:**
- `INPUT_PATH`: Path to directory containing PDF files

**Options:**
| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--output` | `-o` | Output file path | results.csv |
| `--format` | `-f` | Output format (json, csv, xml) | csv |
| `--parser` | `-p` | Parser type (invoice, credit_card) | invoice |
| `--recursive` | `-r` | Process subdirectories recursively | False |
| `--verbose` | `-v` | Enable verbose output | False |
| `--rename` | | Rename PDF files based on extracted data | False |
| `--dry-run` | | Show what would be renamed without actually renaming | False |

**Examples:**
```bash
# Process all PDFs in directory
ocrinvoice batch invoices/

# Save to specific file
ocrinvoice batch invoices/ --output my_results.csv

# Different format
ocrinvoice batch invoices/ --format json --output results.json

# Process recursively
ocrinvoice batch invoices/ --recursive --output all_results.csv

# Verbose output
ocrinvoice batch invoices/ --verbose

# Rename all PDF files based on extracted data
ocrinvoice batch invoices/ --rename

# Dry run to see what would be renamed
ocrinvoice batch invoices/ --rename --dry-run
```

### File Renaming

The `--rename` option allows you to automatically rename PDF files based on the extracted data. Files are renamed using the format:

```
{date}_{company}_{total}.pdf
```

**Examples:**
- `2023-01-15_HYDRO-QUÉBEC_137.50.pdf`
- `2023-02-20_RONA_89.99.pdf`
- `2023-03-10_BANQUE-TD_2500.00.pdf`

**Features:**
- **Automatic formatting**: Dates are formatted as YYYY-MM-DD
- **Company normalization**: Company names are converted to uppercase and special characters are handled
- **Total formatting**: Totals are formatted with 2 decimal places
- **Safe renaming**: If a file with the same name already exists, a number is appended
- **Dry run mode**: Use `--dry-run` to preview what would be renamed without making changes

**Notes:**
- Files are only renamed if all required data (date, company, total) is successfully extracted
- Original files are preserved and renamed in place
- The `--dry-run` option is useful for testing before applying changes

### `aliases` - Manage Business Aliases

Manage business name aliases for consistent company matching.

```bash
ocrinvoice aliases [OPTIONS] COMMAND [ARGS]...
```

#### `aliases list` - List All Aliases

```bash
ocrinvoice aliases list
```

Shows all official business names and their aliases.

#### `aliases add` - Add an Alias

```bash
ocrinvoice aliases add "ALIAS" "OFFICIAL_NAME"
```

**Arguments:**
- `ALIAS`: The alias name to add
- `OFFICIAL_NAME`: The official business name

**Examples:**
```bash
ocrinvoice aliases add "Hydro Quebec" "HYDRO-QUÉBEC"
ocrinvoice aliases add "RBC Bank" "ROYAL BANK OF CANADA"
```

#### `aliases add-official` - Add Official Business Name

```bash
ocrinvoice aliases add-official "BUSINESS_NAME"
```

**Arguments:**
- `BUSINESS_NAME`: The official business name to add

**Examples:**
```bash
ocrinvoice aliases add-official "NEW COMPANY LTD"
```

#### `aliases remove` - Remove an Alias

```bash
ocrinvoice aliases remove "ALIAS"
```

**Arguments:**
- `ALIAS`: The alias name to remove

**Examples:**
```bash
ocrinvoice aliases remove "Hydro Quebec"
```

#### `aliases remove-official` - Remove Official Business Name

```bash
ocrinvoice aliases remove-official "BUSINESS_NAME"
```

**Arguments:**
- `BUSINESS_NAME`: The official business name to remove

**Examples:**
```bash
ocrinvoice aliases remove-official "OLD COMPANY INC"
```

#### `aliases test` - Test Alias Matching

```bash
ocrinvoice aliases test "TEXT_TO_TEST"
```

**Arguments:**
- `TEXT_TO_TEST`: Text to test against aliases

**Examples:**
```bash
ocrinvoice aliases test "Hydro Quebec Inc"
ocrinvoice aliases test "RBC Bank Statement"
```

### `config` - View Configuration

Display current configuration settings.

```bash
ocrinvoice config
```

Shows all configuration values including:
- OCR settings
- Parser settings
- Business alias file location
- Environment variables

### `test` - Run Tests

Run the test suite.

```bash
ocrinvoice test [OPTIONS]
```

**Options:**
| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--verbose` | `-v` | Enable verbose output | False |
| `--coverage` | `-c` | Generate coverage report | False |
| `--test-dir` | | Test directory path | tests/ |

**Examples:**
```bash
# Run all tests
ocrinvoice test

# Run with coverage
ocrinvoice test --coverage

# Run with verbose output
ocrinvoice test --verbose

# Run specific test directory
ocrinvoice test --test-dir tests/unit/
```

## Output Formats

### JSON Format
```json
{
  "company": "HYDRO-QUÉBEC",
  "total": 137.50,
  "date": "2023-01-15",
  "invoice_number": "INV-2023-001",
  "confidence": 0.85
}
```

### CSV Format
```csv
company,total,date,invoice_number,confidence
HYDRO-QUÉBEC,137.50,2023-01-15,INV-2023-001,0.85
```

### XML Format
```xml
<?xml version="1.0" encoding="UTF-8"?>
<invoice>
  <company>HYDRO-QUÉBEC</company>
  <total>137.50</total>
  <date>2023-01-15</date>
  <invoice_number>INV-2023-001</invoice_number>
  <confidence>0.85</confidence>
</invoice>
```

## Error Codes

| Code | Description |
|------|-------------|
| 0 | Success |
| 1 | General error |
| 2 | File not found |
| 3 | Invalid file format |
| 4 | OCR processing failed |
| 5 | Configuration error |

## Getting Help

```bash
# General help
ocrinvoice --help

# Command-specific help
ocrinvoice parse --help
ocrinvoice batch --help
ocrinvoice aliases --help
ocrinvoice test --help
```
