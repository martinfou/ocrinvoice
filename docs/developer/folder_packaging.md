# Folder Packaging Guide

This document explains the folder-based packaging approach for the OCR Invoice Parser, which creates standalone packages that include Tesseract OCR and Poppler utilities.

## Overview

The folder packaging approach creates a directory containing:
- The main application executable
- All Python dependencies
- Tesseract OCR binaries and data files
- Poppler PDF utilities
- Configuration files
- Startup scripts for easy execution

## Benefits

1. **Self-contained**: No need to install Tesseract OCR or Poppler separately
2. **Portable**: Can be moved between systems without reinstallation
3. **Easier distribution**: Single ZIP file contains everything needed
4. **Better debugging**: Easier to inspect and troubleshoot issues
5. **Faster startup**: No need to search for external dependencies

## Files Created

### New Files
- `OCRInvoiceParser-folder.spec` - PyInstaller specification for folder builds
- `.github/workflows/release-folder.yml` - GitHub Actions workflow for automated builds
- `scripts/build_folder_package.py` - Local build script

### Package Contents
```
OCRInvoiceParser/
├── OCRInvoiceParser.exe (Windows) / OCRInvoiceParser (macOS/Linux)
├── run.bat (Windows) / run.sh (macOS/Linux)
├── tesseract.exe / tesseract
├── tessdata/ (Tesseract language data)
├── pdfinfo, pdftoppm, pdftotext (Poppler utilities)
├── config/ (Configuration files)
├── README.txt (Usage instructions)
└── [Python dependencies and libraries]
```

## Building Locally

### Prerequisites
- Python 3.8+
- PyInstaller
- Tesseract OCR installed
- Poppler utilities installed

### Using the Build Script
```bash
# Run the automated build script
python scripts/build_folder_package.py
```

The script will:
1. Install required dependencies
2. Build the application using PyInstaller
3. Copy Tesseract OCR and Poppler binaries
4. Create startup scripts
5. Generate a README file
6. Create a ZIP archive

### Manual Build
```bash
# Install dependencies
pip install -e .[dev]
pip install pyinstaller

# Build the package
pyinstaller OCRInvoiceParser-folder.spec

# Copy external binaries (see build script for details)
# Create startup scripts (see build script for details)
```

## GitHub Actions Integration

The `.github/workflows/release-folder.yml` workflow automatically:
- Builds packages for Windows and macOS
- Installs Tesseract OCR and Poppler on runners
- Copies binaries to the package
- Creates startup scripts
- Generates ZIP archives
- Creates GitHub releases

### Triggering Builds
```bash
# Create a new release
git tag v1.2.3
git push origin v1.2.3
```

## Platform-Specific Details

### Windows
- Uses Chocolatey to install Tesseract OCR and Poppler
- Copies from `C:\Program Files\Tesseract-OCR\`
- Copies from `C:\Program Files\poppler\bin\`
- Creates `run.bat` startup script

### macOS
- Uses Homebrew to install Tesseract OCR and Poppler
- Copies from `/usr/local/bin/` and `/usr/local/share/`
- Creates `run.sh` startup script
- Makes startup script executable

### Linux
- Uses apt-get to install packages
- Copies from `/usr/bin/` and `/usr/share/`
- Creates `run.sh` startup script
- Makes startup script executable

## Testing the Package

### Windows
```cmd
# Extract the ZIP file
# Navigate to the folder
cd OCRInvoiceParser
# Run the application
run.bat
# Or directly
OCRInvoiceParser.exe
```

### macOS/Linux
```bash
# Extract the ZIP file
# Navigate to the folder
cd OCRInvoiceParser
# Run the application
./run.sh
# Or directly
./OCRInvoiceParser
```

## Troubleshooting

### Common Issues

1. **Missing Tesseract data files**
   - Ensure `tessdata/` directory is copied
   - Check that language files are present

2. **Poppler utilities not found**
   - Verify Poppler is installed on the build system
   - Check that `pdf*` binaries are copied

3. **Permission issues on macOS/Linux**
   - Ensure startup script is executable: `chmod +x run.sh`
   - Check file permissions on the main executable

4. **PATH issues**
   - The startup scripts set the PATH to include the package directory
   - If running directly, ensure the package directory is in PATH

### Debugging
- Check the package contents to ensure all files are present
- Verify that Tesseract and Poppler binaries are executable
- Test individual components (Tesseract, Poppler) separately
- Check system logs for missing dependencies

## Comparison with Single Executable

| Aspect | Single Executable | Folder Package |
|--------|-------------------|----------------|
| Size | Smaller | Larger |
| Startup time | Slower (extraction) | Faster |
| Portability | High | High |
| Debugging | Difficult | Easier |
| Dependencies | Bundled | Included as files |
| Updates | Full replacement | Partial updates possible |

## Future Improvements

1. **Incremental updates**: Update only changed components
2. **Configuration management**: Separate user config from package
3. **Plugin system**: Allow additional components
4. **Auto-updater**: Built-in update mechanism
5. **Cross-platform testing**: Automated testing on multiple platforms

## Related Documentation

- [Release Guide](../release_guide.md) - General release process
- [Development Setup](../development_setup.md) - Setting up development environment
- [Testing Guide](../testing.md) - Testing procedures
- [Architecture Overview](../../architecture/system_architecture.md) - System design 