#!/usr/bin/env python3
"""
Invoice OCR Parser Setup Script
Cross-platform setup script for creating virtual environment and installing dependencies
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path

def run_command(command, check=True, shell=False):
    """Run a command and return the result"""
    try:
        if shell:
            result = subprocess.run(command, shell=True, check=check, 
                                  capture_output=True, text=True)
        else:
            result = subprocess.run(command, check=check, 
                                  capture_output=True, text=True)
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed: {command}")
        print(f"Error: {e.stderr}")
        if check:
            sys.exit(1)
        return e

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    print(f"📦 Python version: {version.major}.{version.minor}.{version.micro}")

def create_venv():
    """Create virtual environment"""
    venv_path = Path("venv")
    
    if venv_path.exists():
        print("🗑️  Removing existing virtual environment...")
        shutil.rmtree(venv_path)
    
    print("🔧 Creating virtual environment...")
    result = run_command([sys.executable, "-m", "venv", "venv"])
    if result.returncode == 0:
        print("✅ Virtual environment created successfully!")

def get_venv_python():
    """Get the path to the virtual environment Python executable"""
    if platform.system() == "Windows":
        return Path("venv/Scripts/python.exe")
    else:
        return Path("venv/bin/python")

def get_venv_pip():
    """Get the path to the virtual environment pip executable"""
    if platform.system() == "Windows":
        return Path("venv/Scripts/pip.exe")
    else:
        return Path("venv/bin/pip")

def install_dependencies():
    """Install dependencies in the virtual environment"""
    pip_path = get_venv_pip()
    
    if not pip_path.exists():
        print("❌ Virtual environment pip not found")
        sys.exit(1)
    
    print("⬆️  Upgrading pip...")
    run_command([str(pip_path), "install", "--upgrade", "pip"])
    
    print("📚 Installing dependencies...")
    if Path("requirements.txt").exists():
        result = run_command([str(pip_path), "install", "-r", "requirements.txt"])
        if result.returncode == 0:
            print("✅ Dependencies installed successfully!")
        else:
            print("❌ Failed to install dependencies")
            sys.exit(1)
    else:
        print("❌ requirements.txt not found!")
        sys.exit(1)

def check_system_dependencies():
    """Check if system dependencies are installed"""
    print("\n🔍 Checking system dependencies...")
    
    # Check Tesseract
    tesseract_result = run_command(["tesseract", "--version"], check=False)
    if tesseract_result.returncode != 0:
        print("⚠️  Warning: Tesseract OCR is not installed.")
        if platform.system() == "Darwin":  # macOS
            print("   Install with: brew install tesseract")
        elif platform.system() == "Linux":
            print("   Install with: sudo apt-get install tesseract-ocr")
        elif platform.system() == "Windows":
            print("   Download from: https://github.com/UB-Mannheim/tesseract/wiki")
    else:
        print("✅ Tesseract OCR is installed")
    
    # Check Poppler (for pdf2image)
    poppler_result = run_command(["pdftoppm", "-h"], check=False)
    if poppler_result.returncode != 0:
        print("⚠️  Warning: Poppler is not installed (needed for pdf2image).")
        if platform.system() == "Darwin":  # macOS
            print("   Install with: brew install poppler")
        elif platform.system() == "Linux":
            print("   Install with: sudo apt-get install poppler-utils")
        elif platform.system() == "Windows":
            print("   Download from: https://poppler.freedesktop.org/")
    else:
        print("✅ Poppler is installed")

def main():
    """Main setup function"""
    print("🚀 Setting up Invoice OCR Parser environment...")
    
    # Check Python version
    check_python_version()
    
    # Create virtual environment
    create_venv()
    
    # Install dependencies
    install_dependencies()
    
    # Check system dependencies
    check_system_dependencies()
    
    # Print success message
    print("\n🎉 Setup complete!")
    print("\nTo activate the environment:")
    if platform.system() == "Windows":
        print("   venv\\Scripts\\activate.bat")
    else:
        print("   source venv/bin/activate")
    
    print("\nTo test the parser:")
    print("   python test_parser.py")
    
    print("\nTo run batch processing:")
    print("   python test_parser.py --batch")
    
    print("\n📋 Configuration Files:")
    print("   • business_aliases.json - Configure business name mappings")
    print("   • invoice_database.json - Optional: Stores known company/total pairs (disabled by default)")
    print("   • Edit business_aliases.json to customize company name matching")

if __name__ == "__main__":
    main() 