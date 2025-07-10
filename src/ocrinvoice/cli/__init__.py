"""
Command Line Interface for the Invoice OCR Parser.

This package contains all CLI-related functionality including commands,
utilities, and the main entry point for the application.
"""

from .utils import setup_logging, load_config

__all__ = [
    "setup_logging",
    "load_config",
]

# Import CLI only if click is available
try:
    from .main import cli

    __all__.append("cli")
except ImportError:
    # Click not available, CLI functionality will be limited
    pass
