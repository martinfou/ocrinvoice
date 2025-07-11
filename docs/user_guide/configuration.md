# Configuration Guide

This guide explains how to configure the Invoice OCR Parser to suit your specific needs.

## Configuration Sources

The system loads configuration from multiple sources in this order (later sources override earlier ones):

1. **Package defaults** (`config/default_config.yaml`)
2. **User config** (`~/.ocrinvoice/config.yaml`)
3. **Environment variables** (highest priority)

## Configuration Files

### Default Configuration

Located at `config/default_config.yaml`:

```yaml
# OCR Settings
ocr:
  tesseract_path: auto  # Auto-detect or specify path
  dpi: 300
  language: eng+fra
  confidence_threshold: 0.7

# Parser Settings
parser:
  debug: false
  confidence_threshold: 0.7
  max_retries: 3
  parser_type: invoice

# Business Settings
business:
  alias_file: config/business_aliases.json

# Output Settings
output:
  default_format: json
  include_raw_text: false
  include_confidence: true

# File Renaming Settings
rename:
  enabled: false
  format: "{date}_{company}_{total}.pdf"
  safe_mode: true
  dry_run: false
```

### User Configuration

Create `~/.ocrinvoice/config.yaml` to override defaults:

```yaml
# Your custom settings
ocr:
  language: eng+fra+spa  # Add Spanish support
  dpi: 400  # Higher resolution

parser:
  debug: true  # Enable debug mode
  confidence_threshold: 0.8  # Higher confidence requirement

business:
  alias_file: /path/to/your/aliases.json
```

## Environment Variables

Set these environment variables to override configuration:

### OCR Settings

| Variable | Description | Example |
|----------|-------------|---------|
| `OCRINVOICE_OCR_TESSERACT_PATH` | Tesseract executable path | `/usr/local/bin/tesseract` |
| `OCRINVOICE_OCR_DPI` | Image DPI for OCR | `300` |
| `OCRINVOICE_OCR_LANGUAGE` | OCR languages | `eng+fra` |
| `OCRINVOICE_OCR_CONFIDENCE_THRESHOLD` | OCR confidence threshold | `0.7` |

### Parser Settings

| Variable | Description | Example |
|----------|-------------|---------|
| `OCRINVOICE_PARSER_DEBUG` | Enable debug mode | `true` |
| `OCRINVOICE_PARSER_CONFIDENCE_THRESHOLD` | Parser confidence threshold | `0.8` |
| `OCRINVOICE_PARSER_MAX_RETRIES` | Maximum retry attempts | `3` |
| `OCRINVOICE_PARSER_TYPE` | Default parser type | `invoice` |

### Business Settings

| Variable | Description | Example |
|----------|-------------|---------|
| `OCRINVOICE_BUSINESS_ALIAS_FILE` | Business alias file path | `/path/to/aliases.json` |

### Output Settings

| Variable | Description | Example |
|----------|-------------|---------|
| `OCRINVOICE_OUTPUT_DEFAULT_FORMAT` | Default output format | `json` |
| `OCRINVOICE_OUTPUT_INCLUDE_RAW_TEXT` | Include raw text in output | `false` |
| `OCRINVOICE_OUTPUT_INCLUDE_CONFIDENCE` | Include confidence scores | `true` |

### File Renaming Settings

| Variable | Description | Example |
|----------|-------------|---------|
| `OCRINVOICE_RENAME_ENABLED` | Enable automatic file renaming | `false` |
| `OCRINVOICE_RENAME_FORMAT` | File naming format | `{date}_{company}_{total}.pdf` |
| `OCRINVOICE_RENAME_SAFE_MODE` | Enable safe mode (append numbers for conflicts) | `true` |
| `OCRINVOICE_RENAME_DRY_RUN` | Enable dry run mode | `false` |

## Setting Environment Variables

### Linux/macOS

