# Contributing Guidelines

Thank you for your interest in contributing to the Invoice OCR Parser! This document provides guidelines and standards for contributing to the project.

## 🤝 How to Contribute

### Types of Contributions

We welcome various types of contributions:

- **Bug Reports**: Report issues you encounter
- **Feature Requests**: Suggest new features or improvements
- **Code Contributions**: Submit code changes and improvements
- **Documentation**: Improve or add documentation
- **Testing**: Add tests or improve test coverage
- **Code Review**: Review and provide feedback on pull requests

### Before You Start

1. **Check Existing Issues**: Search existing issues to avoid duplicates
2. **Read the Documentation**: Familiarize yourself with the project structure
3. **Set Up Development Environment**: Follow the [Development Setup Guide](./development_setup.md)
4. **Understand the Codebase**: Review the [Architecture Documentation](../architecture/)

## 🐛 Reporting Bugs

### Bug Report Template

When reporting a bug, please include:

```markdown
**Bug Description**
A clear description of what the bug is.

**Steps to Reproduce**
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

**Expected Behavior**
A clear description of what you expected to happen.

**Actual Behavior**
A clear description of what actually happened.

**Environment**
- OS: [e.g. macOS, Ubuntu, Windows]
- Python Version: [e.g. 3.8, 3.9, 3.10]
- Tesseract Version: [e.g. 4.1.1]
- Package Version: [e.g. 1.0.0]

**Additional Context**
Any other context about the problem, including:
- Sample files that reproduce the issue
- Error messages or logs
- Screenshots if applicable
```

### Bug Report Guidelines

- **Be Specific**: Provide detailed steps to reproduce the issue
- **Include Sample Data**: If possible, provide sample PDF files that reproduce the issue
- **Check Existing Issues**: Search for similar issues before creating a new one
- **Use Clear Language**: Write in clear, concise language

## 💡 Feature Requests

### Feature Request Template

```markdown
**Feature Description**
A clear description of the feature you'd like to see.

**Use Case**
Describe the problem this feature would solve or the use case it would enable.

**Proposed Solution**
A clear description of how you envision this feature working.

**Alternative Solutions**
Any alternative solutions or features you've considered.

**Additional Context**
Any other context, mockups, or examples.
```

### Feature Request Guidelines

- **Explain the Problem**: Clearly describe the problem the feature would solve
- **Provide Examples**: Include examples of how the feature would be used
- **Consider Impact**: Think about how the feature affects existing functionality
- **Be Realistic**: Consider the scope and complexity of the feature

## 🔧 Code Contributions

### Development Workflow

1. **Fork the Repository**: Create your own fork of the project
2. **Create a Feature Branch**: Create a branch for your changes
3. **Make Your Changes**: Implement your feature or fix
4. **Write Tests**: Add tests for your changes
5. **Run Quality Checks**: Ensure code meets quality standards
6. **Submit a Pull Request**: Create a PR with your changes

### Branch Naming Convention

Use descriptive branch names:

- `feature/description-of-feature` - For new features
- `fix/description-of-bug` - For bug fixes
- `docs/description-of-docs` - For documentation changes
- `test/description-of-tests` - For test improvements
- `refactor/description-of-refactor` - For code refactoring

### Commit Message Guidelines

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

**Types:**
- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation only changes
- `style`: Changes that do not affect the meaning of the code
- `refactor`: A code change that neither fixes a bug nor adds a feature
- `test`: Adding missing tests or correcting existing tests
- `chore`: Changes to the build process or auxiliary tools

**Examples:**
```
feat: add support for credit card statement parsing
fix: resolve OCR error correction for amount extraction
docs: update CLI reference with new commands
test: add unit tests for fuzzy matching algorithm
```

### Code Style Guidelines

#### Python Code Style

- **Follow PEP 8**: Use Black for code formatting
- **Type Hints**: Use type hints for all function parameters and return values
- **Docstrings**: Use Google-style docstrings for all public functions and classes
- **Line Length**: Maximum 88 characters (Black default)

#### Example Code Style

```python
from typing import Dict, List, Optional, Union
from pathlib import Path


def process_invoice(
    pdf_path: Union[str, Path],
    config: Optional[Dict[str, any]] = None
) -> Dict[str, any]:
    """Process an invoice PDF and extract structured data.

    Args:
        pdf_path: Path to the PDF file to process
        config: Optional configuration dictionary

    Returns:
        Dictionary containing extracted invoice data

    Raises:
        FileNotFoundError: If the PDF file doesn't exist
        ValueError: If the PDF file is invalid
    """
    # Implementation here
    pass
```

### Testing Requirements

#### Test Coverage

