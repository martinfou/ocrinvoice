#!/usr/bin/env python3
"""
Convenience script to run the OCR GUI application.

Usage:
    python run_ocr_gui.py
"""

import os
import sys

from ocrinvoice.gui.ocr_main_window import main

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

if __name__ == "__main__":
    main()
