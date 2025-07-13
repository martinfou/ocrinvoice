"""
Business Alias Table Widget

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
    QWidget,
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QPoint
from PyQt6.QtGui import QFont, QColor


class AliasTable(QTableWidget):
    """
    Custom table widget for displaying business aliases.

    Provides a sortable, searchable table with context menus
    and selection handling for business alias management.
    """

    # Custom signals
    alias_selected = pyqtSignal(dict)  # Emitted when an alias is selected
    alias_double_clicked = pyqtSignal(dict)  # Emitted when an alias is double-clicked
    alias_updated = pyqtSignal(
        dict
    )  # Emitted when an alias is updated via direct editing

    def __init__(self, parent: Optional[QWidget] = None) -> None:
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

        # Flag to prevent recursive updates
        self._updating_item = False

    def _setup_table(self) -> None:
        """Set up the basic table properties."""
        # Set column count for business aliases
        self.setColumnCount(5)

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
        self.verticalHeader().setDefaultSectionSize(30)  # type: ignore[union-attr]

    def _setup_headers(self) -> None:
        """Set up the table headers for business aliases."""
        # Set header labels for business aliases
        headers = [
            "Company Name",
            "Canonical Name",
            "Match Type",
            "Usage Count",
            "Last Used",
        ]
        self.setHorizontalHeaderLabels(headers)

        # Configure header behavior
        header = self.horizontalHeader()
        header.setStretchLastSection(False)  # type: ignore[union-attr]
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)  # type: ignore[union-attr]
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # type: ignore[union-attr]
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # type: ignore[union-attr]
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # type: ignore[union-attr]
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # type: ignore[union-attr]

        # Set header font
        header_font = QFont()
        header_font.setBold(True)
        header_font.setPointSize(10)
        header.setFont(header_font)  # type: ignore[union-attr]

    def _setup_behavior(self) -> None:
        """Set up table behavior and signals."""
        # Connect selection change signal
        self.itemSelectionChanged.connect(self._on_selection_changed)

        # Connect double-click signal
        self.itemDoubleClicked.connect(self._on_item_double_clicked)

        # Connect item changed signal for direct editing
        self.itemChanged.connect(self._on_item_changed)

        # Set context menu policy
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)

    def load_aliases(self, aliases: List[Dict[str, Any]]) -> None:
        """
        Load business aliases into the table.

        Args:
            aliases: List of alias dictionaries with company_name, canonical_name, match_type, etc.
        """
        # Clear existing data
        self.clearContents()
        self._aliases = aliases.copy()

        # Update filtered list
        self._filtered_aliases = self._aliases.copy()

        # Populate table
        self._populate_table()

        # Update row count
        self.setRowCount(len(self._filtered_aliases))

    def _populate_table(self) -> None:
        """Populate the table with alias data."""
        # Set flag to prevent recursive updates during population
        self._updating_item = True

        self.setRowCount(len(self._filtered_aliases))

        for row, alias_data in enumerate(self._filtered_aliases):
            # Company Name (editable)
            company_item = QTableWidgetItem(alias_data.get("company_name", ""))
            company_item.setData(Qt.ItemDataRole.UserRole, alias_data)
            company_item.setFlags(company_item.flags() | Qt.ItemFlag.ItemIsEditable)
            self.setItem(row, 0, company_item)

            # Canonical Name (editable)
            canonical_item = QTableWidgetItem(alias_data.get("canonical_name", ""))
            canonical_item.setData(Qt.ItemDataRole.UserRole, alias_data)
            canonical_item.setFlags(canonical_item.flags() | Qt.ItemFlag.ItemIsEditable)
            self.setItem(row, 1, canonical_item)

            # Match Type (editable via dropdown)
            match_type = alias_data.get("match_type", "Unknown")
            match_type_item = QTableWidgetItem(match_type)
            match_type_item.setData(Qt.ItemDataRole.UserRole, alias_data)
            match_type_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            match_type_item.setFlags(
                match_type_item.flags() | Qt.ItemFlag.ItemIsEditable
            )

            # Color code match types
            if match_type == "Exact":
                match_type_item.setBackground(QColor(200, 255, 200))  # Light green
            elif match_type == "Partial":
                match_type_item.setBackground(QColor(255, 255, 200))  # Light yellow
            elif match_type == "Fuzzy":
                match_type_item.setBackground(QColor(255, 200, 200))  # Light red
            else:
                match_type_item.setBackground(QColor(240, 240, 240))  # Light gray

            self.setItem(row, 2, match_type_item)

            # Usage Count (read-only)
            usage_count = alias_data.get("usage_count", 0)
            usage_item = QTableWidgetItem(str(usage_count))
            usage_item.setData(Qt.ItemDataRole.UserRole, alias_data)
            usage_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            usage_item.setFlags(usage_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.setItem(row, 3, usage_item)

            # Last Used (read-only)
            last_used = alias_data.get("last_used", "")
            last_used_item = QTableWidgetItem(str(last_used))
            last_used_item.setData(Qt.ItemDataRole.UserRole, alias_data)
            last_used_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            last_used_item.setFlags(
                last_used_item.flags() & ~Qt.ItemFlag.ItemIsEditable
            )
            self.setItem(row, 4, last_used_item)

        # Clear the flag after population
        self._updating_item = False

    def get_selected_alias(self) -> Optional[Dict[str, Any]]:
        """
        Get the currently selected alias data.

        Returns:
            Dictionary containing the selected alias data, or None if no selection
        """
        current_row = self.currentRow()
        if current_row >= 0 and current_row < len(self._filtered_aliases):
            return self._filtered_aliases[current_row]
        return None

    def search_aliases(self, search_text: str) -> None:
        """
        Search aliases by company name or canonical name.

        Args:
            search_text: Text to search for
        """
        self._current_search = search_text.lower().strip()
        self._search_timer.start(300)  # Debounce search

    def _perform_search(self) -> None:
        """Perform the actual search operation."""
        if not self._current_search:
            self._filtered_aliases = self._aliases.copy()
        else:
            self._filtered_aliases = [
                alias
                for alias in self._aliases
                if (
                    self._current_search in alias.get("company_name", "").lower()
                    or self._current_search in alias.get("canonical_name", "").lower()
                )
            ]

        self._populate_table()
        self.setRowCount(len(self._filtered_aliases))

    def _on_selection_changed(self) -> None:
        """Handle selection change events."""
        selected_alias = self.get_selected_alias()
        if selected_alias:
            self.alias_selected.emit(selected_alias)

    def _on_item_double_clicked(self, item: QTableWidgetItem) -> None:
        """Handle double-click events on table items."""
        alias_data = item.data(Qt.ItemDataRole.UserRole)
        if alias_data:
            self.alias_double_clicked.emit(alias_data)

    def _on_item_changed(self, item: QTableWidgetItem) -> None:
        """Handle item change events for direct editing."""
        # Prevent recursive updates
        if self._updating_item:
            return

        row = item.row()
        if row >= 0 and row < len(self._filtered_aliases):
            # Get the original alias data
            original_alias = self._filtered_aliases[row].copy()

            # Update the alias data based on the changed column
            column = item.column()
            new_value = item.text().strip()

            if column == 0:  # Company Name
                original_alias["company_name"] = new_value
            elif column == 1:  # Canonical Name
                original_alias["canonical_name"] = new_value
            elif column == 2:  # Match Type
                # Validate match type
                valid_types = ["Exact", "Partial", "Fuzzy"]
                if new_value in valid_types:
                    original_alias["match_type"] = new_value
                    # Update background color
                    if new_value == "Exact":
                        item.setBackground(QColor(200, 255, 200))  # Light green
                    elif new_value == "Partial":
                        item.setBackground(QColor(255, 255, 200))  # Light yellow
                    elif new_value == "Fuzzy":
                        item.setBackground(QColor(255, 200, 200))  # Light red
                else:
                    # Revert to original value if invalid
                    item.setText(original_alias.get("match_type", "Exact"))
                    return

            # Update the filtered aliases list
            self._filtered_aliases[row] = original_alias

            # Update the main aliases list
            for i, alias in enumerate(self._aliases):
                if alias.get("company_name") == original_alias.get(
                    "company_name"
                ) and alias.get("canonical_name") == original_alias.get(
                    "canonical_name"
                ):
                    self._aliases[i] = original_alias
                    break

            # Emit the updated alias
            self.alias_updated.emit(original_alias)

    def _show_context_menu(self, position: QPoint) -> None:
        """Show context menu for table items."""
        menu = QMenu(self)

        # Get the item at the clicked position
        item = self.itemAt(position)
        if item:
            # Add context menu items
            edit_action = menu.addAction("✏️ Edit Alias")
            delete_action = menu.addAction("🗑️ Delete Alias")
            menu.addSeparator()
            copy_company_action = menu.addAction("📋 Copy Company Name")
            copy_canonical_action = menu.addAction("📋 Copy Canonical Name")

            # Show menu and handle action
            action = menu.exec(self.mapToGlobal(position))

            if action == edit_action:
                alias_data = item.data(Qt.ItemDataRole.UserRole)
                if alias_data:
                    self.alias_double_clicked.emit(alias_data)
            elif action == delete_action:
                self._delete_selected_alias()
            elif action == copy_company_action:
                alias_data = item.data(Qt.ItemDataRole.UserRole)
                if alias_data:
                    self._copy_to_clipboard(alias_data.get("company_name", ""))
            elif action == copy_canonical_action:
                alias_data = item.data(Qt.ItemDataRole.UserRole)
                if alias_data:
                    self._copy_to_clipboard(alias_data.get("canonical_name", ""))

    def _delete_selected_alias(self) -> None:
        """Delete the currently selected alias."""
        selected_alias = self.get_selected_alias()
        if selected_alias:
            # Remove from both lists
            if selected_alias in self._aliases:
                self._aliases.remove(selected_alias)
            if selected_alias in self._filtered_aliases:
                self._filtered_aliases.remove(selected_alias)

            # Clear selection before refreshing
            self.clearSelection()

            # Refresh display
            self._populate_table()
            self.setRowCount(len(self._filtered_aliases))

    def _copy_to_clipboard(self, text: str) -> None:
        """Copy text to clipboard."""
        clipboard = QApplication.clipboard()
        clipboard.setText(text)

    def clear_search(self) -> None:
        """Clear the current search and show all aliases."""
        self._current_search = ""
        self._filtered_aliases = self._aliases.copy()
        self._populate_table()
        self.setRowCount(len(self._filtered_aliases))

    def get_all_aliases(self) -> List[Dict[str, Any]]:
        """Get all aliases (not filtered)."""
        return self._aliases.copy()

    def get_filtered_aliases(self) -> List[Dict[str, Any]]:
        """Get currently filtered aliases."""
        return self._filtered_aliases.copy()

    def refresh_display(self) -> None:
        """Refresh the table display."""
        self._populate_table()

    def select_alias(self, company_name: str) -> bool:
        """
        Select an alias by company name.

        Args:
            company_name: Company name to select

        Returns:
            True if alias was found and selected, False otherwise
        """
        for row, alias_data in enumerate(self._filtered_aliases):
            if alias_data.get("company_name", "").lower() == company_name.lower():
                self.selectRow(row)
                return True
        return False

    def add_alias(self, alias_data: Dict[str, Any]) -> None:
        """
        Add a new alias to the table.

        Args:
            alias_data: Dictionary containing alias information
        """
        self._aliases.append(alias_data)
        if not self._current_search or (
            self._current_search in alias_data.get("company_name", "").lower()
            or self._current_search in alias_data.get("canonical_name", "").lower()
        ):
            self._filtered_aliases.append(alias_data)

        self._populate_table()
        self.setRowCount(len(self._filtered_aliases))

    def update_alias(
        self, old_company_name: str, new_alias_data: Dict[str, Any]
    ) -> bool:
        """
        Update an existing alias.

        Args:
            old_company_name: Company name of the alias to update
            new_alias_data: New alias data

        Returns:
            True if alias was found and updated, False otherwise
        """
        # Update in main list
        for i, alias in enumerate(self._aliases):
            if alias.get("company_name", "").lower() == old_company_name.lower():
                self._aliases[i] = new_alias_data
                break
        else:
            return False

        # Update in filtered list
        for i, alias in enumerate(self._filtered_aliases):
            if alias.get("company_name", "").lower() == old_company_name.lower():
                self._filtered_aliases[i] = new_alias_data
                break

        self._populate_table()
        return True