- **Minimum Coverage**: Aim for 90%+ test coverage
- **New Features**: All new features must have tests
- **Bug Fixes**: Bug fixes must include regression tests
- **Integration Tests**: Include integration tests for complex features

#### Test Structure

```python
import pytest
from pathlib import Path
from ocrinvoice.parsers.invoice_parser import InvoiceParser


class TestInvoiceParser:
    """Test cases for InvoiceParser class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.parser = InvoiceParser()
        self.test_file = Path("tests/fixtures/sample_invoice.pdf")

    def test_parse_invoice_success(self):
        """Test successful invoice parsing."""
        result = self.parser.parse(self.test_file)

        assert result["success"] is True
        assert "company" in result
        assert "total" in result
        assert "date" in result

    def test_parse_invoice_file_not_found(self):
        """Test parsing with non-existent file."""
        with pytest.raises(FileNotFoundError):
            self.parser.parse("non_existent_file.pdf")
```

### Quality Checks

Before submitting a pull request, ensure your code passes all quality checks:

```bash
# Run all quality checks
pre-commit run --all-files

# Or run individual checks
black src/ tests/
flake8 src/ tests/
mypy src/
pytest --cov=src/ocrinvoice
```

## 📝 Documentation Contributions

### Documentation Standards

- **Clear and Concise**: Write in clear, simple language
- **User-Focused**: Write for the intended audience
- **Code Examples**: Include practical code examples
- **Cross-References**: Link related sections appropriately
- **Regular Updates**: Keep documentation current with code changes

### Documentation Types

- **User Documentation**: Guides for end users
- **API Documentation**: Documentation for developers
- **Architecture Documentation**: System design and technical details
- **Contributing Documentation**: Guidelines for contributors

### Documentation Structure

```
docs/
├── README.md                    # Documentation index
├── user_guide/                  # End user documentation
├── architecture/                # Technical architecture
└── developer/                   # Developer resources
```

## 🔍 Code Review Process

### Pull Request Guidelines

1. **Clear Description**: Provide a clear description of your changes
2. **Related Issues**: Link to related issues or feature requests
3. **Testing**: Ensure all tests pass and coverage is maintained
4. **Documentation**: Update documentation if needed
5. **Screenshots**: Include screenshots for UI changes

### Pull Request Template

```markdown
## Description
Brief description of the changes made.

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] All tests pass
- [ ] New tests added for new functionality
- [ ] Documentation updated

## Checklist
- [ ] My code follows the style guidelines of this project
- [ ] I have performed a self-review of my own code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes
```

### Review Process

1. **Automated Checks**: CI/CD pipeline runs quality checks
2. **Code Review**: Maintainers review the code
3. **Testing**: Ensure tests pass and coverage is maintained
4. **Documentation**: Verify documentation is updated
5. **Approval**: At least one maintainer must approve the PR

## 🚀 Release Process

### Version Management

We use [Semantic Versioning](https://semver.org/) for version numbers:

- **MAJOR.MINOR.PATCH** (e.g., 1.2.3)
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Checklist

- [ ] All tests pass
- [ ] Documentation is updated
- [ ] Changelog is updated
- [ ] Version number is updated
- [ ] Release notes are prepared
- [ ] Tag is created

## 🏷️ Labels and Milestones

### Issue Labels

- `bug`: Something isn't working
- `enhancement`: New feature or request
- `documentation`: Improvements or additions to documentation
- `good first issue`: Good for newcomers
- `help wanted`: Extra attention is needed
- `priority: high`: High priority issues
- `priority: low`: Low priority issues

### Milestones

- **v1.0.0**: Initial stable release
- **v1.1.0**: Feature release
- **v1.2.0**: Feature release
- **Future Releases**: Planned features and improvements

## 📞 Getting Help

### Communication Channels

- **GitHub Issues**: For bug reports and feature requests
- **GitHub Discussions**: For questions and general discussion
- **Pull Requests**: For code contributions and reviews

### Resources

- [Development Setup Guide](./development_setup.md)
- [Architecture Documentation](../architecture/)
- [User Guide](../user_guide/)
- [API Reference](./api_reference.md)

## 🙏 Recognition

### Contributors

We recognize all contributors in our project:

- **Code Contributors**: Listed in git history and release notes
- **Documentation Contributors**: Acknowledged in documentation
- **Bug Reporters**: Recognized for helping improve the project
- **Reviewers**: Acknowledged for their review contributions

### Hall of Fame

Special recognition for significant contributions:

- **Core Contributors**: Regular contributors with significant impact
- **Feature Contributors**: Contributors of major features
- **Documentation Champions**: Contributors who significantly improve documentation

## 📄 License

By contributing to this project, you agree that your contributions will be licensed under the same license as the project (MIT License).

---

*Thank you for contributing to the Invoice OCR Parser! Your contributions help make this project better for everyone.*
