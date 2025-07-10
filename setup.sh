#!/bin/bash

# Invoice OCR Parser Setup Script
# This script sets up a Python virtual environment and installs all dependencies

set -e  # Exit on any error

echo "🚀 Setting up Invoice OCR Parser environment..."

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo "📦 Python version: $PYTHON_VERSION"

# Remove existing venv if it exists
if [ -d "venv" ]; then
    echo "🗑️  Removing existing virtual environment..."
    rm -rf venv
fi

# Create virtual environment
echo "🔧 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📚 Installing dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    echo "✅ Dependencies installed successfully!"
else
    echo "❌ requirements.txt not found!"
    exit 1
fi

# Check if Tesseract is installed
if ! command -v tesseract &> /dev/null; then
    echo "⚠️  Warning: Tesseract OCR is not installed."
    echo "   For macOS, install with: brew install tesseract"
    echo "   For Ubuntu/Debian: sudo apt-get install tesseract-ocr"
    echo "   For Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki"
fi

# Check if Poppler is installed (for pdf2image)
if ! command -v pdftoppm &> /dev/null; then
    echo "⚠️  Warning: Poppler is not installed (needed for pdf2image)."
    echo "   For macOS, install with: brew install poppler"
    echo "   For Ubuntu/Debian: sudo apt-get install poppler-utils"
    echo "   For Windows: Download from https://poppler.freedesktop.org/"
fi

echo ""
echo "🎉 Setup complete! To activate the environment:"
echo "   source venv/bin/activate"
echo ""
echo "📖 To test the parser:"
echo "   python test_parser.py"
echo ""
echo "📋 To run batch processing:"
echo "   python test_parser.py --batch"
