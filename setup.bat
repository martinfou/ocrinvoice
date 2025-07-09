@echo off
REM Invoice OCR Parser Setup Script for Windows
REM This script sets up a Python virtual environment and installs all dependencies

echo 🚀 Setting up Invoice OCR Parser environment...

REM Check if Python 3 is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH. Please install Python 3 first.
    pause
    exit /b 1
)

REM Check Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo 📦 Python version: %PYTHON_VERSION%

REM Remove existing venv if it exists
if exist "venv" (
    echo 🗑️  Removing existing virtual environment...
    rmdir /s /q venv
)

REM Create virtual environment
echo 🔧 Creating virtual environment...
python -m venv venv

REM Activate virtual environment
echo 🔌 Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo ⬆️  Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo 📚 Installing dependencies...
if exist "requirements.txt" (
    pip install -r requirements.txt
    echo ✅ Dependencies installed successfully!
) else (
    echo ❌ requirements.txt not found!
    pause
    exit /b 1
)

REM Check if Tesseract is installed (Windows)
tesseract --version >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Warning: Tesseract OCR is not installed.
    echo    Download from: https://github.com/UB-Mannheim/tesseract/wiki
    echo    Make sure to add Tesseract to your PATH
)

echo.
echo 🎉 Setup complete! To activate the environment:
echo    venv\Scripts\activate.bat
echo.
echo 📖 To test the parser:
echo    python test_parser.py
echo.
echo 📋 To run batch processing:
echo    python test_parser.py --batch
echo.
pause 