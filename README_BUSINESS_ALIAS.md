# Business Alias System Implementation Summary

## Overview
A flexible, configurable business alias system that maps any string found in invoices to one of five official business names.

## Current System Features

### 1. **BusinessAliasManager Class** (`business_alias_manager.py`)
- **Exact Matches**: Direct string-to-business mapping (highest priority)
- **Partial Matches**: Substring detection with business assignment  
- **Fuzzy Matches**: OCR error correction using Soundex + Levenshtein distance (requires indicators)
- **Indicators**: Keywords that must be present for fuzzy matching to activate
- **Official Name Enforcement**: All outputs resolve to one of five official business names

### 2. **Configuration File** (`business_aliases.json`)
```json
{
    "official_names": [
        "bmr",
        "banque-td",
        "taxes-scolaires",
        "la-forfaiterie",
        "hydro-québec"
    ],
    "exact_matches": {
        "bmr": "bmr",
        "td": "banque-td",
        "rbc": "banque-td",
        "compte de taxes scolaire": "taxes-scolaires",
        "cdmpte de taxes scdlaire": "taxes-scolaires",
        "la forfaiterie": "la-forfaiterie"
    },
    "partial_matches": {
        "centre de services scolaires": "taxes-scolaires",
        "board of education": "taxes-scolaires",
        "hydro": "hydro-québec",
        "forfaiterie": "la-forfaiterie",
        "bmr": "bmr",
        "grandes-seigneuries": "taxes-scolaires",
        "hautes-rivieres": "taxes-scolaires",
        "toronto dominion": "banque-td",
        "royal bank": "banque-td"
    },
    "fuzzy_candidates": [
        "taxes-scolaires",
        "bmr",
        "banque-td",
        "la-forfaiterie",
        "hydro-québec"
    ],
    "indicators": {
        "taxes-scolaires": ["scolaire", "scola", "scolaires"],
        "bmr": ["bmr"],
        "hydro-québec": ["hydro", "électricité", "energy", "quebec"],
        "la-forfaiterie": ["forfaiterie", "forfaiter"],
        "banque-td": ["td", "dominion"]
    }
}
```


## Current System Benefits

### 1. **Flexibility**
- No hardcoded business names in the code
- Easy to add new business mappings without code changes
- Support for multiple alias types (exact, partial, fuzzy)
- Optional invoice database (disabled by default, stores only business names)

### 2. **Maintainability**
- Centralized configuration in JSON file
- Clear separation of concerns
- Easy to test and validate business mappings
- Simplified database structure (business names only)
- Single source of truth for business names

### 3. **Extensibility**
- Can easily add new business types
- Support for complex matching rules with indicators
- Confidence scoring for different match types
- Optional fallback matching via database
- Easy to modify official names list

### 4. **User-Friendly**
- Simple JSON configuration format
- Clear documentation and examples
- Test scripts for validation
- Database functionality optional and clearly documented
- Consistent output format

## Usage Examples

### Adding a New Business Alias
```python
# Add exact match
alias_manager.add_alias("ABC", "bmr", "exact_matches")

# Add partial match  
alias_manager.add_alias("XYZ", "banque-td", "partial_matches")
```

## Alias Management Tools

### 1. **Simple Example Script** (`add_alias_example.py`)
Demonstrates basic usage of `add_alias()` with predefined examples.

```bash
python3 add_alias_example.py
```

**What it does:**
- Adds example aliases: "ABC" → "bmr", "XYZ Corp" → "banque-td", "MyBank" → "banque-td"
- Tests the new aliases
- Shows updated statistics

### 2. **Interactive Tool** (`interactive_alias_example.py`)
Guided interactive interface for adding aliases.

```bash
python3 interactive_alias_example.py
```

**Features:**
- Lists available official business names
- Prompts for alias text, business name, and match type
- Validates inputs and tests results
- Shows statistics after each addition

**Example session:**
```
🔧 Interactive Business Alias Manager
==================================================
This tool helps you add new business aliases.
Available official business names:
   1. bmr
   2. banque-td
   3. taxes-scolaires
   4. la-forfaiterie
   5. hydro-québec

Available match types:
   1. exact_matches (highest priority)
   2. partial_matches (medium priority)

==================================================
Enter the alias text to match (or 'quit' to exit): ABC Corp
Select the official business name:
   1. bmr
   2. banque-td
   3. taxes-scolaires
   4. la-forfaiterie
   5. hydro-québec
Enter number (1-5): 1
Select match type:
   1. exact_matches (exact string match)
   2. partial_matches (substring match)
Enter number (1-2): 1
✅ Successfully added: 'ABC Corp' -> 'bmr' (exact_matches)
✅ Test result: 'ABC Corp' -> 'bmr' (exact_match, confidence: 1.00)
```

