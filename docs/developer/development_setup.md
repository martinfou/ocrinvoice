# Development Setup Guide

This guide will help you set up a development environment for the Invoice OCR Parser project.

## Prerequisites

Before you begin, ensure you have:

- **Python 3.8+** installed
- **Git** installed
- **Tesseract OCR** installed (see installation instructions below)
- Basic familiarity with Python development tools

## Environment Setup

### Step 1: Clone the Repository

```bash
# Clone the repository
git clone <repository-url>
cd ocrinvoice

# Verify you're on the main branch
git checkout main
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Verify Python version
python --version  # Should be 3.8+
```

### Step 3: Install Dependencies

```bash
# Install the package in development mode
pip install -e ".[dev]"

# Verify installation
python -c "import ocrinvoice; print('Installation successful!')"
```

### Step 4: Install Tesseract OCR

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

### Step 5: Install Pre-commit Hooks

```bash
# Install pre-commit hooks
pre-commit install

# Verify installation
pre-commit --version
```

## Development Tools

### Code Quality Tools

The project uses several tools to maintain code quality:

- **Black**: Code formatting
- **Flake8**: Linting and style checking
- **MyPy**: Type checking
- **Pre-commit**: Git hooks for automated checks

### Running Quality Checks

```bash
# Format code with Black
black src/ tests/

# Check code style with Flake8
flake8 src/ tests/

# Type checking with MyPy
mypy src/

# Run all checks via pre-commit
pre-commit run --all-files
```

### Testing

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=src/ocrinvoice

# Run specific test file
pytest tests/unit/test_parsers/test_invoice_parser.py

# Run tests with verbose output
pytest -v

# Run tests and generate coverage report
pytest --cov=src/ocrinvoice --cov-report=html
```

## Project Structure

```
ocrinvoice/
├── src/ocrinvoice/              # Main package
│   ├── cli/                     # Command line interface
│   │   ├── main.py              # CLI entry point
│   │   ├── commands/            # Individual commands
│   │   └── utils.py             # CLI utilities
│   ├── core/                    # Core functionality
│   │   ├── image_processor.py   # Image preprocessing
│   │   ├── ocr_engine.py        # OCR engine interface
│   │   └── text_extractor.py    # Text extraction
│   ├── parsers/                 # Document parsers
│   │   ├── base_parser.py       # Abstract base parser
│   │   ├── invoice_parser.py    # Invoice-specific parser
│   │   └── credit_card_parser.py # Credit card parser
│   ├── utils/                   # Utilities
│   │   ├── fuzzy_matcher.py     # Fuzzy matching
│   │   └── amount_normalizer.py # Amount processing
│   ├── business/                # Business logic
│   │   └── business_alias_manager.py # Alias management
│   └── config.py                # Configuration management
├── config/                      # Configuration files
├── tests/                       # Test suite
├── docs/                        # Documentation
└── scripts/                     # Development scripts
```

## Development Workflow

### 1. Feature Development

```bash
# Create a new feature branch
git checkout -b feature/your-feature-name

# Make your changes
# ... edit files ...

# Run tests to ensure nothing is broken
pytest

# Run quality checks
pre-commit run --all-files

# Commit your changes
git add .
git commit -m "Add feature: description of changes"
```

### 2. Bug Fixes

```bash
# Create a bug fix branch
git checkout -b fix/description-of-bug

# Make your changes
# ... edit files ...

# Add tests for the bug fix
# ... add test cases ...

# Run tests
pytest

# Commit your changes
git add .
git commit -m "Fix: description of bug fix"
```

### 3. Testing Your Changes

```bash
# Test the CLI commands
ocrinvoice --help
ocrinvoice parse --help

# Test with sample data
ocrinvoice parse tests/fixtures/sample_invoice.pdf

# Test batch processing
ocrinvoice batch tests/fixtures/ --output test_results.csv
```

## Configuration

### Development Configuration

Create a development configuration file:

```bash
# Create user config directory
mkdir -p ~/.ocrinvoice

