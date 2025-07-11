# Troubleshooting Guide

This guide helps you resolve common issues when using the Invoice OCR Parser.

## Quick Diagnosis

Start by running these commands to diagnose your issue:

```bash
# Check if the tool is working
ocrinvoice --version

# Check configuration
ocrinvoice config

# Test with a simple command
ocrinvoice parse --help
```

## Common Issues and Solutions

### OCR Issues

#### Issue: "Tesseract not found" or "OCR engine not available"

**Symptoms:**
- Error: `Tesseract not found`
- Error: `OCR engine not available`
- Error: `No OCR engine configured`

**Solutions:**

1. **Install Tesseract OCR:**

   **macOS:**
   ```bash
   brew install tesseract
   ```

   **Ubuntu/Debian:**
   ```bash
   sudo apt-get update
   sudo apt-get install tesseract-ocr
   sudo apt-get install tesseract-ocr-fra  # For French support
   ```

   **Windows:**
   - Download from [GitHub releases](https://github.com/UB-Mannheim/tesseract/wiki)
   - Install and add to PATH

2. **Verify Installation:**
   ```bash
   tesseract --version
   ```

3. **Set Custom Path:**
   ```bash
   export OCRINVOICE_OCR_TESSERACT_PATH="/usr/local/bin/tesseract"
   ```

#### Issue: Poor OCR Quality

**Symptoms:**
- Low confidence scores
- Incorrect text extraction
- Missing or garbled text

**Solutions:**

1. **Improve Image Quality:**
   ```bash
   # Use higher DPI
   export OCRINVOICE_OCR_DPI="400"
   ```

2. **Add Language Support:**
   ```bash
   # For French documents
   export OCRINVOICE_OCR_LANGUAGE="eng+fra"
   ```

3. **Lower Confidence Threshold:**
   ```bash
   export OCRINVOICE_OCR_CONFIDENCE_THRESHOLD="0.5"
   ```

4. **Check Raw Text:**
   ```bash
   ocrinvoice parse invoice.pdf --show-text
   ```

### Parsing Issues

#### Issue: "No data extracted" or Empty Results

**Symptoms:**
- Empty JSON output
- All fields are null
- Low confidence scores

**Solutions:**

1. **Check Raw Text Extraction:**
   ```bash
   ocrinvoice parse invoice.pdf --show-text
   ```

2. **Enable Verbose Output:**
   ```bash
   ocrinvoice parse invoice.pdf --verbose
   ```

3. **Lower Parser Confidence:**
   ```bash
   export OCRINVOICE_PARSER_CONFIDENCE_THRESHOLD="0.5"
   ```

4. **Enable Debug Mode:**
   ```bash
   export OCRINVOICE_PARSER_DEBUG="true"
   ocrinvoice parse invoice.pdf
   ```

#### Issue: Wrong Company Name Extracted

**Symptoms:**
- Incorrect company names
- Inconsistent business naming
- Missing company information

**Solutions:**

1. **Check Business Aliases:**
   ```bash
   ocrinvoice aliases list
   ```

2. **Add Missing Aliases:**
   ```bash
   ocrinvoice aliases add "Company Alias" "OFFICIAL_NAME"
   ```

3. **Test Alias Matching:**
   ```bash
   ocrinvoice aliases test "Company Name in Document"
   ```

4. **Add Official Business Name:**
   ```bash
   ocrinvoice aliases add-official "NEW_BUSINESS_NAME"
   ```

#### Issue: Wrong Total Amount Extracted

**Symptoms:**
- Incorrect total amounts
- Subtotal instead of total
- Missing decimal places

**Solutions:**

1. **Check Raw Text:**
   ```bash
   ocrinvoice parse invoice.pdf --show-text
   ```

2. **Verify Amount Format:**
   - Ensure amounts are clearly labeled (TOTAL, AMOUNT DUE, etc.)
   - Check for proper decimal formatting

3. **Enable Debug Mode:**
   ```bash
   export OCRINVOICE_PARSER_DEBUG="true"
   ocrinvoice parse invoice.pdf
   ```

### Configuration Issues

#### Issue: Configuration Not Loading

**Symptoms:**
- Default settings not applied
- Environment variables ignored
- Configuration errors

**Solutions:**

1. **Check Configuration:**
   ```bash
   ocrinvoice config
   ```

2. **Verify Config File:**
   ```bash
   ls -la ~/.ocrinvoice/config.yaml
   ```

3. **Check Environment Variables:**
   ```bash
   env | grep OCRINVOICE
   ```

4. **Validate YAML Syntax:**
   ```bash
   python -c "import yaml; yaml.safe_load(open('~/.ocrinvoice/config.yaml'))"
   ```

#### Issue: Business Alias File Not Found

**Symptoms:**
- Error: `Business alias file not found`
- Aliases not working
- Empty alias list

**Solutions:**

1. **Check Alias File Location:**
   ```bash
   ls -la config/business_aliases.json
   ```

2. **Set Custom Path:**
   ```bash
   export OCRINVOICE_BUSINESS_ALIAS_FILE="/path/to/aliases.json"
   ```

3. **Create Alias File:**
   ```bash
   mkdir -p ~/.ocrinvoice
   echo '{"official_names": [], "aliases": {}}' > ~/.ocrinvoice/aliases.json
   ```

### File and Permission Issues

#### Issue: "File not found" or Permission Denied

**Symptoms:**
- Error: `File not found`
- Error: `Permission denied`
- Cannot read PDF files

**Solutions:**

1. **Check File Path:**
   ```bash
   ls -la invoice.pdf
   ```

2. **Check File Permissions:**
   ```bash
   chmod 644 invoice.pdf
   ```

3. **Use Absolute Path:**
   ```bash
   ocrinvoice parse /full/path/to/invoice.pdf
   ```

4. **Check Directory Permissions:**
   ```bash
   ls -la /path/to/invoice/directory/
   ```

### Performance Issues

#### Issue: Slow Processing

**Symptoms:**
- Long processing times
- High memory usage
- System slowdown

**Solutions:**

1. **Optimize Image Quality:**
   ```bash
   # Use appropriate DPI (300-400 is usually sufficient)
   export OCRINVOICE_OCR_DPI="300"
   ```

2. **Limit Language Support:**
   ```bash
   # Use only necessary languages
   export OCRINVOICE_OCR_LANGUAGE="eng"
   ```

3. **Process in Batches:**
   ```bash
   # Use batch processing for multiple files
   ocrinvoice batch invoices/ --output results.csv
   ```

4. **Enable Debug Mode for Analysis:**
   ```bash
   export OCRINVOICE_PARSER_DEBUG="true"
   ocrinvoice parse invoice.pdf
   ```

### Output Format Issues

#### Issue: Incorrect Output Format

**Symptoms:**
- Wrong file format
- Malformed JSON/CSV/XML
- Missing fields

**Solutions:**

1. **Specify Output Format:**
   ```bash
   ocrinvoice parse invoice.pdf --format json --output result.json
   ocrinvoice parse invoice.pdf --format csv --output result.csv
   ocrinvoice parse invoice.pdf --format xml --output result.xml
   ```

2. **Check Output File:**
   ```bash
   cat result.json
   ```

3. **Validate JSON Output:**
   ```bash
   python -m json.tool result.json
   ```

### File Renaming Issues

#### Issue: Files Not Being Renamed

**Symptoms:**
- Files remain with original names
- No renaming messages
- Rename option ignored

**Solutions:**

1. **Check Rename Configuration:**
   ```bash
   ocrinvoice config | grep -A 5 "rename:"
   ```

2. **Enable Rename Option:**
   ```bash
   # Use CLI flag
   ocrinvoice parse invoice.pdf --rename

   # Or set environment variable
   export OCRINVOICE_RENAME_ENABLED="true"
   ```

3. **Verify Required Data:**
   ```bash
   # Check if all required fields are extracted
   ocrinvoice parse invoice.pdf --verbose
   ```

4. **Use Dry Run Mode:**
   ```bash
   ocrinvoice parse invoice.pdf --rename --dry-run
   ```

#### Issue: Incorrect File Names

**Symptoms:**
- Files renamed with wrong data
- Missing or incorrect company names
- Wrong dates or amounts

**Solutions:**

1. **Check Extracted Data:**
   ```bash
   ocrinvoice parse invoice.pdf --verbose
   ```

2. **Verify Business Aliases:**
   ```bash
   ocrinvoice aliases list
   ocrinvoice aliases test "Company Name"
   ```

3. **Test with Dry Run:**
   ```bash
   ocrinvoice parse invoice.pdf --rename --dry-run
   ```

4. **Check File Name Format:**
   ```bash
   # View current format
   ocrinvoice config | grep -A 3 "rename:"
   ```

#### Issue: File Name Conflicts

**Symptoms:**
- Error: "File already exists"
- Renaming fails
- Duplicate file names

**Solutions:**

1. **Enable Safe Mode:**
   ```bash
   export OCRINVOICE_RENAME_SAFE_MODE="true"
   ```

2. **Check for Existing Files:**
   ```bash
   ls -la *.pdf
   ```

3. **Use Dry Run to Preview:**
   ```bash
   ocrinvoice batch invoices/ --rename --dry-run
   ```

4. **Manual Conflict Resolution:**
   ```bash
   # Move conflicting files first
   mv existing_file.pdf backup/
   ```

## Advanced Troubleshooting

### Debug Mode

Enable comprehensive debugging:

```bash
# Set debug environment variables
export OCRINVOICE_PARSER_DEBUG="true"
export OCRINVOICE_OUTPUT_INCLUDE_RAW_TEXT="true"

# Run with verbose output
ocrinvoice parse invoice.pdf --verbose
```

### Test Individual Components

```bash
# Test OCR only
tesseract invoice.pdf stdout

# Test configuration
ocrinvoice config

# Test business aliases
ocrinvoice aliases list
ocrinvoice aliases test "Company Name"
```

### Log Analysis

Check for detailed error information:

```bash
# Run with maximum verbosity
ocrinvoice parse invoice.pdf --verbose 2>&1 | tee debug.log

# Analyze the log
grep -i error debug.log
grep -i warning debug.log
```

## Getting Help

### Before Asking for Help

1. **Collect Information:**
   ```bash
   # System information
   ocrinvoice --version
   tesseract --version
   python --version

   # Configuration
   ocrinvoice config

   # Test with sample file
   ocrinvoice parse sample.pdf --verbose
   ```

2. **Document the Issue:**
   - Exact error message
   - Steps to reproduce
   - Sample file (if possible)
   - System information

3. **Check Documentation:**
   - Review this troubleshooting guide
   - Check the main README
   - Review CLI reference guide

### Where to Get Help

1. **Check Existing Issues:** Search for similar problems
2. **Create New Issue:** Provide detailed information
3. **Community Support:** Ask in discussions
4. **Documentation:** Review guides and examples

## Prevention Tips

### Best Practices

1. **Use High-Quality Scans:**
   - 300 DPI minimum
   - Good contrast
   - Clear text

2. **Organize Your Files:**
   - Consistent naming
   - Proper directory structure
   - Backup important files

3. **Test Regularly:**
   - Run tests: `ocrinvoice test`
   - Test with sample files
   - Verify configuration

4. **Keep Updated:**
   - Update Tesseract regularly
   - Update the package
   - Review configuration

### Maintenance

```bash
# Regular maintenance tasks
ocrinvoice test  # Run tests
ocrinvoice config  # Check configuration
ocrinvoice aliases list  # Review business aliases
```

---

**Still having issues?** Collect the information above and create a detailed issue report with your specific problem.
