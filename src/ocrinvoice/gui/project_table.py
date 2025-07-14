"""
Project Table Widget

A table widget for displaying and managing projects in the GUI.
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


class ProjectTable(QTableWidget):
    """
    Table widget for displaying and managing projects.

    Displays projects in a table format with columns for:
    - Project Name
    - Description
    - Created Date
    """

    # Custom signals
    project_selected = pyqtSignal(dict)  # Emitted when a project is selected
    project_double_clicked = pyqtSignal(
        dict
    )  # Emitted when a project is double-clicked
    delete_project_requested = pyqtSignal(str)  # Emitted when delete is requested

    def __init__(self, parent=None):
        super().__init__(parent)
        self.projects: List[Dict[str, str]] = []
        self._filtered_projects: List[Dict[str, str]] = []

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
        self.setHorizontalHeaderLabels(["Project Name", "Description", "Created Date"])

        # Configure header
        header = self.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)

        # Set up vertical header
        self.verticalHeader().setVisible(False)

        # Set table style
        self.setStyleSheet(
            """
            QTableWidget {
                background-color: white;
                alternate-background-color: #f8f9fa;
                gridline-color: #dee2e6;
                border: 1px solid #dee2e6;
                border-radius: 4px;
            }
            QTableWidget::item {
                padding: 8px;
                border: none;
            }
            QTableWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                padding: 8px;
                border: none;
                border-bottom: 2px solid #dee2e6;
                font-weight: bold;
                color: #495057;
            }
        """
        )

    def _setup_connections(self) -> None:
        """Set up signal connections."""
        self.itemSelectionChanged.connect(self._on_selection_changed)
        self.itemDoubleClicked.connect(self._on_item_double_clicked)
        self.customContextMenuRequested.connect(self._show_context_menu)

    def load_projects(self, projects: List[Dict[str, str]]) -> None:
        """
        Load projects into the table.

        Args:
            projects: List of project dictionaries
        """
        self.projects = projects.copy()
        self._filtered_projects = self.projects.copy()
        self._populate_table()

    def _populate_table(self) -> None:
        """Populate the table with project data."""
        self.setRowCount(len(self._filtered_projects))

        for row, project in enumerate(self._filtered_projects):
            # Project Name (not editable - use edit dialog instead)
            name_item = QTableWidgetItem(project.get("name", ""))
            name_item.setData(Qt.ItemDataRole.UserRole, project.get("id", ""))
            name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.setItem(row, 0, name_item)

            # Description (not editable - use edit dialog instead)
            desc_item = QTableWidgetItem(project.get("description", ""))
            desc_item.setFlags(desc_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.setItem(row, 1, desc_item)

            # Created Date (not editable)
            date_item = QTableWidgetItem(project.get("created_date", ""))
            date_item.setFlags(date_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.setItem(row, 2, date_item)

    def search_projects(self, search_text: str) -> None:
        """
        Search projects by name or description.

        Args:
            search_text: Text to search for
        """
        self._current_search = search_text.lower().strip()
        self._search_timer.start(300)  # Debounce search

    def _perform_search(self) -> None:
        """Perform the actual search operation."""
        if not self._current_search:
            self._filtered_projects = self.projects.copy()
        else:
            self._filtered_projects = [
                project
                for project in self.projects
                if (
                    self._current_search in project.get("name", "").lower()
                    or self._current_search in project.get("description", "").lower()
                )
            ]

        self._populate_table()
        self.setRowCount(len(self._filtered_projects))

    def clear_search(self) -> None:
        """Clear the current search and show all projects."""
        self._current_search = ""
        self._filtered_projects = self.projects.copy()
        self._populate_table()

    def get_selected_project(self) -> Optional[Dict[str, str]]:
        """
        Get the currently selected project.

        Returns:
            Selected project dictionary or None if no selection
        """
        current_row = self.currentRow()
        if current_row >= 0 and current_row < len(self._filtered_projects):
            return self._filtered_projects[current_row]
        return None

    def get_selected_project_id(self) -> Optional[str]:
        """
        Get the ID of the currently selected project.

        Returns:
            Selected project ID or None if no selection
        """
        project = self.get_selected_project()
        return project.get("id") if project else None

    def select_project(self, project_id: str) -> bool:
        """
        Select a project by ID.

        Args:
            project_id: The project ID to select

        Returns:
            True if project was found and selected, False otherwise
        """
        for row, project in enumerate(self._filtered_projects):
            if project.get("id") == project_id:
                self.selectRow(row)
                return True
        return False

    def clear_selection(self) -> None:
        """Clear the current selection."""
        self.clearSelection()

    def refresh_projects(self, projects: List[Dict[str, str]]) -> None:
        """
        Refresh the table with new project data.

        Args:
            projects: Updated list of project dictionaries
        """
        self.load_projects(projects)

    def _on_selection_changed(self) -> None:
        """Handle selection change events."""
        project = self.get_selected_project()
        if project:
            self.project_selected.emit(project)

    def _on_item_double_clicked(self, item: QTableWidgetItem) -> None:
        """Handle double-click events."""
        project = self.get_selected_project()
        if project:
            self.project_double_clicked.emit(project)

    def _show_context_menu(self, position) -> None:
        """Show context menu for right-click actions."""
        project = self.get_selected_project()
        if not project:
            return

        menu = QMenu(self)

        # Edit action
        edit_action = QAction("Edit Project", self)
        edit_action.triggered.connect(lambda: self.project_double_clicked.emit(project))
        menu.addAction(edit_action)

        menu.addSeparator()

        # Delete action
        delete_action = QAction("Delete Project", self)
        delete_action.triggered.connect(lambda: self._confirm_delete_project(project))
        menu.addAction(delete_action)

        menu.exec(self.mapToGlobal(position))

    def _confirm_delete_project(self, project: Dict[str, str]) -> None:
        """
        Show confirmation dialog for project deletion.

        Args:
            project: The project to delete
        """
        project_name = project.get("name", "Unknown")

        reply = QMessageBox.question(
            self,
            "Delete Project",
            f"Are you sure you want to delete the project '{project_name}'?\n\n"
            "This action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            project_id = project.get("id")
            if project_id:
                self.delete_project_requested.emit(project_id)
