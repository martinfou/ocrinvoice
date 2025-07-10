#!/bin/bash

# Invoice OCR Parser Setup Script for Unix/Linux

set -e

echo "Setting up Invoice OCR Parser..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python 3.8+ is installed
check_python() {
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
        print_status "Found Python $PYTHON_VERSION"

        # Check if version is 3.8 or higher
        if python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
            print_status "Python version is compatible"
        else
            print_error "Python 3.8 or higher is required. Found: $PYTHON_VERSION"
            exit 1
        fi
    else
        print_error "Python 3 is not installed. Please install Python 3.8 or higher."
        exit 1
    fi
}

# Check if pip is installed
check_pip() {
    if command -v pip3 &> /dev/null; then
        print_status "Found pip3"
    else
        print_error "pip3 is not installed. Please install pip3."
        exit 1
    fi
}

# Install Python dependencies
install_dependencies() {
    print_status "Installing Python dependencies..."

    # Upgrade pip
    python3 -m pip install --upgrade pip

    # Install requirements
    if [ -f "requirements.txt" ]; then
        pip3 install -r requirements.txt
        print_status "Dependencies installed from requirements.txt"
    else
        print_warning "requirements.txt not found, installing basic dependencies..."
        pip3 install pytesseract pdf2image pillow opencv-python pandas numpy
    fi
}

# Check for Tesseract OCR
check_tesseract() {
    if command -v tesseract &> /dev/null; then
        TESSERACT_VERSION=$(tesseract --version | head -n 1)
        print_status "Found Tesseract: $TESSERACT_VERSION"
    else
        print_warning "Tesseract OCR is not installed."
        print_status "Please install Tesseract OCR:"
        echo "  Ubuntu/Debian: sudo apt-get install tesseract-ocr"
        echo "  CentOS/RHEL: sudo yum install tesseract"
        echo "  macOS: brew install tesseract"
        echo "  Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki"
    fi
}

# Check for Poppler (for PDF processing)
check_poppler() {
    if command -v pdftoppm &> /dev/null; then
        print_status "Found Poppler utilities"
    else
        print_warning "Poppler utilities are not installed."
        print_status "Please install Poppler:"
        echo "  Ubuntu/Debian: sudo apt-get install poppler-utils"
        echo "  CentOS/RHEL: sudo yum install poppler-utils"
        echo "  macOS: brew install poppler"
        echo "  Windows: Download from http://blog.alivate.com.au/poppler-windows/"
    fi
}

# Create necessary directories
create_directories() {
    print_status "Creating necessary directories..."

    mkdir -p logs
    mkdir -p output
    mkdir -p tests/fixtures/sample_pdfs

    print_status "Directories created"
}

# Set up virtual environment (optional)
setup_venv() {
    if [ ! -d "venv" ]; then
        print_status "Creating virtual environment..."
        python3 -m venv venv
        print_status "Virtual environment created"
        print_status "To activate: source venv/bin/activate"
    else
        print_status "Virtual environment already exists"
    fi
}

# Main setup process
main() {
    print_status "Starting Invoice OCR Parser setup..."

    check_python
    check_pip
    setup_venv
    install_dependencies
    check_tesseract
    check_poppler
    create_directories

    print_status "Setup completed successfully!"
    print_status "Next steps:"
    echo "  1. Activate virtual environment: source venv/bin/activate"
    echo "  2. Run tests: python -m pytest tests/"
    echo "  3. Try parsing: python -m ocrinvoice.cli.main parse <pdf_file>"
}

# Run main function
main "$@"
