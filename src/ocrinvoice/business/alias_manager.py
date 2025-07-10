"""
Business alias management.

This module contains the BusinessAliasManager class for managing
business name aliases and resolving them to full names.
"""

from typing import Dict, Optional
import logging
import json
from pathlib import Path

logger = logging.getLogger(__name__)


class BusinessAliasManager:
    """
    Business alias management system.

    This class manages business name aliases and provides methods
    for resolving aliases to full business names.
    """

    def __init__(self, alias_file: Optional[str] = None):
        """
        Initialize the business alias manager.

        Args:
            alias_file: Path to alias file (optional)
        """
        self.aliases = {}
        self.alias_file = alias_file

        if alias_file and Path(alias_file).exists():
            self.load_aliases(alias_file)

    def add_alias(self, alias: str, full_name: str) -> None:
        """
        Add a new business alias.

        Args:
            alias: Short alias name
            full_name: Full business name
        """
        self.aliases[alias.upper()] = full_name
        logger.info(f"Added alias: {alias} -> {full_name}")

    def resolve_alias(self, name: str) -> str:
        """
        Resolve alias to full business name.

        Args:
            name: Name to resolve

        Returns:
            Resolved business name or original name if no alias found
        """
        # Placeholder implementation
        logger.info(f"Resolving alias: {name}")

        # Check for exact match
        if name.upper() in self.aliases:
            return self.aliases[name.upper()]

        # Check for partial matches
        for alias, full_name in self.aliases.items():
            if alias in name.upper() or name.upper() in alias:
                return full_name

        return name

    def load_aliases(self, filepath: str) -> None:
        """
        Load aliases from file.

        Args:
            filepath: Path to alias file
        """
        # Placeholder implementation
        logger.info(f"Loading aliases from: {filepath}")

        try:
            with open(filepath, "r") as f:
                data = json.load(f)
                self.aliases.update(data)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Error loading aliases from {filepath}: {e}")

    def save_aliases(self, filepath: str) -> None:
        """
        Save aliases to file.

        Args:
            filepath: Path to save aliases to
        """
        # Placeholder implementation
        logger.info(f"Saving aliases to: {filepath}")

        try:
            with open(filepath, "w") as f:
                json.dump(self.aliases, f, indent=2)
        except OSError as e:
            logger.error(f"Error saving aliases to {filepath}: {e}")

    def get_aliases(self) -> Dict[str, str]:
        """
        Get all aliases.

        Returns:
            Dictionary of aliases
        """
        return self.aliases.copy()
