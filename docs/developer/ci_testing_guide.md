# CI Testing Guide

## Overview

This guide addresses common CI testing issues, particularly the Windows GUI test hanging problem that can cause CI builds to run for hours.

## Problem: Windows CI Tests Hanging

### Symptoms
- Tests hang at GUI test execution
- CI builds running for 3+ hours
- Tests stuck at `test_window_size` or similar GUI tests
- No error output, just infinite waiting

### Root Causes
1. **Missing Display Server**: Windows CI runners often lack proper display support
2. **PyQt6 GUI Initialization**: GUI components can't initialize in headless environments
3. **No Timeouts**: Tests can hang indefinitely without proper timeout handling
4. **Missing Dependencies**: GUI-related dependencies may not be available in CI

## Solutions

### 1. Skip GUI Tests in CI

The primary solution is to skip GUI tests in CI environments:

```bash
# Run tests without GUI tests
python -m pytest tests/ -m "not gui"

# Use the CI test runner script
python scripts/run_ci_tests.py
```

### 2. Use Test Markers

GUI tests are marked with `@pytest.mark.gui`:

```python
@pytest.mark.gui
class TestOCRMainWindow:
    """GUI tests that should be skipped in CI."""
```

### 3. CI Configuration

Use `pytest-ci.ini` for CI environments:

```ini
[tool:pytest]
addopts =
    --timeout=300
    --timeout-method=thread
    -m "not gui"
    --disable-warnings
```

### 4. Environment Detection

Tests automatically detect CI environments:

```python
import os

# Skip GUI tests in CI
if os.environ.get("CI") and not os.environ.get("DISPLAY") and os.name != "nt":
    pytest.skip("GUI tests require display in CI environment", allow_module_level=True)
```

## Test Categories

### Unit Tests (Always Run)
- Core functionality tests
- Business logic tests
- Utility function tests
- Parser tests

### Integration Tests (Run in CI)
- End-to-end workflow tests
- File processing tests
- Configuration tests

### GUI Tests (Skip in CI)
- Window creation tests
- User interface tests
- Dialog tests
- Menu interaction tests

## Running Tests

### Local Development
```bash
# Run all tests including GUI
python -m pytest tests/ -v

# Run only unit tests
python -m pytest tests/ -m "unit" -v

# Run only integration tests
python -m pytest tests/ -m "integration" -v
```

### CI Environment
```bash
# Run tests without GUI (recommended for CI)
python -m pytest tests/ -m "not gui" -v

# Use CI test runner
python scripts/run_ci_tests.py

# Run with timeout protection
python -m pytest tests/ --timeout=300 --timeout-method=thread -m "not gui"
```

## CI Configuration Files

### GitHub Actions Example
```yaml
- name: Run Tests
  run: |
    python scripts/run_ci_tests.py
  env:
    CI: true
```

### GitLab CI Example
```yaml
test:
  script:
    - python scripts/run_ci_tests.py
  variables:
    CI: "true"
```

## Troubleshooting

### Test Timeouts
If tests still hang, increase timeout:

```bash
python -m pytest tests/ --timeout=600 --timeout-method=thread
```

### Memory Issues
If tests fail due to memory:

```bash
python -m pytest tests/ --maxfail=10 --tb=short
```

### Specific Test Failures
To debug specific tests:

```bash
# Run specific test file
python -m pytest tests/unit/test_core/test_ocr_engine.py -v

# Run specific test class
python -m pytest tests/unit/test_core/test_ocr_engine.py::TestOCREngine -v

# Run specific test method
python -m pytest tests/unit/test_core/test_ocr_engine.py::TestOCREngine::test_init -v
```

## Best Practices

1. **Always mark GUI tests** with `@pytest.mark.gui`
2. **Use timeouts** in CI environments
3. **Skip GUI tests** in headless environments
4. **Add proper error handling** in test fixtures
5. **Use CI-specific configurations**
6. **Monitor test execution time**
7. **Set reasonable timeouts** (300-600 seconds)

## Performance Optimization

### Test Execution Time
- Unit tests: < 30 seconds
- Integration tests: < 2 minutes
- Full test suite (no GUI): < 5 minutes

### Memory Usage
- Monitor memory usage in CI
- Use `--maxfail` to stop on first failure
- Clean up resources in test teardown

## Monitoring

### Test Metrics
- Execution time per test
- Memory usage
- Success/failure rates
- Timeout occurrences

### CI Metrics
- Build duration
- Test pass rate
- Resource utilization
- Failure patterns

## Conclusion

The key to reliable CI testing is:
1. **Skip GUI tests** in CI environments
2. **Use proper timeouts** to prevent hanging
3. **Implement test markers** for categorization
4. **Monitor and optimize** test performance
5. **Use CI-specific configurations**

This approach ensures fast, reliable CI builds while maintaining comprehensive test coverage for local development.