# Create development config
cat > ~/.ocrinvoice/config.yaml << EOF
# Development settings
debug: true
log_level: DEBUG

# OCR settings
ocr:
  tesseract_path: /usr/local/bin/tesseract
  language: eng+fra
  dpi: 300

# Parser settings
parser:
  confidence_threshold: 0.7
  max_retries: 3

# Business settings
business:
  alias_file: config/business_aliases.json
EOF
```

### Environment Variables

You can also use environment variables for configuration:

```bash
# Development environment variables
export OCRINVOICE_DEBUG="true"
export OCRINVOICE_LOG_LEVEL="DEBUG"
export OCRINVOICE_OCR_TESSERACT_PATH="/usr/local/bin/tesseract"
export OCRINVOICE_PARSER_CONFIDENCE_THRESHOLD="0.7"
```

## Debugging

### Enable Debug Mode

```bash
# Set debug environment variable
export OCRINVOICE_DEBUG="true"

# Or use the debug flag
ocrinvoice parse invoice.pdf --debug
```

### Logging

The project uses Python's logging module. Configure logging in your development environment:

```python
import logging

# Set up logging for development
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Using a Debugger

You can use Python's built-in debugger or external tools like VS Code's debugger:

```python
# Add breakpoints in your code
import pdb; pdb.set_trace()

# Or use the newer breakpoint() function (Python 3.7+)
breakpoint()
```

## Common Development Tasks

### Adding a New Parser

1. Create a new parser class in `src/ocrinvoice/parsers/`
2. Inherit from `BaseParser`
3. Implement required abstract methods
4. Add tests in `tests/unit/test_parsers/`
5. Update documentation

### Adding a New CLI Command

1. Create a new command file in `src/ocrinvoice/cli/commands/`
2. Implement the command logic
3. Register the command in `src/ocrinvoice/cli/main.py`
4. Add tests in `tests/unit/test_cli/`
5. Update CLI documentation

### Modifying Configuration

1. Update `src/ocrinvoice/config.py` for new configuration options
2. Update `config/default_config.yaml` for default values
3. Add environment variable support if needed
4. Update configuration documentation
5. Add tests for configuration changes

## Performance Profiling

### Profiling Code Performance

```bash
# Install profiling tools
pip install cProfile

# Profile a specific function
python -m cProfile -o profile.stats -m ocrinvoice.cli.main parse invoice.pdf

# Analyze profile results
python -c "import pstats; p = pstats.Stats('profile.stats'); p.sort_stats('cumulative').print_stats(10)"
```

### Memory Profiling

```bash
# Install memory profiler
pip install memory-profiler

# Profile memory usage
python -m memory_profiler your_script.py
```

## Troubleshooting

### Common Issues

**Import Errors:**
```bash
# Ensure you're in the virtual environment
source venv/bin/activate

# Reinstall the package
pip install -e .
```

**Test Failures:**
```bash
# Check if Tesseract is installed
tesseract --version

# Run tests with verbose output
pytest -v

# Check test configuration
pytest --collect-only
```

**Pre-commit Hook Failures:**
```bash
# Run pre-commit manually
pre-commit run --all-files

# Skip pre-commit for a commit (not recommended)
git commit --no-verify -m "Your message"
```

### Getting Help

- Check the [Troubleshooting Guide](../user_guide/troubleshooting.md)
- Review the [Architecture Documentation](../architecture/)
- Look at existing tests for examples
- Open an issue on GitHub

## Next Steps

Once your development environment is set up:

1. **Read the Architecture Documentation**: Understand the system design
2. **Review the Test Suite**: Learn how to write tests
3. **Check the Contributing Guidelines**: Understand contribution standards
4. **Start with Small Changes**: Begin with documentation or test improvements
5. **Join the Community**: Participate in discussions and code reviews

---

*For more information, see the [Contributing Guidelines](./contributing.md) and [API Reference](./api_reference.md).*
