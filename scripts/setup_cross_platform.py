#!/usr/bin/env python3
"""
Cross-platform setup script for OCR Invoice Parser.

This script handles installation of Tesseract OCR and Python dependencies
across Windows, macOS, and Linux platforms.

Usage:
    python scripts/setup_cross_platform.py
"""

import sys
import platform
import subprocess
import shutil
from pathlib import Path
from typing import Union, List


def run_command(
    command: Union[str, List[str]], check: bool = True, shell: bool = False
) -> Union[subprocess.CompletedProcess, None]:
    """Run a command and return the result."""
    try:
        if isinstance(command, str) and not shell:
            command = command.split()

        result = subprocess.run(
            command, check=check, shell=shell, capture_output=True, text=True
        )
        return result
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {command}")
        print(f"Error: {e}")
        return None


def check_tesseract() -> bool:
    """Check if Tesseract is installed and accessible."""
    try:
        result = subprocess.run(
            ["tesseract", "--version"], capture_output=True, text=True
        )
        if result.returncode == 0:
            print("✅ Tesseract OCR is already installed")
            return True
    except FileNotFoundError:
        pass

    print("❌ Tesseract OCR not found")
    return False


def install_tesseract_windows() -> bool:
    """Install Tesseract on Windows."""
    print("Installing Tesseract OCR on Windows...")

    # Check if Chocolatey is available
    if shutil.which("choco"):
        print("Using Chocolatey to install Tesseract...")
        result = run_command("choco install tesseract -y")
        if result and result.returncode == 0:
            print("✅ Tesseract installed via Chocolatey")
            return True

    # Check if winget is available
    if shutil.which("winget"):
        print("Using winget to install Tesseract...")
        result = run_command("winget install UB-Mannheim.TesseractOCR")
        if result and result.returncode == 0:
            print("✅ Tesseract installed via winget")
            return True

    print("❌ Please install Tesseract manually:")
    print("   1. Download from: https://github.com/UB-Mannheim/tesseract/wiki")
    print("   2. Add Tesseract to your system PATH")
    return False


def install_tesseract_macos() -> bool:
    """Install Tesseract on macOS."""
    print("Installing Tesseract OCR on macOS...")

    # Check if Homebrew is available
    if shutil.which("brew"):
        print("Using Homebrew to install Tesseract...")
        result = run_command(["brew", "install", "tesseract"])
        if result and result.returncode == 0:
            print("✅ Tesseract installed via Homebrew")
            return True

    # Check if MacPorts is available
    if shutil.which("port"):
        print("Using MacPorts to install Tesseract...")
        result = run_command(["sudo", "port", "install", "tesseract"])
        if result and result.returncode == 0:
            print("✅ Tesseract installed via MacPorts")
            return True

    print("❌ Please install Tesseract manually:")
    print("   1. Install Homebrew: https://brew.sh/")
    print("   2. Run: brew install tesseract")
    return False


def install_tesseract_linux() -> bool:
    """Install Tesseract on Linux."""
    print("Installing Tesseract OCR on Linux...")

    # Detect package manager
    if shutil.which("apt-get"):
        print("Using apt-get to install Tesseract...")
        result = run_command(["sudo", "apt-get", "update"])
        if result and result.returncode == 0:
            result = run_command(
                [
                    "sudo",
                    "apt-get",
                    "install",
                    "-y",
                    "tesseract-ocr",
                    "tesseract-ocr-eng",
                ]
            )
            if result and result.returncode == 0:
                print("✅ Tesseract installed via apt-get")
                return True

    elif shutil.which("yum"):
        print("Using yum to install Tesseract...")
        result = run_command(["sudo", "yum", "install", "-y", "tesseract"])
        if result and result.returncode == 0:
            print("✅ Tesseract installed via yum")
            return True

    elif shutil.which("dnf"):
        print("Using dnf to install Tesseract...")
        result = run_command(["sudo", "dnf", "install", "-y", "tesseract"])
        if result and result.returncode == 0:
            print("✅ Tesseract installed via dnf")
            return True

    elif shutil.which("pacman"):
        print("Using pacman to install Tesseract...")
        result = run_command(["sudo", "pacman", "-S", "--noconfirm", "tesseract"])
        if result and result.returncode == 0:
            print("✅ Tesseract installed via pacman")
            return True

    print("❌ Please install Tesseract manually:")
    print("   Ubuntu/Debian: sudo apt-get install tesseract-ocr")
    print("   CentOS/RHEL: sudo yum install tesseract")
    print("   Fedora: sudo dnf install tesseract")
    print("   Arch: sudo pacman -S tesseract")
    return False


def install_tesseract() -> bool:
    """Install Tesseract based on the operating system."""
    system = platform.system().lower()

    if system == "windows":
        return install_tesseract_windows()
    elif system == "darwin":
        return install_tesseract_macos()
    elif system == "linux":
        return install_tesseract_linux()
    else:
        print(f"❌ Unsupported operating system: {system}")
        return False


def setup_python_environment() -> bool:
    """Set up Python virtual environment and install dependencies."""
    print("Setting up Python environment...")

    # Check if virtual environment exists
    venv_path = Path("venv")
    if venv_path.exists():
        print("✅ Virtual environment already exists")
    else:
        print("Creating virtual environment...")
        result = run_command([sys.executable, "-m", "venv", "venv"])
        if not result or result.returncode != 0:
            print("❌ Failed to create virtual environment")
            return False
        print("✅ Virtual environment created")

    # Determine pip path
    if platform.system().lower() == "windows":
        pip_path = venv_path / "Scripts" / "pip.exe"
    else:
        pip_path = venv_path / "bin" / "pip"

    # Install dependencies
    print("Installing Python dependencies...")
    result = run_command([str(pip_path), "install", "-e", "."])
    if not result or result.returncode != 0:
        print("❌ Failed to install dependencies")
        return False

    print("✅ Python dependencies installed")
    return True


def main() -> None:
    """Main setup function."""
    print("🚀 OCR Invoice Parser - Cross-Platform Setup")
    print("=" * 50)

    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)

    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")

    # Check and install Tesseract
    if not check_tesseract():
        if not install_tesseract():
            print("❌ Tesseract installation failed")
            sys.exit(1)

    # Set up Python environment
    if not setup_python_environment():
        print("❌ Python environment setup failed")
        sys.exit(1)

    print("\n🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Activate the virtual environment:")
    if platform.system().lower() == "windows":
        print("   venv\\Scripts\\activate")
    else:
        print("   source venv/bin/activate")
    print("2. Run the GUI application:")
    print("   python run_ocr_gui.py")
    print("3. Or use the CLI:")
    print("   ocrinvoice --help")


if __name__ == "__main__":
    main()
