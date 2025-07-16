#!/usr/bin/env python3
"""
Build script for creating folder-based packages with Tesseract OCR and Poppler included.
This script helps build the application as a folder instead of a single executable.
"""

import os
import sys
import shutil
import subprocess
import platform
from pathlib import Path


def run_command(cmd, check=True):
    """Run a command and return the result."""
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"Error: {result.stderr}")
        sys.exit(1)
    return result


def install_dependencies():
    """Install required dependencies."""
    print("Installing dependencies...")
    
    # Install Python dependencies
    run_command("pip install -e .[dev]")
    run_command("pip install pyinstaller")
    
    # Install system dependencies based on platform
    system = platform.system().lower()
    
    if system == "windows":
        print("Installing Tesseract OCR and Poppler on Windows...")
        try:
            run_command("choco install tesseract poppler -y", check=False)
        except:
            print("Chocolatey not available. Please install Tesseract OCR and Poppler manually.")
            print("Download from: https://github.com/UB-Mannheim/tesseract/wiki")
            print("And: https://poppler.freedesktop.org/")
    
    elif system == "darwin":  # macOS
        print("Installing Tesseract OCR and Poppler on macOS...")
        try:
            run_command("brew install tesseract poppler")
        except:
            print("Homebrew not available. Please install Tesseract OCR and Poppler manually.")
            print("Download from: https://github.com/tesseract-ocr/tesseract")
            print("And: https://poppler.freedesktop.org/")
    
    else:  # Linux
        print("Installing Tesseract OCR and Poppler on Linux...")
        try:
            run_command("sudo apt-get update && sudo apt-get install -y tesseract-ocr poppler-utils")
        except:
            print("Please install Tesseract OCR and Poppler manually:")
            print("sudo apt-get install tesseract-ocr poppler-utils")


def build_folder_package():
    """Build the application as a folder package."""
    print("Building folder package...")
    
    # Clean previous builds
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    if os.path.exists("build"):
        shutil.rmtree("build")
    
    # Build using the folder spec
    run_command("pyinstaller OCRInvoiceParser-folder.spec")
    
    print("Folder package built successfully!")


def copy_external_binaries():
    """Copy Tesseract OCR and Poppler binaries to the package."""
    print("Copying external binaries...")
    
    system = platform.system().lower()
    dist_path = Path("dist/OCRInvoiceParser")
    
    if system == "windows":
        # Copy Tesseract binaries
        tesseract_path = Path("C:/Program Files/Tesseract-OCR")
        if tesseract_path.exists():
            print(f"Copying Tesseract from {tesseract_path}")
            for item in tesseract_path.iterdir():
                if item.is_file():
                    shutil.copy2(item, dist_path)
                elif item.is_dir():
                    shutil.copytree(item, dist_path / item.name, dirs_exist_ok=True)
        
        # Copy Poppler binaries
        poppler_path = Path("C:/Program Files/poppler/bin")
        if poppler_path.exists():
            print(f"Copying Poppler from {poppler_path}")
            for item in poppler_path.iterdir():
                if item.is_file():
                    shutil.copy2(item, dist_path)
    
    elif system == "darwin":  # macOS
        # Copy Tesseract binaries
        tesseract_bin = Path("/usr/local/bin/tesseract")
        if tesseract_bin.exists():
            print("Copying Tesseract binary")
            shutil.copy2(tesseract_bin, dist_path)
        
        tessdata_path = Path("/usr/local/share/tessdata")
        if tessdata_path.exists():
            print("Copying Tesseract data")
            shutil.copytree(tessdata_path, dist_path / "tessdata", dirs_exist_ok=True)
        
        # Copy Poppler binaries
        poppler_binaries = list(Path("/usr/local/bin").glob("pdf*"))
        for binary in poppler_binaries:
            if binary.is_file():
                print(f"Copying {binary.name}")
                shutil.copy2(binary, dist_path)
    
    else:  # Linux
        # Copy Tesseract binaries
        tesseract_bin = Path("/usr/bin/tesseract")
        if tesseract_bin.exists():
            print("Copying Tesseract binary")
            shutil.copy2(tesseract_bin, dist_path)
        
        tessdata_path = Path("/usr/share/tessdata")
        if tessdata_path.exists():
            print("Copying Tesseract data")
            shutil.copytree(tessdata_path, dist_path / "tessdata", dirs_exist_ok=True)
        
        # Copy Poppler binaries
        poppler_binaries = list(Path("/usr/bin").glob("pdf*"))
        for binary in poppler_binaries:
            if binary.is_file():
                print(f"Copying {binary.name}")
                shutil.copy2(binary, dist_path)


