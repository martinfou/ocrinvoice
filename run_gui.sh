#!/bin/bash
# GUI Launcher Script for Business Aliases Manager
# This script activates the virtual environment and launches the GUI

echo "🚀 Launching Business Aliases GUI Manager..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Creating one..."
    python3 -m venv venv
    source venv/bin/activate
    echo "📦 Installing dependencies..."
    pip install PyQt6 Pillow
else
    echo "✅ Virtual environment found. Activating..."
    source venv/bin/activate
fi

# Launch the GUI
echo "🎯 Starting GUI..."
python ocrinvoice_cli.py --gui
