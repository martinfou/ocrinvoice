"""
Main entry point for the ocrinvoice package.

This module allows the package to be run as a module:
    python -m ocrinvoice [options]
"""

from ocrinvoice.cli.main import cli

if __name__ == "__main__":
    cli()
