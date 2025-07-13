"""
Official Names Table Widget

A custom QTableWidget for displaying and managing official business names
with sorting, selection, and editing capabilities.
"""

from typing import Optional, List
from PyQt6.QtWidgets import (
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QAbstractItemView,
    QMenu,
    QApplication,
    QWidget,
    QMessageBox,
    QInputDialog,
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QPoint
from PyQt6.QtGui import QFont


class OfficialNamesTable(QTableWidget):
    """
    Custom table widget for displaying official business names.

    Provides a sortable, searchable table with context menus
    and selection handling for official name management.
    """

    # Custom signals
    official_name_selected = pyqtSignal(
        str
    )  # Emitted when an official name is selected
    official_name_double_clicked = pyqtSignal(
        str
    )  # Emitted when an official name is double-clicked
    official_name_updated = pyqtSignal(
        str, str
    )  # Emitted when an official name is updated (old, new)
    official_name_deleted = pyqtSignal(str)  # Emitted when an official name is deleted

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        # Table setup
        self._setup_table()
        self._setup_headers()
        self._setup_behavior()

        # Data storage
        self._official_names: List[str] = []
        self._filtered_names: List[str] = []

        # Search functionality
        self._search_timer = QTimer()
        self._search_timer.setSingleShot(True)
        self._search_timer.timeout.connect(self._perform_search)
        self._current_search = ""

        # Flag to prevent recursive updates
        self._updating_item = False

    def _setup_table(self) -> None:
        """Set up the basic table properties."""
        # Set column count for official names
        self.setColumnCount(3)

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
        """Set up the table headers for official names."""
        # Set header labels for official names
        headers = [
            "Official Name",
            "Usage Count",
            "Last Used",
        ]
        self.setHorizontalHeaderLabels(headers)

        # Configure header behavior
        header = self.horizontalHeader()
        header.setStretchLastSection(False)  # type: ignore[union-attr]
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)  # type: ignore[union-attr]
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # type: ignore[union-attr]
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # type: ignore[union-attr]

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

    def load_official_names(self, official_names: List[str]) -> None:
        """
        Load official names into the table.

        Args:
            official_names: List of official business names
        """
        # Clear existing data
        self.clearContents()
        self._official_names = official_names.copy()

        # Update filtered list
        self._filtered_names = self._official_names.copy()

        # Populate table
        self._populate_table()

        # Update row count
        self.setRowCount(len(self._filtered_names))

    def _populate_table(self) -> None:
        """Populate the table with official name data."""
        # Set flag to prevent recursive updates during population
        self._updating_item = True

        self.setRowCount(len(self._filtered_names))

        for row, official_name in enumerate(self._filtered_names):
            # Official Name (editable)
            name_item = QTableWidgetItem(official_name)
            name_item.setFlags(name_item.flags() | Qt.ItemFlag.ItemIsEditable)
            self.setItem(row, 0, name_item)

            # Usage Count (read-only, placeholder for future implementation)
            usage_item = QTableWidgetItem("0")
            usage_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            usage_item.setFlags(usage_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.setItem(row, 1, usage_item)

            # Last Used (read-only, placeholder for future implementation)
            last_used_item = QTableWidgetItem("")
            last_used_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            last_used_item.setFlags(
                last_used_item.flags() & ~Qt.ItemFlag.ItemIsEditable
            )
            self.setItem(row, 2, last_used_item)

        # Clear the flag after population
        self._updating_item = False

    def get_selected_official_name(self) -> Optional[str]:
        """
        Get the currently selected official name.

        Returns:
            The selected official name, or None if no selection
        """
        current_row = self.currentRow()
        if current_row >= 0 and current_row < len(self._filtered_names):
            return self._filtered_names[current_row]
        return None

    def search_official_names(self, search_text: str) -> None:
        """
        Search official names.

        Args:
            search_text: Text to search for
        """
        self._current_search = search_text.lower().strip()
        self._search_timer.start(300)  # Debounce search

    def _perform_search(self) -> None:
        """Perform the actual search operation."""
        if not self._current_search:
            self._filtered_names = self._official_names.copy()
        else:
            self._filtered_names = [
                name
                for name in self._official_names
                if self._current_search in name.lower()
            ]

        self._populate_table()
        self.setRowCount(len(self._filtered_names))

    def _on_selection_changed(self) -> None:
        """Handle selection change events."""
        selected_name = self.get_selected_official_name()
        if selected_name:
            self.official_name_selected.emit(selected_name)

    def _on_item_double_clicked(self, item: QTableWidgetItem) -> None:
        """Handle double-click events on table items."""
        official_name = item.text()
        self.official_name_double_clicked.emit(official_name)

    def _on_item_changed(self, item: QTableWidgetItem) -> None:
        """Handle item change events for direct editing."""
        # Prevent recursive updates
        if self._updating_item:
            return

        row = item.row()
        if row >= 0 and row < len(self._filtered_names):
            column = item.column()
            if column == 0:  # Official Name column
                old_name = self._filtered_names[row]
                new_name = item.text().strip()

                if new_name and new_name != old_name:
                    # Update the filtered names list
                    self._filtered_names[row] = new_name

                    # Update the main names list
                    for i, name in enumerate(self._official_names):
                        if name == old_name:
                            self._official_names[i] = new_name
                            break

                    # Emit the updated official name
                    self.official_name_updated.emit(old_name, new_name)

    def _show_context_menu(self, position: QPoint) -> None:
        """Show context menu for table items."""
        menu = QMenu(self)

        # Get the item at the clicked position
        item = self.itemAt(position)
        if item:
            # Add context menu items
            edit_action = menu.addAction("✏️ Edit Name")
            delete_action = menu.addAction("🗑️ Delete Name")
            menu.addSeparator()
            copy_action = menu.addAction("📋 Copy Name")

            # Show menu and handle action
            action = menu.exec(self.mapToGlobal(position))

            if action == edit_action:
                self._edit_official_name(item)
            elif action == delete_action:
                self._delete_official_name(item)
            elif action == copy_action:
                self._copy_to_clipboard(item.text())

    def _edit_official_name(self, item: QTableWidgetItem) -> None:
        """Edit an official name via dialog."""
        old_name = item.text()
        new_name, ok = QInputDialog.getText(
            self, "Edit Official Name", "Enter new official name:", text=old_name
        )

        if ok and new_name.strip() and new_name.strip() != old_name:
            new_name = new_name.strip()
            item.setText(new_name)
            # The _on_item_changed will handle the update

    def _delete_official_name(self, item: QTableWidgetItem) -> None:
        """Delete an official name."""
        official_name = item.text()
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete the official name '{official_name}'?\n\n"
            "This will also remove all aliases that reference this name.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            # Remove from lists
            if official_name in self._official_names:
                self._official_names.remove(official_name)
            if official_name in self._filtered_names:
                self._filtered_names.remove(official_name)

            # Refresh display
            self._populate_table()
            self.setRowCount(len(self._filtered_names))

            # Emit deletion signal
            self.official_name_deleted.emit(official_name)

    def _copy_to_clipboard(self, text: str) -> None:
        """Copy text to clipboard."""
        clipboard = QApplication.clipboard()
        clipboard.setText(text)

    def clear_search(self) -> None:
        """Clear the current search and show all official names."""
        self._current_search = ""
        self._filtered_names = self._official_names.copy()
        self._populate_table()
        self.setRowCount(len(self._filtered_names))

    def get_all_official_names(self) -> List[str]:
        """Get all official names (not filtered)."""
        return self._official_names.copy()

    def get_filtered_official_names(self) -> List[str]:
        """Get currently filtered official names."""
        return self._filtered_names.copy()

    def refresh_display(self) -> None:
        """Refresh the table display."""
        self._populate_table()

    def select_official_name(self, name: str) -> bool:
        """
        Select an official name.

        Args:
            name: Official name to select

        Returns:
            True if name was found and selected, False otherwise
        """
        for row, official_name in enumerate(self._filtered_names):
            if official_name.lower() == name.lower():
                self.selectRow(row)
                return True
        return False

    def add_official_name(self, name: str) -> None:
        """
        Add a new official name to the table.

        Args:
            name: Official name to add
        """
        if name not in self._official_names:
            self._official_names.append(name)
            if not self._current_search or self._current_search in name.lower():
                self._filtered_names.append(name)

            self._populate_table()
            self.setRowCount(len(self._filtered_names))

    def update_official_name(self, old_name: str, new_name: str) -> bool:
        """
        Update an existing official name.

        Args:
            old_name: Current official name
            new_name: New official name

        Returns:
            True if name was found and updated, False otherwise
        """
        # Update in main list
        for i, name in enumerate(self._official_names):
            if name == old_name:
                self._official_names[i] = new_name
                break
        else:
            return False

        # Update in filtered list
        for i, name in enumerate(self._filtered_names):
            if name == old_name:
                self._filtered_names[i] = new_name
                break

        self._populate_table()
        return True
