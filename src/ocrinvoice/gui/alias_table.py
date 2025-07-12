"""
Alias Table Widget

A custom QTableWidget for displaying and managing business aliases
with sorting, selection, and search capabilities.
"""

from typing import Dict, Any, Optional, List
from PyQt6.QtWidgets import (
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QAbstractItemView,
    QMenu,
    QApplication,
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QColor


class AliasTable(QTableWidget):
    """
    Custom table widget for displaying business aliases.

    Provides a sortable, searchable table with context menus
    and selection handling for alias management.
    """

    # Custom signals
    alias_selected = pyqtSignal(dict)  # Emitted when an alias is selected
    alias_double_clicked = pyqtSignal(dict)  # Emitted when an alias is double-clicked

    def __init__(self, parent=None):
        super().__init__(parent)

        # Table setup
        self._setup_table()
        self._setup_headers()
        self._setup_behavior()

        # Data storage
        self._aliases: List[Dict[str, Any]] = []
        self._filtered_aliases: List[Dict[str, Any]] = []

        # Search functionality
        self._search_timer = QTimer()
        self._search_timer.setSingleShot(True)
        self._search_timer.timeout.connect(self._perform_search)
        self._current_search = ""

    def _setup_table(self) -> None:
        """Set up the basic table properties."""
        # Set column count
        self.setColumnCount(4)

        # Set selection behavior
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

        # Enable sorting
        self.setSortingEnabled(True)

        # Set alternating row colors
        self.setAlternatingRowColors(True)

        # Set font
        font = QFont()
        font.setPointSize(10)
        self.setFont(font)

        # Set row height
        self.verticalHeader().setDefaultSectionSize(30)

    def _setup_headers(self) -> None:
        """Set up the table headers."""
        # Set header labels
        headers = ["Company Name", "Official Name", "Match Type", "Usage Count"]
        self.setHorizontalHeaderLabels(headers)

        # Configure header behavior
        header = self.horizontalHeader()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)  # Company Name
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Official Name
        header.setSectionResizeMode(
            2, QHeaderView.ResizeMode.ResizeToContents
        )  # Match Type
        header.setSectionResizeMode(
            3, QHeaderView.ResizeMode.ResizeToContents
        )  # Usage Count

        # Set header font
        header_font = QFont()
        header_font.setBold(True)
        header_font.setPointSize(10)
        header.setFont(header_font)

    def _setup_behavior(self) -> None:
        """Set up table behavior and signals."""
        # Connect selection change signal
        self.itemSelectionChanged.connect(self._on_selection_changed)

        # Connect double-click signal
        self.itemDoubleClicked.connect(self._on_item_double_clicked)

        # Set context menu policy
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)

    def load_aliases(
        self, exact_matches: Dict[str, str], partial_matches: Dict[str, str]
    ) -> None:
        """
        Load aliases into the table.

        Args:
            exact_matches: Dictionary of exact match aliases
            partial_matches: Dictionary of partial match aliases
        """
        # Clear existing data
        self.clearContents()
        self._aliases = []

        # Process exact matches
        for alias, official_name in exact_matches.items():
            self._aliases.append(
                {
                    "alias": alias,
                    "official_name": official_name,
                    "match_type": "Exact",
                    "usage_count": 0,  # TODO: Implement usage tracking
                }
            )

        # Process partial matches
        for alias, official_name in partial_matches.items():
            self._aliases.append(
                {
                    "alias": alias,
                    "official_name": official_name,
                    "match_type": "Partial",
                    "usage_count": 0,  # TODO: Implement usage tracking
                }
            )

        # Update filtered list
        self._filtered_aliases = self._aliases.copy()

        # Populate table
        self._populate_table()

        # Update row count
        self.setRowCount(len(self._filtered_aliases))

    def _populate_table(self) -> None:
        """Populate the table with alias data."""
        self.setRowCount(len(self._filtered_aliases))

        for row, alias_data in enumerate(self._filtered_aliases):
            # Company Name
            company_item = QTableWidgetItem(alias_data["alias"])
            company_item.setData(Qt.ItemDataRole.UserRole, alias_data)
            self.setItem(row, 0, company_item)

            # Official Name
            official_item = QTableWidgetItem(alias_data["official_name"])
            self.setItem(row, 1, official_item)

            # Match Type
            match_type_item = QTableWidgetItem(alias_data["match_type"])
            match_type_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            # Color code match types
            if alias_data["match_type"] == "Exact":
                match_type_item.setBackground(QColor(200, 255, 200))  # Light green
            else:
                match_type_item.setBackground(QColor(255, 255, 200))  # Light yellow

            self.setItem(row, 2, match_type_item)

            # Usage Count
            usage_item = QTableWidgetItem(str(alias_data["usage_count"]))
            usage_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.setItem(row, 3, usage_item)

    def get_selected_alias(self) -> Optional[Dict[str, Any]]:
        """
        Get the currently selected alias data.

        Returns:
            Dictionary containing alias data or None if no selection
        """
        current_row = self.currentRow()
        if current_row >= 0 and current_row < len(self._filtered_aliases):
            return self._filtered_aliases[current_row]
        return None

    def search_aliases(self, search_text: str) -> None:
        """
        Search aliases and filter the table.

        Args:
            search_text: Text to search for in company and official names
        """
        self._current_search = search_text.lower()

        # Reset timer to avoid too many searches while typing
        self._search_timer.stop()
        self._search_timer.start(300)  # 300ms delay

    def _perform_search(self) -> None:
        """Perform the actual search operation."""
        if not self._current_search:
            # No search text, show all aliases
            self._filtered_aliases = self._aliases.copy()
        else:
            # Filter aliases based on search text
            self._filtered_aliases = []
            for alias_data in self._aliases:
                alias = alias_data["alias"].lower()
                official = alias_data["official_name"].lower()

                if self._current_search in alias or self._current_search in official:
                    self._filtered_aliases.append(alias_data)

        # Update table
        self._populate_table()

        # Update status (if we have access to status bar)
        if hasattr(self.parent(), "status_bar"):
            count = len(self._filtered_aliases)
            total = len(self._aliases)
            if self._current_search:
                self.parent().status_bar.showMessage(
                    f"Found {count} of {total} aliases"
                )
            else:
                self.parent().status_bar.showMessage(f"{total} aliases loaded")

    def _on_selection_changed(self) -> None:
        """Handle selection change events."""
        selected_alias = self.get_selected_alias()
        self.alias_selected.emit(selected_alias if selected_alias else {})

    def _on_item_double_clicked(self, item: QTableWidgetItem) -> None:
        """Handle double-click events on table items."""
        selected_alias = self.get_selected_alias()
        if selected_alias:
            self.alias_double_clicked.emit(selected_alias)

    def _show_context_menu(self, position) -> None:
        """Show context menu for right-click actions."""
        selected_alias = self.get_selected_alias()
        if not selected_alias:
            return

        context_menu = QMenu(self)

        # Edit action
        edit_action = context_menu.addAction("Edit Alias")
        edit_action.triggered.connect(
            lambda: self.alias_double_clicked.emit(selected_alias)
        )

        # Delete action
        delete_action = context_menu.addAction("Delete Alias")
        delete_action.triggered.connect(lambda: self._delete_selected_alias())

        # Copy actions
        context_menu.addSeparator()
        copy_alias_action = context_menu.addAction("Copy Alias")
        copy_alias_action.triggered.connect(
            lambda: self._copy_to_clipboard(selected_alias["alias"])
        )

        copy_official_action = context_menu.addAction("Copy Official Name")
        copy_official_action.triggered.connect(
            lambda: self._copy_to_clipboard(selected_alias["official_name"])
        )

        # Show menu
        context_menu.exec(self.mapToGlobal(position))

    def _delete_selected_alias(self) -> None:
        """Delete the currently selected alias."""
        selected_alias = self.get_selected_alias()
        if not selected_alias:
            return

        # This will be handled by the main window
        # We just emit a signal or call a method
        if hasattr(self.parent(), "_delete_alias"):
            self.parent()._delete_alias()

    def _copy_to_clipboard(self, text: str) -> None:
        """Copy text to clipboard."""
        clipboard = QApplication.clipboard()
        clipboard.setText(text)

    def clear_search(self) -> None:
        """Clear the current search and show all aliases."""
        self.search_aliases("")

    def get_all_aliases(self) -> List[Dict[str, Any]]:
        """Get all aliases (not filtered)."""
        return self._aliases.copy()

    def get_filtered_aliases(self) -> List[Dict[str, Any]]:
        """Get currently filtered aliases."""
        return self._filtered_aliases.copy()

    def refresh_display(self) -> None:
        """Refresh the table display."""
        self._populate_table()

    def select_alias(self, alias: str) -> bool:
        """
        Select an alias by its name.

        Args:
            alias: The alias name to select

        Returns:
            True if alias was found and selected, False otherwise
        """
        for row, alias_data in enumerate(self._filtered_aliases):
            if alias_data["alias"] == alias:
                self.selectRow(row)
                return True
        return False
