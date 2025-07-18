#!/usr/bin/env python3
"""
NSIS Installer Script for Windows

This script automatically downloads and installs NSIS (Nullsoft Scriptable Install System)
which is required for building Windows installers.

Usage:
    python scripts/install_nsis.py
"""

import os
import sys
import subprocess
import urllib.request
import zipfile
import tempfile
from pathlib import Path
from typing import Optional


def run_command(command: str, check: bool = True) -> subprocess.CompletedProcess:
    """Run a command and return the result."""
    print(f"Running: {command}")
    try:
        result = subprocess.run(
            command, check=check, shell=True, capture_output=True, text=True
        )
        return result
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {command}")
        print(f"Error: {e}")
        return None


def check_nsis_installed() -> bool:
    """Check if NSIS is already installed."""
    print("Checking if NSIS is already installed...")
    
    # Check if makensis is available in PATH
    result = run_command("makensis /VERSION", check=False)
    if result and result.returncode == 0:
        print(f"NSIS found: {result.stdout.strip()}")
        return True
    
    # Check common installation paths
    common_paths = [
        r"C:\Program Files (x86)\NSIS\makensis.exe",
        r"C:\Program Files\NSIS\makensis.exe",
        r"C:\NSIS\makensis.exe"
    ]
    
    for path in common_paths:
        if os.path.exists(path):
            print(f"NSIS found at: {path}")
            return True
    
    print("NSIS not found")
    return False


def download_nsis() -> Optional[str]:
    """Download NSIS installer."""
    print("Downloading NSIS...")
    
    # NSIS download URL (latest stable version)
    nsis_url = "https://sourceforge.net/projects/nsis/files/NSIS%203/3.10/nsis-3.10-setup.exe/download"
    
    # Create temp directory for download
    temp_dir = tempfile.mkdtemp()
    installer_path = os.path.join(temp_dir, "nsis-3.10-setup.exe")
    
    try:
        print(f"Downloading from: {nsis_url}")
        print(f"Downloading to: {installer_path}")
        
        # Download the installer
        urllib.request.urlretrieve(nsis_url, installer_path)
        
        if os.path.exists(installer_path):
            print(f"Download completed: {installer_path}")
            return installer_path
        else:
            print("Download failed: file not found")
            return None
            
    except Exception as e:
        print(f"Download failed: {e}")
        return None


def install_nsis(installer_path: str) -> bool:
    """Install NSIS using the downloaded installer."""
    print("Installing NSIS...")
    
    # NSIS installer command with silent installation
    # /S = silent install, /D= = specify installation directory
    install_dir = r"C:\Program Files (x86)\NSIS"
    command = f'"{installer_path}" /S /D="{install_dir}"'
    
    print(f"Running installer: {command}")
    result = run_command(command)
    
    if result and result.returncode == 0:
        print("NSIS installation completed successfully")
        return True
    else:
        print("NSIS installation failed")
        return False


def add_nsis_to_path() -> bool:
    """Add NSIS to system PATH."""
    print("Adding NSIS to system PATH...")
    
    nsis_path = r"C:\Program Files (x86)\NSIS"
    
    if not os.path.exists(nsis_path):
        print(f"NSIS installation directory not found: {nsis_path}")
        return False
    
    # Get current PATH
    current_path = os.environ.get('PATH', '')
    
    if nsis_path in current_path:
        print("NSIS already in PATH")
        return True
    
    # Add NSIS to PATH for current session
    os.environ['PATH'] = f"{nsis_path};{current_path}"
    
    print(f"Added {nsis_path} to PATH for current session")
    print("Note: You may need to restart your terminal or computer for PATH changes to take effect")
    
    return True


def verify_installation() -> bool:
    """Verify that NSIS is properly installed."""
    print("Verifying NSIS installation...")
    
    result = run_command("makensis /VERSION", check=False)
    if result and result.returncode == 0:
        print(f"NSIS verification successful: {result.stdout.strip()}")
        return True
    else:
        print("NSIS verification failed")
        return False


def main():
    """Main installation function."""
    print("NSIS Installer for Windows")
    print("=" * 40)
    
    # Check if already installed
    if check_nsis_installed():
        print("NSIS is already installed!")
        return True
    
    # Download NSIS
    installer_path = download_nsis()
    if not installer_path:
        print("Failed to download NSIS")
        return False
    
    # Install NSIS
    if not install_nsis(installer_path):
        print("Failed to install NSIS")
        return False
    
    # Add to PATH
    add_nsis_to_path()
    
    # Verify installation
    if verify_installation():
        print("\nNSIS installation completed successfully!")
        print("You can now build Windows installers using the build_installer.py script.")
        return True
    else:
        print("\nNSIS installation may have failed. Please check manually.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 