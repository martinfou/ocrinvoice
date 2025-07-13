# Release Guide - OCR Invoice Parser

This guide covers the process of creating cross-platform releases for the OCR Invoice Parser application.

## Overview

The OCR Invoice Parser supports three platforms:
- **Windows** (Windows 10+)
- **macOS** (10.14+)
- **Linux** (Ubuntu 18.04+, CentOS 7+, Fedora 28+)

## Prerequisites

Before creating a release, ensure you have:

1. **Git access** to the repository
2. **GitHub Actions** enabled for the repository
3. **PyPI account** (for publishing to PyPI)
4. **Test environments** for each platform (optional but recommended)

## Release Process

### 1. Pre-Release Checklist

Before creating a release, complete these steps:

- [ ] All tests pass on all platforms
- [ ] Documentation is up to date
- [ ] Version numbers are consistent across files
- [ ] CHANGELOG.md is updated (if applicable)
- [ ] Dependencies are up to date
- [ ] Security vulnerabilities are addressed

### 2. Automated Release (Recommended)

The easiest way to create a release is using the automated release script:

```bash
# Bump patch version (1.0.0 -> 1.0.1)
python scripts/release.py patch

# Bump minor version (1.0.0 -> 1.1.0)
python scripts/release.py minor

# Bump major version (1.0.0 -> 2.0.0)
python scripts/release.py major

# Set specific version
python scripts/release.py --version 1.2.3
```

The release script will:
1. Check git status
2. Run tests
3. Update version numbers
4. Build the package
5. Commit changes
6. Create and push a git tag
7. Trigger GitHub Actions for cross-platform builds

### 3. Manual Release Process

If you prefer to create a release manually:

#### Step 1: Update Version

Update the version in `pyproject.toml`:

```toml
[project]
name = "ocrinvoice"
version = "1.0.1"  # Update this
```

#### Step 2: Update Documentation

Update version references in:
- `README.md`
- `docs/user_guide/getting_started.md`
- Any other documentation files

#### Step 3: Test Locally

```bash
# Run tests
pytest tests/ -v

# Build package
python -m build

# Test installation
pip install dist/ocrinvoice-*.whl
```

#### Step 4: Commit and Tag

```bash
# Commit changes
git add .
git commit -m "Bump version to 1.0.1"

# Push to main
git push origin main

# Create and push tag
git tag v1.0.1
git push origin v1.0.1
```

### 4. GitHub Actions Workflow

When you push a tag starting with `v`, GitHub Actions will automatically:

1. **Build on all platforms** (Windows, macOS, Linux)
2. **Test on multiple Python versions** (3.8, 3.9, 3.10, 3.11)
3. **Install Tesseract OCR** on each platform
4. **Run the test suite**
5. **Build distribution packages**
6. **Create a GitHub release** with all artifacts

## Platform-Specific Considerations

### Windows

#### Tesseract Installation
- **Chocolatey**: `choco install tesseract`
- **winget**: `winget install UB-Mannheim.TesseractOCR`
- **Manual**: Download from https://github.com/UB-Mannheim/tesseract/wiki

#### Dependencies
- PyQt6 requires Visual C++ Redistributable
- OpenCV may require additional DLLs

### macOS

#### Tesseract Installation
- **Homebrew**: `brew install tesseract`
- **MacPorts**: `sudo port install tesseract`

#### Dependencies
- PyQt6 works out of the box
- OpenCV is pre-compiled for macOS

### Linux

#### Tesseract Installation
- **Ubuntu/Debian**: `sudo apt-get install tesseract-ocr`
- **CentOS/RHEL**: `sudo yum install tesseract`
- **Fedora**: `sudo dnf install tesseract`
- **Arch**: `sudo pacman -S tesseract`

#### Dependencies
- May need to install system packages for PyQt6
- OpenCV requires additional system libraries

## Distribution Packages

The release process creates several distribution formats:

