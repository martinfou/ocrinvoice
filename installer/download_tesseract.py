#!/usr/bin/env python3
"""
Download Tesseract OCR for Windows and prepare it for inclusion in the installer.
"""

import os
import sys
import urllib.request
import zipfile
import tempfile
import shutil
from pathlib import Path


def download_tesseract():
    """Download Tesseract OCR for Windows."""
    print("Downloading Tesseract OCR for Windows...")
    
    # Tesseract download URL (latest stable version for Windows)
    tesseract_url = "https://digi.bib.uni-mannheim.de/tesseract/tesseract-ocr-w64-setup-5.3.3.20231005.exe"
    
    # Create installer directory if it doesn't exist
    installer_dir = Path("installer")
    installer_dir.mkdir(exist_ok=True)
    
    # Create tesseract subdirectory
    tesseract_dir = installer_dir / "tesseract"
    tesseract_dir.mkdir(exist_ok=True)
    
    # Download path
    installer_path = tesseract_dir / "tesseract-installer.exe"
    
    try:
        print(f"Downloading from: {tesseract_url}")
        print(f"Downloading to: {installer_path}")
        
        # Download the installer
        urllib.request.urlretrieve(tesseract_url, installer_path)
        
        if installer_path.exists():
            print(f"Download completed: {installer_path}")
            print(f"File size: {installer_path.stat().st_size / (1024*1024):.1f} MB")
            return str(installer_path)
        else:
            print("Download failed: file not found")
            return None
            
    except Exception as e:
        print(f"Download failed: {e}")
        return None


def create_tesseract_section():
    """Create NSIS section for Tesseract installation."""
    print("Creating Tesseract installation section...")
    
    # Create a simple NSIS script for Tesseract installation
    tesseract_script = """# Tesseract OCR Installation Script
# This script installs Tesseract OCR silently

!include "MUI2.nsh"
!include "LogicLib.nsh"

Name "Tesseract OCR Installer"
OutFile "tesseract-installer.exe"
InstallDir "$PROGRAMFILES64\\Tesseract-OCR"
RequestExecutionLevel admin

!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_LANGUAGE "English"

Section "Tesseract OCR" SecTesseract
    SetOutPath "$INSTDIR"
    
    ; Extract Tesseract files
    File /r "tesseract\\*.*"
    
    ; Add to PATH
    EnVar::SetHKLM
    EnVar::AddValue "Path" "$INSTDIR"
    
    ; Write registry information
    WriteRegStr HKLM "SOFTWARE\\Tesseract-OCR" "InstallDir" "$INSTDIR"
    WriteRegStr HKLM "SOFTWARE\\Tesseract-OCR" "Version" "5.3.3"
    
    ; Create uninstaller
    WriteUninstaller "$INSTDIR\\Uninstall.exe"
    
    ; Write registry information for add/remove programs
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\Tesseract-OCR" "DisplayName" "Tesseract OCR"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\Tesseract-OCR" "UninstallString" '"$INSTDIR\\Uninstall.exe"'
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\Tesseract-OCR" "DisplayVersion" "5.3.3"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\Tesseract-OCR" "Publisher" "UB-Mannheim"
SectionEnd

Section "Uninstall"
    ; Remove files
    RMDir /r "$INSTDIR"
    
    ; Remove from PATH
    EnVar::SetHKLM
    EnVar::DeleteValue "Path" "$INSTDIR"
    
    ; Remove registry keys
    DeleteRegKey HKLM "SOFTWARE\\Tesseract-OCR"
    DeleteRegKey HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\Tesseract-OCR"
SectionEnd
"""
    
    script_path = Path("installer") / "tesseract-installer.nsi"
    with open(script_path, "w") as f:
        f.write(tesseract_script)
    
    print(f"Created Tesseract NSIS script: {script_path}")
    return str(script_path)


def main():
    """Main function to prepare Tesseract for installer."""
    print("Preparing Tesseract OCR for installer inclusion...")
    
    # Download Tesseract
    installer_path = download_tesseract()
    if not installer_path:
        print("Failed to download Tesseract")
        return False
    
    # Create NSIS script
    script_path = create_tesseract_section()
    if not script_path:
        print("Failed to create Tesseract NSIS script")
        return False
    
    print("\nTesseract OCR preparation completed!")
    print(f"Installer: {installer_path}")
    print(f"NSIS Script: {script_path}")
    print("\nNext steps:")
    print("1. Build the Tesseract installer: makensis installer/tesseract-installer.nsi")
    print("2. Include the Tesseract installer in the main installer")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 