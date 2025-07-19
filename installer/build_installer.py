#!/usr/bin/env python3
"""
Windows Installer Build Script

This script automates the process of creating a Windows installer for the OCR Invoice Parser.
It builds the PyInstaller executable and then creates an NSIS installer.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
import argparse


def run_command(command, cwd=None, check=True):
    """Run a command and return the result."""
    print(f"Running: {command}")
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=check
        )
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(f"STDERR: {result.stderr}")
        return result
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {e}")
        if e.stdout:
            print(f"STDOUT: {e.stdout}")
        if e.stderr:
            print(f"STDERR: {e.stderr}")
        return e


def check_dependencies():
    """Check if required dependencies are installed."""
    print("Checking dependencies...")
    
    # Check PyInstaller
    result = run_command("pyinstaller --version", check=False)
    if result.returncode != 0:
        print("PyInstaller not found. Installing...")
        result = run_command("pip install pyinstaller")
        if result.returncode != 0:
            print("Failed to install PyInstaller")
            return False
    else:
        print("PyInstaller found")
    
    # Check NSIS (optional, will warn if not found)
    result = run_command("makensis /VERSION", check=False)
    if result.returncode != 0:
        print("NSIS not found. Please install NSIS to create the installer.")
        print("   Download from: https://nsis.sourceforge.io/Download")
        return False
    else:
        print("NSIS found")
        return True


def clean_build_directories():
    """Clean previous build artifacts."""
    print("Cleaning build directories...")
    
    dirs_to_clean = ["build", "dist", "__pycache__"]
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"   Removed {dir_name}")
    
    # Clean .spec files
    for spec_file in Path(".").glob("*.spec"):
        spec_file.unlink()
        print(f"   Removed {spec_file}")


def build_executable():
    """Build the PyInstaller executable."""
    print("Building executable with PyInstaller...")
    
    # Use the existing PyInstaller spec if available
    spec_file = "OCRInvoiceParser.spec"
    if os.path.exists(spec_file):
        print(f"Using existing spec file: {spec_file}")
        result = run_command(f"pyinstaller {spec_file}")
    else:
        print("Creating new PyInstaller build...")
        result = run_command(
            "pyinstaller --onefile --windowed --name OCRInvoiceParser "
            "--add-data 'config;config' --add-data 'docs;docs' "
            "src/ocrinvoice/gui/ocr_main_window.py"
        )
    
    if result.returncode != 0:
        print("PyInstaller build failed")
        return False
    
    print("Executable built successfully")
    return True


def prepare_tesseract():
    """Prepare Tesseract OCR for inclusion in the installer."""
    print("Preparing Tesseract OCR...")
    
    installer_dir = Path("installer")
    tesseract_dir = installer_dir / "tesseract"
    
    # Check if Tesseract is already prepared
    if tesseract_dir.exists() and (tesseract_dir / "tesseract-installer.exe").exists():
        print("   Tesseract OCR already prepared")
        return True
    
    # Try to run the Tesseract download script
    try:
        result = run_command("python installer/download_tesseract.py", check=False)
        if result and result.returncode == 0:
            print("   Tesseract OCR prepared successfully")
            return True
        else:
            print("   Warning: Could not prepare Tesseract OCR automatically")
            print("   The installer will prompt users to install Tesseract manually")
            return False
    except Exception as e:
        print(f"   Warning: Error preparing Tesseract OCR: {e}")
        print("   The installer will prompt users to install Tesseract manually")
        return False


def create_installer_assets():
    """Create installer assets (icons, images, etc.)."""
    print("Creating installer assets...")
    
    installer_dir = Path("installer")
    installer_dir.mkdir(exist_ok=True)
    
    # Create placeholder files if they don't exist
    assets = {
        "icon.ico": "Application icon (32x32)",
        "setup.ico": "Setup icon (32x32)", 
        "welcome.bmp": "Welcome page image (164x314)",
    }
    
    for asset, description in assets.items():
        asset_path = installer_dir / asset
        if not asset_path.exists():
            print(f"   {asset} not found - {description}")
            print(f"      Please create this file for a complete installer")
    
    # Create LICENSE file if it doesn't exist
    if not os.path.exists("LICENSE"):
        print("   Creating placeholder LICENSE file...")
        with open("LICENSE", "w") as f:
            f.write("OCR Invoice Parser License\n\n")
            f.write("This software is provided as-is for educational and personal use.\n")
            f.write("Please refer to the project documentation for usage terms.\n")


def build_installer():
    """Build the NSIS installer."""
    print("Building NSIS installer...")
    
    # Check if NSIS is available
    result = run_command("makensis /VERSION", check=False)
    if result.returncode != 0:
        print("NSIS not available. Skipping installer creation.")
        return False
    
    # Before running NSIS, check for setup.ico
    nsis_icon_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'setup.ico'))
    print(f"Checking for NSIS icon at: {nsis_icon_path}")
    if not os.path.exists(nsis_icon_path):
        print(f"ERROR: Required NSIS icon file not found: {nsis_icon_path}")
        print("Please add a valid setup.ico file to the installer directory.")
        sys.exit(1)
    else:
        print("NSIS icon file found.")

    # Build the installer
    result = run_command("makensis installer/installer.nsi")
    if result.returncode != 0:
        print("NSIS installer build failed")
        return False
    
    print("Installer built successfully")
    return True


def update_version_in_installer(version):
    """Update version in the installer script."""
    print(f"Updating installer version to {version}...")
    
    installer_script = Path("installer/installer.nsi")
    if not installer_script.exists():
        print("Installer script not found")
        return False
    
    # Clean version by removing 'v' prefix if present
    clean_version = version.lstrip('v')
    print(f"Cleaned version: {clean_version}")
    
    # Read the script
    with open(installer_script, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Update version
    import re
    content = re.sub(
        r'!define APP_VERSION "[\d.]+"',
        f'!define APP_VERSION "{clean_version}"',
        content
    )
    
    # Update VIProductVersion to use correct 4-number format
    content = re.sub(
        r'VIProductVersion "[\d.]+"',
        f'VIProductVersion "{clean_version}.0"',
        content
    )
    
    # Write back
    with open(installer_script, "w", encoding="utf-8") as f:
        f.write(content)
    
    print(f"Updated installer version to {clean_version}")
    return True


def get_current_version():
    """Get current version from pyproject.toml."""
    try:
        import toml
        with open("pyproject.toml", "r", encoding="utf-8") as f:
            data = toml.load(f)
        version = data["project"]["version"]
        print(f"✅ Read version from pyproject.toml: {version}")
        return version
    except ImportError:
        print("⚠️  toml package not found, trying alternative methods...")
        # Try reading with regex as fallback
        try:
            import re
            with open("pyproject.toml", "r", encoding="utf-8") as f:
                content = f.read()
            match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
            if match:
                version = match.group(1)
                print(f"✅ Read version with regex: {version}")
                return version
        except Exception as e:
            print(f"⚠️  Regex fallback failed: {e}")
    except Exception as e:
        print(f"⚠️  Could not read version from pyproject.toml: {e}")
    
    print("❌ Using default version: 1.3.0")
    return "1.3.0"  # Default version


def main():
    """Main build function."""
    parser = argparse.ArgumentParser(description="Build Windows installer for OCR Invoice Parser")
    parser.add_argument("--version", help="Version number for the installer")
    parser.add_argument("--skip-nsis", action="store_true", help="Skip NSIS installer creation")
    parser.add_argument("--clean", action="store_true", help="Clean build directories first")
    
    args = parser.parse_args()
    
    print("Windows Installer Build Script")
    print("=" * 50)
    
    # Get version
    version = args.version or get_current_version()
    print(f"Building version: {version}")
    
    # Clean if requested
    if args.clean:
        clean_build_directories()
    
    # Check dependencies
    nsis_available = check_dependencies()
    
    # Create installer assets
    create_installer_assets()
    
    # Prepare Tesseract OCR
    prepare_tesseract()
    
    # Update version in installer
    update_version_in_installer(version)
    
    # Build executable
    if not build_executable():
        print("Build failed")
        sys.exit(1)
    
    # Build installer (if NSIS is available and not skipped)
    if nsis_available and not args.skip_nsis:
        if not build_installer():
            print("Installer build failed")
            sys.exit(1)
    else:
        print("Skipping installer creation")
    
    print("\nBuild completed successfully!")
    print(f"Executable: dist/OCRInvoiceParser.exe")
    if nsis_available and not args.skip_nsis:
        print(f"Installer: OCRInvoiceParser-Windows-Setup-{version}.exe")
    
    print("\nNext steps:")
    print("1. Test the executable: dist/OCRInvoiceParser.exe")
    if nsis_available and not args.skip_nsis:
        print("2. Test the installer: OCRInvoiceParser-Windows-Setup-{version}.exe")
    print("3. Distribute the files to users")


if __name__ == "__main__":
    main() 