"""
Mapping Table Widget

A custom QTableWidget for displaying and managing business mappings
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


class MappingTable(QTableWidget):
    """
    Custom table widget for displaying business mappings.

    Provides a sortable, searchable table with context menus
    and selection handling for mapping management.
    """

    # Custom signals
    mapping_selected = pyqtSignal(dict)  # Emitted when a mapping is selected
    mapping_double_clicked = pyqtSignal(
        dict
    )  # Emitted when a mapping is double-clicked

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        # Table setup
        self._setup_table()
        self._setup_headers()
        self._setup_behavior()

        # Data storage
        self._mappings: List[Dict[str, Any]] = []
        self._filtered_mappings: List[Dict[str, Any]] = []

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
        self.verticalHeader().setDefaultSectionSize(30)  # type: ignore[union-attr]

    def _setup_headers(self) -> None:
        """Set up the table headers."""
        # Set header labels
        headers = [
            "Trigger Term",
            "Business Canonical Name",
            "Match Type",
            "Usage Count",
        ]
        self.setHorizontalHeaderLabels(headers)

        # Configure header behavior
        header = self.horizontalHeader()
        header.setStretchLastSection(False)  # type: ignore[union-attr]
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)  # type: ignore[union-attr]
        header.setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )  # type: ignore[union-attr]
        header.setSectionResizeMode(
            2, QHeaderView.ResizeMode.ResizeToContents
        )  # type: ignore[union-attr]
        header.setSectionResizeMode(
            3, QHeaderView.ResizeMode.ResizeToContents
        )  # type: ignore[union-attr]

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

        # Set context menu policy
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)

    def load_mappings(
        self, exact_matches: Dict[str, str], partial_matches: Dict[str, str]
    ) -> None:
        """
        Load mappings into the table.

        Args:
            exact_matches: Dictionary of exact match mappings
            partial_matches: Dictionary of partial match mappings
        """
        # Clear existing data
        self.clearContents()
        self._mappings = []

        # Process exact matches
        for mapping, official_name in exact_matches.items():
            self._mappings.append(
                {
                    "mapping": mapping,
                    "official_name": official_name,
                    "match_type": "Exact",
                    "usage_count": 0,  # TODO: Implement usage tracking
                }
            )

        # Process partial matches
        for mapping, official_name in partial_matches.items():
            self._mappings.append(
                {
                    "mapping": mapping,
                    "official_name": official_name,
                    "match_type": "Partial",
                    "usage_count": 0,  # TODO: Implement usage tracking
                }
            )

        # Update filtered list
        self._filtered_mappings = self._mappings.copy()

        # Populate table
        self._populate_table()

        # Update row count
        self.setRowCount(len(self._filtered_mappings))

    def _populate_table(self) -> None:
        """Populate the table with mapping data."""
        self.setRowCount(len(self._filtered_mappings))

        for row, mapping_data in enumerate(self._filtered_mappings):
            # Trigger Term
            trigger_item = QTableWidgetItem(mapping_data["mapping"])
            trigger_item.setData(Qt.ItemDataRole.UserRole, mapping_data)
            self.setItem(row, 0, trigger_item)

            # Business Canonical Name
            official_item = QTableWidgetItem(mapping_data["official_name"])
            self.setItem(row, 1, official_item)

            # Match Type
            match_type_item = QTableWidgetItem(mapping_data["match_type"])
            match_type_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            # Color code match types
            if mapping_data["match_type"] == "Exact":
                match_type_item.setBackground(QColor(200, 255, 200))  # Light green
            else:
                match_type_item.setBackground(QColor(255, 255, 200))  # Light yellow

            self.setItem(row, 2, match_type_item)

            # Usage Count
            usage_item = QTableWidgetItem(str(mapping_data["usage_count"]))
            usage_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.setItem(row, 3, usage_item)

    def get_selected_mapping(self) -> Optional[Dict[str, Any]]:
        """
        Get the currently selected mapping data.

        Returns:
            Dictionary containing mapping data or None if no selection
        """
        current_row = self.currentRow()
        if current_row >= 0 and current_row < len(self._filtered_mappings):
            return self._filtered_mappings[current_row]
        return None

    def search_mappings(self, search_text: str) -> None:
        """
        Search mappings and filter the table.

        Args:
            search_text: Text to search for in trigger terms and business canonical names
        """
        self._current_search = search_text.lower()

        # Reset timer to avoid too many searches while typing
        self._search_timer.stop()
        self._search_timer.start(300)  # 300ms delay

    def _perform_search(self) -> None:
        """Perform the actual search operation."""
        if not self._current_search:
            # No search text, show all mappings
            self._filtered_mappings = self._mappings.copy()
        else:
            # Filter mappings based on search text
            self._filtered_mappings = []
            for mapping_data in self._mappings:
                mapping = mapping_data["mapping"].lower()
                official = mapping_data["official_name"].lower()

                if self._current_search in mapping or self._current_search in official:
                    self._filtered_mappings.append(mapping_data)

        # Update table
        self._populate_table()

        # Update status (if we have access to status bar)
        if hasattr(self.parent(), "status_bar"):
            count = len(self._filtered_mappings)
            total = len(self._mappings)
            if self._current_search:
                self.parent().status_bar.showMessage(
                    f"Found {count} of {total} mappings"
                )  # type: ignore[union-attr]
            else:
                self.parent().status_bar.showMessage(f"{total} mappings loaded")  # type: ignore[union-attr]

    def _on_selection_changed(self) -> None:
        """Handle selection change events."""
        selected_mapping = self.get_selected_mapping()
        self.mapping_selected.emit(selected_mapping if selected_mapping else {})

    def _on_item_double_clicked(self, item: QTableWidgetItem) -> None:
        """Handle double-click events on table items."""
        selected_mapping = self.get_selected_mapping()
        if selected_mapping:
            self.mapping_double_clicked.emit(selected_mapping)

    def _show_context_menu(self, position: QPoint) -> None:
        """Show context menu for right-click actions."""
        selected_mapping = self.get_selected_mapping()
        if not selected_mapping:
            return

        context_menu = QMenu(self)

        # Edit action
        edit_action = context_menu.addAction("Edit Mapping")
        edit_action.triggered.connect(
            lambda: self.mapping_double_clicked.emit(selected_mapping)
        )  # type: ignore[union-attr]

        # Delete action
        delete_action = context_menu.addAction("Delete Mapping")
        delete_action.triggered.connect(lambda: self._delete_selected_mapping())  # type: ignore[union-attr]

        # Copy actions
        context_menu.addSeparator()
        copy_mapping_action = context_menu.addAction("Copy Mapping")
        copy_mapping_action.triggered.connect(
            lambda: self._copy_to_clipboard(selected_mapping["mapping"])
        )  # type: ignore[union-attr]

        copy_official_action = context_menu.addAction("Copy Business Canonical Name")
        copy_official_action.triggered.connect(
            lambda: self._copy_to_clipboard(selected_mapping["official_name"])
        )  # type: ignore[union-attr]

        # Show menu
        context_menu.exec(self.mapToGlobal(position))

    def _delete_selected_mapping(self) -> None:
        """Delete the currently selected mapping."""
        selected_mapping = self.get_selected_mapping()
        if not selected_mapping:
            return

        # This will be handled by the main window
        # We just emit a signal or call a method
        if hasattr(self.parent(), "_delete_mapping"):
            self.parent()._delete_mapping()  # type: ignore[union-attr]

    def _copy_to_clipboard(self, text: str) -> None:
        """Copy text to clipboard."""
        clipboard = QApplication.clipboard()  # type: ignore[union-attr]
        clipboard.setText(text)  # type: ignore[union-attr]

    def clear_search(self) -> None:
        """Clear the current search and show all mappings."""
        self.search_mappings("")

    def get_all_mappings(self) -> List[Dict[str, Any]]:
        """Get all mappings (not filtered)."""
        return self._mappings.copy()

    def get_filtered_mappings(self) -> List[Dict[str, Any]]:
        """Get currently filtered mappings."""
        return self._filtered_mappings.copy()

    def refresh_display(self) -> None:
        """Refresh the table display."""
        self._populate_table()

    def select_mapping(self, mapping: str) -> bool:
        """
        Select a mapping by its name.

        Args:
            mapping: The mapping name to select

        Returns:
            True if mapping was found and selected, False otherwise
        """
        for row, mapping_data in enumerate(self._filtered_mappings):
            if mapping_data["mapping"] == mapping:
                self.selectRow(row)
                return True
        return False
