"""
Category Table Widget

Table widget for displaying and managing expense categories.
"""

from typing import List, Dict, Optional
from PyQt6.QtWidgets import (
    QTableWidget, QTableWidgetItem, QHeaderView, QMenu,
    QMessageBox
)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import pyqtSignal, Qt


class CategoryTable(QTableWidget):
    """
    Table widget for displaying and managing expense categories.

    Displays categories in a table format with columns for:
    - Category Name
    - Description
    - Expense Code
    """

    # Custom signals
    category_selected = pyqtSignal(dict)  # Emitted when a category is selected
    category_double_clicked = pyqtSignal(dict)  # Emitted when a category is double-clicked
    delete_category_requested = pyqtSignal(str)  # Emitted when delete is requested

    def __init__(self, parent=None):
        """Initialize the category table."""
        super().__init__(parent)
        
        self._categories = []
        self._filtered_categories = []
        self._search_text = ""
        
        self._setup_ui()
        self._setup_connections()

    def _setup_ui(self) -> None:
        """Set up the user interface."""
        # Set up columns
        self.setColumnCount(3)
        self.setHorizontalHeaderLabels(["Category Name", "Description", "Expense Code"])
        
        # Set up table properties
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.setAlternatingRowColors(True)
        self.setSortingEnabled(True)
        
        # Set up column sizing
        header = self.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)  # Name
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Description
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Expense Code
        
        # Set up row height
        self.verticalHeader().setDefaultSectionSize(30)
        
        # Hide vertical header
        self.verticalHeader().setVisible(False)

    def _setup_connections(self) -> None:
        """Set up signal connections."""
        self.itemSelectionChanged.connect(self._on_selection_changed)
        self.itemDoubleClicked.connect(self._on_item_double_clicked)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)

    def load_categories(self, categories: List[Dict[str, str]]) -> None:
        """
        Load categories into the table.

        Args:
            categories: List of category dictionaries
        """
        self._categories = categories
        self._filtered_categories = categories.copy()
        self._populate_table()

    def _populate_table(self) -> None:
        """Populate the table with category data."""
        self.setRowCount(len(self._filtered_categories))
        
        for row, category in enumerate(self._filtered_categories):
            # Category name
            name_item = QTableWidgetItem(category.get("name", ""))
            name_item.setData(Qt.ItemDataRole.UserRole, category)
            self.setItem(row, 0, name_item)
            
            # Description
            description_item = QTableWidgetItem(category.get("description", ""))
            self.setItem(row, 1, description_item)
            
            # Expense Code
            cra_code_item = QTableWidgetItem(category.get("cra_code", ""))
            self.setItem(row, 2, cra_code_item)

    def search_categories(self, search_text: str) -> None:
        """
        Search categories by name, description, or expense code.

        Args:
            search_text: Text to search for
        """
        self._search_text = search_text.lower()
        self._perform_search()

    def _perform_search(self) -> None:
        """Perform the search and update the table."""
        if not self._search_text:
            self._filtered_categories = self._categories.copy()
        else:
            self._filtered_categories = []
            for category in self._categories:
                name = category.get("name", "").lower()
                description = category.get("description", "").lower()
                cra_code = category.get("cra_code", "").lower()
                
                if (self._search_text in name or 
                    self._search_text in description or 
                    self._search_text in cra_code):
                    self._filtered_categories.append(category)
        
        self._populate_table()

    def clear_search(self) -> None:
        """Clear the search and show all categories."""
        self._search_text = ""
        self._filtered_categories = self._categories.copy()
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
            QMessageBox.StandardButton.Yes)
        
        if reply == QMessageBox.StandardButton.Yes:
            self.delete_category_requested.emit(category.get("id", "")) 