### Source Distribution
- `ocrinvoice-1.0.1.tar.gz` - Source code distribution
- Contains all source files and can be built on any platform

### Wheel Distribution
- `ocrinvoice-1.0.1-py3-none-any.whl` - Universal wheel
- Pre-built package that works on all platforms
- Faster installation than source distribution

## Installation Instructions

### From PyPI (Recommended)

```bash
# Install the package
pip install ocrinvoice

# Install Tesseract OCR (required)
# Windows: choco install tesseract
# macOS: brew install tesseract
# Linux: sudo apt-get install tesseract-ocr
```

### From GitHub Release

1. Download the appropriate wheel file from the GitHub release
2. Install with pip:
   ```bash
   pip install ocrinvoice-1.0.1-py3-none-any.whl
   ```

### From Source

```bash
# Clone the repository
git clone https://github.com/your-username/ocrinvoice.git
cd ocrinvoice

# Install in development mode
pip install -e .

# Install Tesseract OCR
python scripts/setup_cross_platform.py
```

## Testing the Release

After creating a release, test it on each platform:

### Windows Testing
```bash
# Install from PyPI
pip install ocrinvoice

# Test CLI
ocrinvoice --help

# Test GUI
python -m ocrinvoice.gui.ocr_main_window
```

### macOS Testing
```bash
# Install from PyPI
pip install ocrinvoice

# Test CLI
ocrinvoice --help

# Test GUI
python -m ocrinvoice.gui.ocr_main_window
```

### Linux Testing
```bash
# Install from PyPI
pip install ocrinvoice

# Test CLI
ocrinvoice --help

# Test GUI
python -m ocrinvoice.gui.ocr_main_window
```

## Troubleshooting

### Common Issues

#### 1. Tesseract Not Found
**Problem**: OCR engine is not installed or not in PATH
**Solution**: Install Tesseract using platform-specific instructions

#### 2. PyQt6 Import Error
**Problem**: PyQt6 dependencies are missing
**Solution**: Install system dependencies (Linux) or Visual C++ Redistributable (Windows)

#### 3. OpenCV Import Error
**Problem**: OpenCV system libraries are missing
**Solution**: Install system dependencies or use conda environment

#### 4. Build Failures
**Problem**: GitHub Actions build fails
**Solution**: Check build logs for specific errors and fix platform-specific issues

### Platform-Specific Issues

#### Windows
- Ensure Tesseract is in PATH
- Install Visual C++ Redistributable
- Use Windows-compatible paths

#### macOS
- Ensure Homebrew is installed
- Check for macOS-specific library issues
- Verify code signing if distributing outside App Store

#### Linux
- Install system dependencies for PyQt6
- Ensure proper library paths
- Check for distribution-specific package names

## Release Notes Template

When creating a release, include:

```markdown
## Version 1.0.1

### New Features
- Feature 1
- Feature 2

### Bug Fixes
- Fix 1
- Fix 2

### Improvements
- Improvement 1
- Improvement 2

### Breaking Changes
- None

### Dependencies
- Updated dependency X to version Y

### Installation
```bash
pip install ocrinvoice==1.0.1
```

### Supported Platforms
- Windows 10+
- macOS 10.14+
- Linux (Ubuntu 18.04+, CentOS 7+, Fedora 28+)
```

## Security Considerations

- Never include API keys or secrets in releases
- Use dependency scanning tools
- Keep dependencies up to date
- Follow security best practices for package distribution

## Future Improvements

- [ ] Add code signing for macOS
- [ ] Create Windows installer
- [ ] Add Docker support
- [ ] Implement automated dependency updates
- [ ] Add performance benchmarks
- [ ] Create platform-specific wheels for better performance

## Support

For release-related issues:

1. Check the troubleshooting section
2. Review GitHub Actions logs
3. Test on clean environments
4. Consult platform-specific documentation
5. Open an issue on GitHub

---

*This guide covers the current release process. For the latest information, check the GitHub repository and documentation.*
