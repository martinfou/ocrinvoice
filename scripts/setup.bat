@echo off
REM Invoice OCR Parser Setup Script for Windows

echo Setting up Invoice OCR Parser...

REM Check if Python 3.8+ is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Please install Python 3.8 or higher from https://python.org
    pause
    exit /b 1
)

REM Get Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [INFO] Found Python %PYTHON_VERSION%

REM Check if pip is installed
pip --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] pip is not installed or not in PATH.
    echo Please install pip or upgrade Python.
    pause
    exit /b 1
)

echo [INFO] Found pip

REM Upgrade pip
echo [INFO] Upgrading pip...
python -m pip install --upgrade pip

REM Install Python dependencies
echo [INFO] Installing Python dependencies...
if exist requirements.txt (
    pip install -r requirements.txt
    echo [INFO] Dependencies installed from requirements.txt
) else (
    echo [WARNING] requirements.txt not found, installing basic dependencies...
    pip install pytesseract pdf2image pillow opencv-python pandas numpy
)

REM Check for Tesseract OCR
tesseract --version >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Tesseract OCR is not installed or not in PATH.
    echo Please install Tesseract OCR from https://github.com/UB-Mannheim/tesseract/wiki
    echo Make sure to add Tesseract to your system PATH.
) else (
    echo [INFO] Found Tesseract OCR
)

REM Check for Poppler (for PDF processing)
pdftoppm -h >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Poppler utilities are not installed or not in PATH.
    echo Please install Poppler from http://blog.alivate.com.au/poppler-windows/
    echo Make sure to add Poppler to your system PATH.
) else (
    echo [INFO] Found Poppler utilities
)

REM Create necessary directories
echo [INFO] Creating necessary directories...
if not exist logs mkdir logs
if not exist output mkdir output
if not exist tests\fixtures\sample_pdfs mkdir tests\fixtures\sample_pdfs

echo [INFO] Directories created

REM Set up virtual environment (optional)
if not exist venv (
    echo [INFO] Creating virtual environment...
    python -m venv venv
    echo [INFO] Virtual environment created
    echo [INFO] To activate: venv\Scripts\activate
) else (
    echo [INFO] Virtual environment already exists
)

echo.
echo [INFO] Setup completed successfully!
echo [INFO] Next steps:
echo   1. Activate virtual environment: venv\Scripts\activate
echo   2. Run tests: python -m pytest tests\
echo   3. Try parsing: python -m ocrinvoice.cli.main parse ^<pdf_file^>
echo.
pause