```bash
# Set for current session
export OCRINVOICE_OCR_LANGUAGE="eng+fra"
export OCRINVOICE_PARSER_DEBUG="true"

# Set permanently (add to ~/.bashrc or ~/.zshrc)
echo 'export OCRINVOICE_OCR_LANGUAGE="eng+fra"' >> ~/.bashrc
echo 'export OCRINVOICE_PARSER_DEBUG="true"' >> ~/.bashrc
```

### Windows

```cmd
# Set for current session
set OCRINVOICE_OCR_LANGUAGE=eng+fra
set OCRINVOICE_PARSER_DEBUG=true

# Set permanently (use System Properties > Environment Variables)
```

## Viewing Configuration

### View All Settings

```bash
ocrinvoice config
```

This shows the effective configuration after all sources are merged.

### View Specific Settings

```bash
# View OCR settings
ocrinvoice config | grep -A 10 "ocr:"

# View parser settings
ocrinvoice config | grep -A 10 "parser:"
```

## Common Configuration Scenarios

### High-Accuracy Mode

```yaml
# ~/.ocrinvoice/config.yaml
ocr:
  dpi: 400
  confidence_threshold: 0.8

parser:
  confidence_threshold: 0.9
  debug: true
```

### Multi-Language Support

```yaml
# ~/.ocrinvoice/config.yaml
ocr:
  language: eng+fra+spa+deu  # English, French, Spanish, German
```

### Custom Business Aliases

```yaml
# ~/.ocrinvoice/config.yaml
business:
  alias_file: /path/to/your/custom/aliases.json
```

### Development Mode

```bash
# Environment variables
export OCRINVOICE_PARSER_DEBUG="true"
export OCRINVOICE_OUTPUT_INCLUDE_RAW_TEXT="true"
export OCRINVOICE_PARSER_CONFIDENCE_THRESHOLD="0.5"
```

### File Renaming Mode

```yaml
# ~/.ocrinvoice/config.yaml
rename:
  enabled: true
  format: "{date}_{company}_{total}.pdf"
  safe_mode: true
  dry_run: false
```

Or using environment variables:

```bash
export OCRINVOICE_RENAME_ENABLED="true"
export OCRINVOICE_RENAME_SAFE_MODE="true"
```

## Configuration Validation

The system validates configuration on startup:

```bash
# Test configuration
ocrinvoice config

# If there are errors, they will be displayed
```

### Common Validation Errors

| Error | Solution |
|-------|----------|
| `Tesseract not found` | Install Tesseract or set correct path |
| `Invalid language code` | Use valid language codes (eng, fra, etc.) |
| `Invalid confidence threshold` | Use values between 0.0 and 1.0 |
| `Alias file not found` | Create the alias file or set correct path |

## Configuration Best Practices

### 1. Start with Defaults

Begin with the default configuration and only change what you need.

### 2. Use Environment Variables for Secrets

Don't put sensitive information in config files. Use environment variables instead.

### 3. Test Configuration Changes

Always test your configuration changes:

```bash
# Test with a sample file
ocrinvoice parse sample.pdf --verbose
```

### 4. Document Your Changes

Keep a record of your configuration changes for future reference.

### 5. Use Version Control

Consider versioning your custom configuration:

```bash
# Create a backup
cp ~/.ocrinvoice/config.yaml ~/.ocrinvoice/config.yaml.backup
```

## Troubleshooting Configuration

### Issue: Configuration Not Loading

```bash
# Check if config file exists
ls -la ~/.ocrinvoice/config.yaml

# Check file permissions
chmod 644 ~/.ocrinvoice/config.yaml
```

### Issue: Environment Variables Not Working

```bash
# Verify environment variable is set
echo $OCRINVOICE_PARSER_DEBUG

# Check if variable is exported
env | grep OCRINVOICE
```

### Issue: Invalid Configuration

```bash
# View current configuration
ocrinvoice config

# Check for syntax errors in YAML files
python -c "import yaml; yaml.safe_load(open('~/.ocrinvoice/config.yaml'))"
```
