"""
Utility module for handling bundled Tesseract OCR and Poppler binaries.

This module provides functions to locate and configure bundled binaries
when the application is packaged with PyInstaller.
"""

import os
import sys
from pathlib import Path
from typing import Optional


def get_app_directory() -> Path:
    """Get the application directory, whether running from source or PyInstaller bundle.
    
    Returns:
        Path to the application directory
    """
    if getattr(sys, 'frozen', False):
        # Running in PyInstaller bundle
        return Path(sys.executable).parent
    else:
        # Running from source
        return Path(__file__).parent.parent.parent.parent


def get_bundled_tesseract_path() -> Optional[Path]:
    """Get the path to the bundled Tesseract binary.
    
    Returns:
        Path to tesseract binary if found, None otherwise
    """
    app_dir = get_app_directory()
    
    # Check for tesseract binary in app directory
    if os.name == 'nt':  # Windows
        tesseract_path = app_dir / 'tesseract.exe'
    else:  # macOS/Linux
        tesseract_path = app_dir / 'tesseract'
    
    if tesseract_path.exists():
        return tesseract_path
    
    return None


def get_bundled_tessdata_path() -> Optional[Path]:
    """Get the path to the bundled Tesseract data directory.
    
    Returns:
        Path to tessdata directory if found, None otherwise
    """
    app_dir = get_app_directory()
    tessdata_path = app_dir / 'tessdata'
    
    if tessdata_path.exists() and tessdata_path.is_dir():
        return tessdata_path
    
    return None


def get_bundled_poppler_path() -> Optional[Path]:
    """Get the path to the bundled Poppler binaries directory.
    
    Returns:
        Path to Poppler binaries directory if found, None otherwise
    """
    app_dir = get_app_directory()
    
    # Check for Poppler binaries in app directory
    if os.name == 'nt':  # Windows
        # On Windows, Poppler binaries are typically in the main directory
        # Check if pdfinfo.exe exists
        pdfinfo_path = app_dir / 'pdfinfo.exe'
        if pdfinfo_path.exists():
            return app_dir
    else:  # macOS/Linux
        # On Unix systems, Poppler binaries are typically in the main directory
        pdfinfo_path = app_dir / 'pdfinfo'
        if pdfinfo_path.exists():
            return app_dir
    
    return None


def configure_bundled_binaries() -> None:
    """Configure the application to use bundled Tesseract and Poppler binaries.
    
    This function:
    1. Sets the TESSDATA_PREFIX environment variable
    2. Adds the app directory to PATH
    3. Configures pytesseract to use the bundled binary
    """
    app_dir = get_app_directory()
    
    # Set TESSDATA_PREFIX for Tesseract
    tessdata_path = get_bundled_tessdata_path()
    if tessdata_path:
        os.environ['TESSDATA_PREFIX'] = str(tessdata_path)
    
    # Add app directory to PATH (for Poppler binaries)
    current_path = os.environ.get('PATH', '')
    if str(app_dir) not in current_path:
        os.environ['PATH'] = str(app_dir) + os.pathsep + current_path
    
    # Configure pytesseract to use bundled binary
    tesseract_path = get_bundled_tesseract_path()
    if tesseract_path:
        try:
            import pytesseract
            pytesseract.pytesseract.tesseract_cmd = str(tesseract_path)
        except ImportError:
            pass  # pytesseract not available


def get_pdf2image_poppler_path() -> Optional[str]:
    """Get the Poppler path for pdf2image library.
    
    Returns:
        Path to Poppler binaries directory as string, or None if not found
    """
    poppler_path = get_bundled_poppler_path()
    if poppler_path:
        return str(poppler_path)
    return None


def is_bundled_binary_available(binary_name: str) -> bool:
    """Check if a bundled binary is available.
    
    Args:
        binary_name: Name of the binary to check (e.g., 'tesseract', 'pdfinfo')
        
    Returns:
        True if the binary is available, False otherwise
    """
    app_dir = get_app_directory()
    
    if os.name == 'nt':  # Windows
        binary_path = app_dir / f'{binary_name}.exe'
    else:  # macOS/Linux
        binary_path = app_dir / binary_name
    
    return binary_path.exists()


def get_bundled_binaries_info() -> dict:
    """Get information about available bundled binaries.
    
    Returns:
        Dictionary with information about bundled binaries
    """
    return {
        'app_directory': str(get_app_directory()),
        'tesseract_available': is_bundled_binary_available('tesseract'),
        'tessdata_available': get_bundled_tessdata_path() is not None,
        'poppler_available': is_bundled_binary_available('pdfinfo'),
        'tesseract_path': str(get_bundled_tesseract_path()) if get_bundled_tesseract_path() else None,
        'tessdata_path': str(get_bundled_tessdata_path()) if get_bundled_tessdata_path() else None,
        'poppler_path': str(get_bundled_poppler_path()) if get_bundled_poppler_path() else None,
    } 