@echo off
REM Windows Installer Build Script
REM This batch file provides an easy way to build the Windows installer

echo ========================================
echo OCR Invoice Parser - Windows Installer
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python and try again
    pause
    exit /b 1
)

REM Check if we're in the right directory
if not exist "src\ocrinvoice\gui\ocr_main_window.py" (
    echo ERROR: Please run this script from the project root directory
    echo Current directory: %CD%
    pause
    exit /b 1
)

REM Build the installer
echo Building Windows installer...
python installer\build_installer.py %*

if errorlevel 1 (
    echo.
    echo ERROR: Build failed!
    echo Check the error messages above for details
    pause
    exit /b 1
)

echo.
echo ========================================
echo Build completed successfully!
echo ========================================
echo.
echo Files created:
if exist "dist\OCRInvoiceParser.exe" (
    echo - dist\OCRInvoiceParser.exe
)
if exist "OCRInvoiceParser-Setup-*.exe" (
    echo - OCRInvoiceParser-Setup-*.exe
)
echo.
echo Next steps:
echo 1. Test the executable: dist\OCRInvoiceParser.exe
echo 2. Test the installer: OCRInvoiceParser-Setup-*.exe
echo 3. Distribute to users
echo.
pause 