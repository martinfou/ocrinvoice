#!/usr/bin/env python3
"""
CLI Wrapper for OCR Invoice Parser with GUI Support

This script provides a command-line interface that simulates the ocrinvoice command.
Usage: python3 ocrinvoice_cli.py --gui
       python3 ocrinvoice_cli.py aliases --gui
"""

import sys
import os
import argparse


def main() -> None:
    """Main CLI entry point."""
    # Add the src directory to the Python path
    src_path = os.path.join(os.path.dirname(__file__), "src")
    sys.path.insert(0, src_path)

    parser = argparse.ArgumentParser(
        description="Invoice OCR Parser - Extract structured data from PDF invoices using OCR",  # noqa: E501
        prog="ocrinvoice",
    )

    # Add global options
    parser.add_argument(
        "--gui", action="store_true", help="Launch the GUI for managing aliases"
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose output"
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug output")
    parser.add_argument("--version", action="version", version="1.0.0")

    # Add subcommands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Aliases command
    aliases_parser = subparsers.add_parser(
        "aliases", help="Manage business name aliases"
    )
    aliases_parser.add_argument(
        "--gui", action="store_true", help="Launch the GUI for managing aliases"
    )
    aliases_parser.add_argument(
        "subcommand",
        nargs="?",
        choices=["list", "add", "remove", "test"],
        help="Alias subcommand",
    )

    # Parse arguments
    args = parser.parse_args()

    # Handle GUI launch
    if args.gui or (hasattr(args, "gui") and args.gui):
        try:
            from ocrinvoice.gui.main_window import main

            print("🚀 Launching Business Aliases GUI Manager...")
            main()
            return
        except ImportError as e:
            print(f"❌ Error: GUI not available - {e}")
            print("Make sure PyQt6 is installed: pip3 install PyQt6")
            sys.exit(1)
        except Exception as e:
            print(f"❌ Error launching GUI: {e}")
            sys.exit(1)

    # Handle other commands
    if args.command == "aliases":
        if args.subcommand == "list":
            print("📋 Listing aliases...")
            # TODO: Implement alias listing
            print("(Alias listing will be implemented)")
        elif args.subcommand == "add":
            print("➕ Adding alias...")
            # TODO: Implement alias adding
            print("(Alias adding will be implemented)")
        elif args.subcommand == "remove":
            print("🗑️ Removing alias...")
            # TODO: Implement alias removal
            print("(Alias removal will be implemented)")
        elif args.subcommand == "test":
            print("🧪 Testing alias...")
            # TODO: Implement alias testing
            print("(Alias testing will be implemented)")
        else:
            print("📋 Business Aliases Management")
            print("Use --gui to launch the graphical interface")
            print("Available subcommands: list, add, remove, test")
    else:
        # Show help if no command specified
        parser.print_help()


if __name__ == "__main__":
    main()
