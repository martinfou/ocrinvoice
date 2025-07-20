"""
Category Table Widget

A table widget for displaying and managing CRA expense categories in the GUI.
"""

from typing import Dict, Optional, List
from PyQt6.QtWidgets import (
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QAbstractItemView,
    QMenu,
    QMessageBox,
)
from PyQt6.QtCore import pyqtSignal, Qt, QTimer
from PyQt6.QtGui import QColor, QAction


class CategoryTable(QTableWidget):
    """
    Table widget for displaying and managing CRA expense categories.

    Displays categories in a table format with columns for:
    - Category Name
    - Description
    - CRA Code
    """

    # Custom signals
    category_selected = pyqtSignal(dict)  # Emitted when a category is selected
    category_double_clicked = pyqtSignal(
        dict
    )  # Emitted when a category is double-clicked
    delete_category_requested = pyqtSignal(str)  # Emitted when delete is requested

    def __init__(self, parent=None):
        super().__init__(parent)
        self.categories: List[Dict[str, str]] = []
        self._filtered_categories: List[Dict[str, str]] = []

        # Search functionality
        self._search_timer = QTimer()
        self._search_timer.setSingleShot(True)
        self._search_timer.timeout.connect(self._perform_search)
        self._current_search = ""

        self._setup_ui()
        self._setup_connections()

    def _setup_ui(self) -> None:
        """Set up the table UI."""
        # Set table properties
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setSortingEnabled(True)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)

        # Set up columns
        self.setColumnCount(3)
        self.setHorizontalHeaderLabels(["Category Name", "Description", "CRA Code"])

        # Configure header
        header = self.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)

        # Set up vertical header
        self.verticalHeader().setVisible(False)

    def _setup_connections(self) -> None:
        """Set up signal connections."""
        self.itemSelectionChanged.connect(self._on_selection_changed)
        self.itemDoubleClicked.connect(self._on_item_double_clicked)
        self.customContextMenuRequested.connect(self._show_context_menu)

    def load_categories(self, categories: List[Dict[str, str]]) -> None:
        """
        Load categories into the table.

        Args:
            categories: List of category dictionaries
        """
        self.categories = categories.copy()
        self._filtered_categories = self.categories.copy()
        self._populate_table()

    def _populate_table(self) -> None:
        """Populate the table with category data."""
        self.setRowCount(len(self._filtered_categories))

        for row, category in enumerate(self._filtered_categories):
            # Category Name (not editable - use edit dialog instead)
            name_item = QTableWidgetItem(category.get("name", ""))
            name_item.setData(Qt.ItemDataRole.UserRole, category.get("id", ""))
            name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.setItem(row, 0, name_item)

            # Description (not editable - use edit dialog instead)
            desc_item = QTableWidgetItem(category.get("description", ""))
            desc_item.setFlags(desc_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.setItem(row, 1, desc_item)

            # CRA Code (not editable)
            code_item = QTableWidgetItem(category.get("cra_code", ""))
            code_item.setFlags(code_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.setItem(row, 2, code_item)

    def search_categories(self, search_text: str) -> None:
        """
        Search categories by name, description, or CRA code.

        Args:
            search_text: Text to search for
        """
        self._current_search = search_text.lower().strip()
        self._search_timer.start(300)  # Debounce search

    def _perform_search(self) -> None:
        """Perform the actual search operation."""
        if not self._current_search:
            self._filtered_categories = self.categories.copy()
        else:
            self._filtered_categories = [
                category
                for category in self.categories
                if (
                    self._current_search in category.get("name", "").lower()
                    or self._current_search in category.get("description", "").lower()
                    or self._current_search in category.get("cra_code", "").lower()
                )
            ]

        self._populate_table()
        self.setRowCount(len(self._filtered_categories))

    def clear_search(self) -> None:
        """Clear the current search and show all categories."""
        self._current_search = ""
        self._filtered_categories = self.categories.copy()
        self._populate_table()

    def get_selected_category(self) -> Optional[Dict[str, str]]:
        """
        Get the currently selected category.

        Returns:
            Selected category dictionary or None if no selection
        """
        current_row = self.currentRow()
        if current_row >= 0 and current_row < len(self._filtered_categories):
            return self._filtered_categories[current_row]
        return None

    def get_selected_category_id(self) -> Optional[str]:
        """
        Get the ID of the currently selected category.

        Returns:
            Selected category ID or None if no selection
        """
        category = self.get_selected_category()
        return category.get("id") if category else None

    def select_category(self, category_id: str) -> bool:
        """
        Select a category by ID.

        Args:
            category_id: The category ID to select

        Returns:
            True if category was found and selected, False otherwise
        """
        for row, category in enumerate(self._filtered_categories):
            if category.get("id") == category_id:
                self.selectRow(row)
                return True
        return False

    def clear_selection(self) -> None:
        """Clear the current selection."""
        self.clearSelection()

    def refresh_categories(self, categories: List[Dict[str, str]]) -> None:
        """
        Refresh the table with new category data.

        Args:
            categories: Updated list of category dictionaries
        """
        self.load_categories(categories)

    def _on_selection_changed(self) -> None:
        """Handle selection change events."""
        category = self.get_selected_category()
        if category:
            self.category_selected.emit(category)

    def _on_item_double_clicked(self, item: QTableWidgetItem) -> None:
        """Handle double-click events."""
        category = self.get_selected_category()
        if category:
            self.category_double_clicked.emit(category)

    def _show_context_menu(self, position) -> None:
        """Show context menu for the table."""
        menu = QMenu(self)
        
        # Get the item at the clicked position
        item = self.itemAt(position)
        if item:
            # Edit action
            edit_action = QAction("✏️ Edit Category", self)
            edit_action.triggered.connect(
                lambda: self.category_double_clicked.emit(self.get_selected_category())
            )
            menu.addAction(edit_action)
            
            menu.addSeparator()
            
            # Delete action
            delete_action = QAction("🗑️ Delete Category", self)
            delete_action.triggered.connect(
                lambda: self._confirm_delete_category(self.get_selected_category())
            )
            menu.addAction(delete_action)
        
        if menu.actions():
            menu.exec(self.mapToGlobal(position))

    def _confirm_delete_category(self, category: Dict[str, str]) -> None:
        """Confirm deletion of a category."""
        if not category:
            return
            
        name = category.get("name", "Unknown")
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete the category '{name}'?\n\n"
            "This action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.delete_category_requested.emit(category.get("id", "")) 