def create_startup_scripts():
    """Create startup scripts for the package."""
    print("Creating startup scripts...")
    
    system = platform.system().lower()
    dist_path = Path("dist/OCRInvoiceParser")
    
    if system == "windows":
        # Create Windows batch file
        bat_content = """@echo off
set PATH=%~dp0;%PATH%
OCRInvoiceParser.exe %*
"""
        with open(dist_path / "run.bat", "w") as f:
            f.write(bat_content)
        print("Created run.bat")
    
    else:  # macOS and Linux
        # Create shell script
        sh_content = """#!/bin/bash
export PATH="$(dirname "$0"):$PATH"
$(dirname "$0")/OCRInvoiceParser "$@"
"""
        with open(dist_path / "run.sh", "w") as f:
            f.write(sh_content)
        
        # Make executable
        os.chmod(dist_path / "run.sh", 0o755)
        print("Created run.sh")


def create_readme():
    """Create README file for the package."""
    print("Creating README...")
    
    system = platform.system().lower()
    dist_path = Path("dist/OCRInvoiceParser")
    
    readme_content = """OCR Invoice Parser - Standalone Package

This package contains everything needed to run the OCR Invoice Parser
without requiring separate installation of Tesseract OCR or Poppler.

To run the application:

"""
    
    if system == "windows":
        readme_content += """Windows:
- Double-click run.bat
- Or run OCRInvoiceParser.exe directly
"""
    else:
        readme_content += """macOS/Linux:
- Double-click run.sh
- Or run ./OCRInvoiceParser directly
"""
    
    readme_content += """
Requirements:
- Windows 10+ or macOS 10.14+ or Linux
- 4GB RAM recommended

Note: This package includes Tesseract OCR and Poppler binaries.
No additional software installation is required.
"""
    
    with open(dist_path / "README.txt", "w") as f:
        f.write(readme_content)
    
    print("Created README.txt")


def create_zip_archive():
    """Create a ZIP archive of the package."""
    print("Creating ZIP archive...")
    
    system = platform.system().lower()
    dist_path = Path("dist")
    
    if system == "windows":
        # Use 7zip if available, otherwise use built-in zip
        try:
            run_command("7z a -tzip OCRInvoiceParser-Windows.zip OCRInvoiceParser/")
        except:
            import zipfile
            with zipfile.ZipFile("OCRInvoiceParser-Windows.zip", "w", zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk("dist/OCRInvoiceParser"):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, "dist")
                        zipf.write(file_path, arcname)
    else:
        run_command("cd dist && zip -r OCRInvoiceParser-$(uname -s).zip OCRInvoiceParser/")
    
    print("ZIP archive created!")


def main():
    """Main function."""
    print("OCR Invoice Parser - Folder Package Builder")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists("OCRInvoiceParser-folder.spec"):
        print("Error: OCRInvoiceParser-folder.spec not found!")
        print("Please run this script from the project root directory.")
        sys.exit(1)
    
    # Install dependencies
    install_dependencies()
    
    # Build the package
    build_folder_package()
    
    # Copy external binaries
    copy_external_binaries()
    
    # Create startup scripts
    create_startup_scripts()
    
    # Create README
    create_readme()
    
    # Create ZIP archive
    create_zip_archive()
    
    print("\n" + "=" * 50)
    print("Build completed successfully!")
    print(f"Package location: {os.path.abspath('dist/OCRInvoiceParser')}")
    print("You can now test the package by running the startup script.")


if __name__ == "__main__":
    main() 