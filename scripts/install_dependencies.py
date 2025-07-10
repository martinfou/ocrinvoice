#!/usr/bin/env python3
"""
Dependency installation script for Invoice OCR Parser.

This script handles the installation of all required dependencies
and provides detailed feedback on the installation process.
"""

import subprocess
import sys
import os
import platform
from pathlib import Path


def run_command(command, check=True, capture_output=True):
    """Run a shell command and return the result."""
    try:
        result = subprocess.run(
            command, shell=True, check=check, capture_output=capture_output, text=True
        )
        return result
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Command failed: {command}")
        print(f"[ERROR] Error: {e}")
        return e


def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(
            f"[ERROR] Python 3.8 or higher is required. Found: {version.major}.{version.minor}"
        )
        return False
    print(
        f"[INFO] Python version {version.major}.{version.minor}.{version.micro} is compatible"
    )
    return True


def upgrade_pip():
    """Upgrade pip to the latest version."""
    print("[INFO] Upgrading pip...")
    result = run_command("python -m pip install --upgrade pip")
    if result.returncode == 0:
        print("[INFO] Pip upgraded successfully")
    else:
        print("[WARNING] Failed to upgrade pip, continuing anyway")
    return result.returncode == 0


def install_requirements():
    """Install dependencies from requirements.txt if it exists."""
    requirements_file = Path("requirements.txt")
    if requirements_file.exists():
        print("[INFO] Installing dependencies from requirements.txt...")
        result = run_command("pip install -r requirements.txt")
        if result.returncode == 0:
            print("[INFO] Dependencies installed successfully")
            return True
        else:
            print("[ERROR] Failed to install dependencies from requirements.txt")
            return False
    else:
        print("[WARNING] requirements.txt not found")
        return False


def install_basic_dependencies():
    """Install basic dependencies manually."""
    print("[INFO] Installing basic dependencies...")

    dependencies = [
        "pytesseract",
        "pdf2image",
        "pillow",
        "opencv-python",
        "pandas",
        "numpy",
        "click",
        "pyyaml",
        "pytest",
        "pytest-cov",
    ]

    for dep in dependencies:
        print(f"[INFO] Installing {dep}...")
        result = run_command(f"pip install {dep}")
        if result.returncode == 0:
            print(f"[INFO] {dep} installed successfully")
        else:
            print(f"[ERROR] Failed to install {dep}")
            return False

    return True


def check_system_dependencies():
    """Check for system dependencies like Tesseract and Poppler."""
    print("[INFO] Checking system dependencies...")

    # Check Tesseract
    result = run_command("tesseract --version", check=False)
    if result.returncode == 0:
        version_line = result.stdout.split("\n")[0]
        print(f"[INFO] Found Tesseract: {version_line}")
    else:
        print("[WARNING] Tesseract OCR not found")
        print("[INFO] Please install Tesseract OCR:")
        system = platform.system().lower()
        if system == "linux":
            print("  Ubuntu/Debian: sudo apt-get install tesseract-ocr")
            print("  CentOS/RHEL: sudo yum install tesseract")
        elif system == "darwin":
            print("  macOS: brew install tesseract")
        elif system == "windows":
            print(
                "  Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki"
            )

    # Check Poppler
    result = run_command("pdftoppm -h", check=False)
    if result.returncode == 0:
        print("[INFO] Found Poppler utilities")
    else:
        print("[WARNING] Poppler utilities not found")
        print("[INFO] Please install Poppler:")
        system = platform.system().lower()
        if system == "linux":
            print("  Ubuntu/Debian: sudo apt-get install poppler-utils")
            print("  CentOS/RHEL: sudo yum install poppler-utils")
        elif system == "darwin":
            print("  macOS: brew install poppler")
        elif system == "windows":
            print(
                "  Windows: Download from http://blog.alivate.com.au/poppler-windows/"
            )


def create_directories():
    """Create necessary directories."""
    print("[INFO] Creating necessary directories...")

    directories = [
        "logs",
        "output",
        "tests/fixtures/sample_pdfs",
        "docs/api",
        "docs/user_guide",
        "docs/developer_guide",
        "docs/examples",
    ]

    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"[INFO] Created directory: {directory}")


def setup_virtual_environment():
    """Set up virtual environment if it doesn't exist."""
    venv_path = Path("venv")
    if not venv_path.exists():
        print("[INFO] Creating virtual environment...")
        result = run_command("python -m venv venv")
        if result.returncode == 0:
            print("[INFO] Virtual environment created successfully")
            print("[INFO] To activate:")
            if platform.system().lower() == "windows":
                print("  venv\\Scripts\\activate")
            else:
                print("  source venv/bin/activate")
        else:
            print("[ERROR] Failed to create virtual environment")
            return False
    else:
        print("[INFO] Virtual environment already exists")

    return True


def main():
    """Main installation process."""
    print("=" * 50)
    print("Invoice OCR Parser - Dependency Installation")
    print("=" * 50)

    # Check Python version
    if not check_python_version():
        sys.exit(1)

    # Upgrade pip
    upgrade_pip()

    # Try to install from requirements.txt first
    if not install_requirements():
        # Fall back to manual installation
        if not install_basic_dependencies():
            print("[ERROR] Failed to install basic dependencies")
            sys.exit(1)

    # Check system dependencies
    check_system_dependencies()

    # Create directories
    create_directories()

    # Set up virtual environment
    setup_virtual_environment()

    print("\n" + "=" * 50)
    print("[SUCCESS] Installation completed!")
    print("=" * 50)
    print("Next steps:")
    print("1. Activate virtual environment")
    print("2. Run tests: python -m pytest tests/")
    print("3. Try parsing: python -m ocrinvoice.cli.main parse <pdf_file>")
    print("=" * 50)


if __name__ == "__main__":
    main()
