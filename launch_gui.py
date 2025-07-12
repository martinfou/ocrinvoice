#!/usr/bin/env python3
"""
Simple GUI Launcher for Business Aliases Manager

This script launches the GUI without requiring package installation.
Run with: python3 launch_gui.py
"""

import sys
import os


def main() -> None:
    """Launch the GUI application."""
    # Add the src directory to the Python path
    src_path = os.path.join(os.path.dirname(__file__), "src")
    sys.path.insert(0, src_path)

    try:
        # Import and run the GUI
        from ocrinvoice.gui.main_window import main

        print("🚀 Launching Business Aliases GUI Manager...")
        main()
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("\n📋 Troubleshooting:")
        print("1. Make sure PyQt6 is installed:")
        print("   pip3 install PyQt6")
        print("\n2. If you're on macOS with Homebrew Python, try:")
        print("   pip3 install --user PyQt6")
        print("\n3. Or use a virtual environment:")
        print("   python3 -m venv venv")
        print("   source venv/bin/activate")
        print("   pip install PyQt6")
        print("   python launch_gui.py")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error launching GUI: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
