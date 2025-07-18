# Windows Installer for OCR Invoice Parser

This directory contains the NSIS installer configuration and build scripts for creating a professional Windows installer for the OCR Invoice Parser.

## Prerequisites

### Required Tools

1. **NSIS (Nullsoft Scriptable Install System)**
   - Download from: https://nsis.sourceforge.io/Download
   - Install and ensure `makensis` is in your PATH
   - Test installation: `makensis /VERSION`

2. **PyInstaller**
   - Install via pip: `pip install pyinstaller`
   - Used to create the standalone executable

3. **Python Dependencies**
   - All project dependencies must be installed
   - Run: `pip install -r requirements.txt` (if available)

### Optional Assets

For a complete installer, create these files in the `installer/` directory:

- `icon.ico` - Application icon (32x32 pixels)
- `setup.ico` - Setup installer icon (32x32 pixels)  
- `welcome.bmp` - Welcome page image (164x314 pixels)

## Building the Installer

### Quick Build

```bash
# Build everything (executable + installer)
python installer/build_installer.py

# Build with specific version
python installer/build_installer.py --version 1.3.0

# Clean build (removes previous artifacts)
python installer/build_installer.py --clean

# Build executable only (skip NSIS installer)
python installer/build_installer.py --skip-nsis
```

### Manual Build Steps

1. **Build the executable:**
   ```bash
   pyinstaller OCRInvoiceParser.spec
   ```

2. **Create the installer:**
   ```bash
   makensis installer/installer.nsi
   ```

## Installer Features

### What the Installer Does

- **Main Application**: Installs the OCR Invoice Parser executable and all dependencies
- **Configuration Files**: Copies default configuration files to the installation directory
- **Documentation**: Installs user guides and documentation
- **Start Menu Shortcuts**: Creates shortcuts in the Start Menu
- **Desktop Shortcut**: Optional desktop shortcut creation
- **Tesseract Detection**: Checks for Tesseract OCR and offers installation if missing
- **Registry Integration**: Proper Windows registry entries for uninstall
- **Uninstaller**: Complete uninstallation with registry cleanup

### Installation Options

Users can choose to install:
- ✅ Main Application (required)
- ✅ Start Menu Shortcuts (recommended)
- ✅ Desktop Shortcut (optional)
- ✅ Tesseract OCR (if not already installed)

### System Requirements

- Windows 7 or later (64-bit recommended)
- 4GB RAM minimum
- 500MB free disk space
- Tesseract OCR (will be detected or offered for installation)

## Customization

### Modifying the Installer

Edit `installer.nsi` to customize:

- Application name and version
- Installation directory
- Included files and folders
- Installer appearance and branding
- Additional installation options

### Adding Custom Pages

The installer uses NSIS Modern UI 2. You can add custom pages for:

- License agreement
- Component selection
- Custom configuration
- Post-installation setup

### Branding

To customize the installer appearance:

1. Replace `installer/icon.ico` with your application icon
2. Replace `installer/setup.ico` with your installer icon
3. Replace `installer/welcome.bmp` with your welcome page image
4. Modify colors and text in `installer.nsi`

## Testing

### Testing the Executable

```bash
# Test the standalone executable
./dist/OCRInvoiceParser.exe
```

### Testing the Installer

1. Run the installer: `OCRInvoiceParser-Setup-1.3.0.exe`
2. Test installation in different directories
3. Test uninstallation
4. Verify registry entries
5. Check file associations (if configured)

### Testing Uninstallation

The installer includes robust uninstallation that:
- Removes all application files and directories
- Removes Start Menu shortcuts
- Removes desktop shortcuts (with multiple fallback methods)
- Cleans up registry entries
- Removes Tesseract OCR (if installed by this installer)

**Note**: If desktop shortcuts persist after uninstallation, run `cleanup_desktop_shortcuts.bat` to manually remove them.

### Testing on Different Windows Versions

Test the installer on:
- Windows 10 (latest)
- Windows 11
- Windows Server 2019/2022
- Different user permission levels

## Troubleshooting

### Common Issues

1. **NSIS not found**
   - Install NSIS and ensure it's in PATH
   - Test with: `makensis /VERSION`

2. **PyInstaller build fails**
   - Check all dependencies are installed
   - Verify Python environment
   - Check for missing imports

3. **Installer fails to run**
   - Check Windows compatibility
   - Verify user permissions
   - Check antivirus software interference

4. **Missing Tesseract**
   - Install Tesseract manually
   - Add to system PATH
   - Test with: `tesseract --version`

5. **Desktop shortcuts remain after uninstall**
   - Run `cleanup_desktop_shortcuts.bat` to manually remove them
   - Refresh desktop (F5) or restart Windows Explorer
   - Check both user and public desktop folders

### Debug Mode

Enable verbose output:

```bash
# PyInstaller debug
pyinstaller --debug OCRInvoiceParser.spec

# NSIS debug
makensis /V4 installer/installer.nsi
```

## Distribution

### Release Package

For distribution, include:

1. `OCRInvoiceParser-Setup-{version}.exe` - Main installer
2. `README.md` - Installation instructions
3. `CHANGELOG.md` - Version history
4. `LICENSE` - License information

### Digital Signing

For production releases, consider:

1. Code signing the executable
2. Code signing the installer
3. Obtaining an EV certificate for Windows SmartScreen

### Update Mechanism

The installer supports:

- Version checking via registry
- Automatic update detection
- Clean uninstall before reinstall

## Support

For issues with the installer:

1. Check the troubleshooting section
2. Review NSIS documentation
3. Test on clean Windows installations
4. Verify all dependencies are correctly included 