### 3. **Command Line Tool** (`manage_business_cli.py`)
Quick command-line interface for adding aliases and managing official business names.

```bash
python3 manage_business_cli.py <alias> <business_name> <match_type>
python3 manage_business_cli.py --add-official <business_name>
```

**Usage:**
```bash
# Add exact match
python3 manage_business_cli.py "ABC Corp" "bmr" "exact"

# Add partial match
python3 manage_business_cli.py "MyBank" "banque-td" "partial"

# Add new official business name
python3 manage_business_cli.py --add-official "New-Company"

# Show help and available business names
python3 manage_business_cli.py
```

**Parameters:**
- **`alias`**: The text to match (e.g., "ABC Corp", "MyBank")
- **`business_name`**: Official business name (must be one of the official names)
- **`match_type`**: "exact" or "partial"

**Commands:**
- **Add alias**: `python3 manage_business_cli.py <alias> <business_name> <match_type>`
- **Add official**: `python3 manage_business_cli.py --add-official <business_name>`

**Example output:**
```
# Adding alias
✅ Successfully added: 'ABC Corp' -> 'bmr' (exact match)
✅ Test result: 'ABC Corp' -> 'bmr' (exact_match, confidence: 1.00)

# Adding official business name
✅ Successfully added 'new-company' as an official business name
📋 Total official business names: 6

📋 All Official Business Names:
------------------------------
   1. bmr
   2. banque-td
   3. hydro-québec
   4. la-forfaiterie
   5. taxes-scolaires
   6. new-company
```

### 4. **Direct Python Usage**
Use the BusinessAliasManager directly in your own scripts.

```python
from business_alias_manager import BusinessAliasManager

# Initialize
alias_manager = BusinessAliasManager()

# Add aliases
alias_manager.add_alias("NewBank", "banque-td", "exact_matches")
alias_manager.add_alias("Hardware Store", "bmr", "partial_matches")

# Test aliases
result = alias_manager.find_business_match("NewBank")
if result:
    business_name, match_type, confidence = result
    print(f"Match: {business_name} ({match_type}, {confidence:.2f})")

# Get statistics
stats = alias_manager.get_stats()
print(f"Total aliases: {stats['exact_matches'] + stats['partial_matches']}")
```

### 5. **Validation and Testing**
All tools include validation and testing:

- **Input validation**: Ensures business names are official
- **Automatic testing**: Tests new aliases immediately after addition
- **Statistics tracking**: Shows updated counts after changes
- **Error handling**: Clear error messages for invalid inputs

### 6. **Configuration Persistence**
All changes are automatically saved to `business_aliases.json`:

- Changes persist between sessions
- No manual file editing required
- Backup your configuration file before major changes
- Configuration is validated on startup

### 7. **Best Practices**
- **Use exact matches** for precise text matching (highest confidence)
- **Use partial matches** for substring detection (medium confidence)
- **Test aliases** after adding them
- **Keep aliases simple** and avoid overly complex patterns
- **Use official business names** only (the 5 defined names)
- **Backup configuration** before making changes

### 8. **Troubleshooting**
- **"Not an official business name"**: Use only the 5 official names
- **"No match found"**: Check spelling and try partial match instead
- **Configuration errors**: Validate JSON syntax in `business_aliases.json`
- **Permission errors**: Ensure write access to the configuration file

### Configuration Structure
- **official_names**: Authoritative list of five business names
- **exact_matches**: Direct string-to-business mapping
- **partial_matches**: Substring detection with business assignment
- **fuzzy_candidates**: List of business names for fuzzy matching
- **indicators**: Keywords required for fuzzy matching activation
- **confidence_weights**: Scoring for different match types

## Current System Architecture

### Matching Priority
1. **Exact Matches** (highest priority, confidence: 1.0)
2. **Partial Matches** (medium priority, confidence: 0.8)
3. **Fuzzy Matches** (lowest priority, confidence: 0.6, requires indicators)

### Fuzzy Matching Requirements
- **Indicators needed**: 1 (any single indicator from the list)
- **Fuzzy threshold**: 0.8 (very strict)
- **Purpose**: Prevents false positives while catching OCR errors

### Database Integration
- **Optional**: Disabled by default
- **Purpose**: Stores only business names for fallback matching
- **Usage**: `InvoiceOCRParser(use_database=True)` to enable

## Configuration Files

### Required Files
- `business_aliases.json`: Business name mapping configuration with five official names
- `invoice_ocr_parser_cli.py`: Main parser with alias integration
- `business_alias_manager.py`: Alias management class

### Optional Files
- `invoice_database.json`: Business names database (when enabled)
- `test_business_aliases.py`: Validation test script