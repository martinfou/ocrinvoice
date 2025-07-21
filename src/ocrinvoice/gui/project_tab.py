"""
Project Tab Widget

A tab widget for managing projects within the main OCR application.
Integrates the project table and form components with the project manager.
"""

from typing import Dict, Any, Optional, List
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QSplitter,
    QPushButton,
    QLineEdit,
    QLabel,
    QMessageBox,
    QDialog,
    QVBoxLayout as QVBoxLayoutDialog,
    QGroupBox,
    QStatusBar,
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread, pyqtSignal as Signal
from PyQt6.QtGui import QFont

from .project_table import ProjectTable
from .project_form import ProjectForm
from ocrinvoice.business.project_manager import ProjectManager


class ProjectManagerThread(QThread):
    """Background thread for project management operations."""

    # Signals
    projects_loaded = Signal(list)  # Emits list of projects
    project_saved = Signal(dict)  # Emits saved project data
    project_deleted = Signal(str)  # Emits deleted project ID
    error_occurred = Signal(str)  # Emits error message

    def __init__(self, project_manager: ProjectManager):
        super().__init__()
        self.project_manager = project_manager
        self._operation = None
        self._data = None

    def load_projects(self):
        """Load projects from the project manager."""
        self._operation = "load"
        self.start()

    def save_project(self, project_data: Dict[str, Any]):
        """Save a project to the project manager."""
        self._operation = "save"
        self._data = project_data
        self.start()

    def delete_project(self, project_id: str):
        """Delete a project from the project manager."""
        self._operation = "delete"
        self._data = project_id
        self.start()

    def run(self):
        """Run the background operation."""
        try:
            if self._operation == "load":
                # Reload configuration before loading projects
                self.project_manager.reload_projects()
                projects = self.project_manager.get_all_projects()
                self.projects_loaded.emit(projects)
            elif self._operation == "save":
                self._save_project_to_manager(self._data)
                self.project_saved.emit(self._data)
            elif self._operation == "delete":
                self._delete_project_from_manager(self._data)
                self.project_deleted.emit(self._data)
        except Exception as e:
            self.error_occurred.emit(str(e))

    def _save_project_to_manager(self, project_data: Dict[str, Any]):
        """Save a project to the project manager."""
        project_id = project_data.get("id")
        name = project_data.get("name", "")
        description = project_data.get("description", "")

        if project_id:
            # Update existing project
            self.project_manager.update_project(project_id, name, description)
        else:
            # Add new project
            new_id = self.project_manager.add_project(name, description)
            project_data["id"] = new_id

    def _delete_project_from_manager(self, project_id: str):
        """Delete a project from the project manager."""
        self.project_manager.delete_project(project_id)


class ProjectDialog(QDialog):
    """Dialog for adding/editing projects."""

    def __init__(self, parent=None, project_data=None):
        super().__init__(parent)
        self.setWindowTitle("Add/Edit Project")
        self.setModal(True)
        self.setMinimumSize(500, 400)

        layout = QVBoxLayoutDialog(self)

        # Create project form
        self.project_form = ProjectForm()
        layout.addWidget(self.project_form)

        # Load project data if provided (edit mode)
        if project_data:
            self.project_form.load_project(project_data)

        # Connect form signals
        self.project_form.project_saved.connect(self.accept)
        self.project_form.form_cancelled.connect(self.reject)

    def get_project_data(self):
        """Get the project data from the form."""
        return self.project_form.get_project_data()


class ProjectTab(QWidget):
    """
    Project management tab for the main OCR application.

    Provides a complete interface for managing projects with
    table view, search, add/edit functionality, and integration with
    the project manager.
    """

    # Custom signals
    project_updated = pyqtSignal()  # Emitted when projects are modified

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.project_manager = ProjectManager()
        self.project_manager_thread = ProjectManagerThread(self.project_manager)
        self._setup_ui()
        self._setup_connections()
        self._load_projects()

    def _setup_ui(self) -> None:
        """Set up the user interface components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Header section
        header_layout = QHBoxLayout()

        # Title
        title_label = QLabel("Project Manager")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(16)
        title_label.setFont(title_font)
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        # Search box
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("🔍 Search projects...")
        self.search_edit.setMaximumWidth(300)
        self.search_edit.textChanged.connect(self._on_search_changed)
        header_layout.addWidget(self.search_edit)

        layout.addLayout(header_layout)

        # Toolbar section
        toolbar_layout = QHBoxLayout()

        # Add button
        self.add_button = QPushButton("➕ Add Project")
        self.add_button.clicked.connect(self._on_add_project)
        toolbar_layout.addWidget(self.add_button)

        # Edit button
        self.edit_button = QPushButton("✏️ Edit Project")
        self.edit_button.clicked.connect(self._on_edit_project)
        self.edit_button.setEnabled(False)
        toolbar_layout.addWidget(self.edit_button)

        # Delete button
        self.delete_button = QPushButton("🗑️ Delete Project")
        self.delete_button.clicked.connect(self._on_delete_project)
        self.delete_button.setEnabled(False)
        toolbar_layout.addWidget(self.delete_button)

        toolbar_layout.addStretch()

        # Refresh button
        self.refresh_button = QPushButton("🔄 Refresh")
        self.refresh_button.clicked.connect(self._load_projects)
        toolbar_layout.addWidget(self.refresh_button)

        layout.addLayout(toolbar_layout)

        # Main content area
        content_splitter = QSplitter(Qt.Orientation.Horizontal)

        # Project table
        self.project_table = ProjectTable()
        content_splitter.addWidget(self.project_table)

        # Statistics panel
        stats_panel = self._create_stats_panel()
        content_splitter.addWidget(stats_panel)

        # Set splitter proportions
        content_splitter.setSizes([600, 200])
        layout.addWidget(content_splitter)

        # Status bar
        self.status_bar = QStatusBar()
        layout.addWidget(self.status_bar)

    def _create_stats_panel(self) -> QWidget:
        """Create the statistics panel."""
        panel = QWidget()
        panel.setMaximumWidth(250)
        layout = QVBoxLayout(panel)

        # Statistics group
        stats_group = QGroupBox("Statistics")
        stats_layout = QVBoxLayout(stats_group)

        self.total_projects_label = QLabel("Total Projects: 0")
        self.active_projects_label = QLabel("Active Projects: 0")
        self.recent_projects_label = QLabel("Recent Projects: 0")

        stats_layout.addWidget(self.total_projects_label)
        stats_layout.addWidget(self.active_projects_label)
        stats_layout.addWidget(self.recent_projects_label)

        layout.addWidget(stats_group)
        layout.addStretch()

        return panel

    def _setup_connections(self) -> None:
        """Set up signal connections."""
        # Table signals
        self.project_table.project_selected.connect(self._on_project_selected)
        self.project_table.project_double_clicked.connect(self._on_edit_project)
        self.project_table.delete_project_requested.connect(self._on_delete_project)

        # Thread signals
        self.project_manager_thread.projects_loaded.connect(self._on_projects_loaded)
        self.project_manager_thread.project_saved.connect(self._on_project_saved)
        self.project_manager_thread.project_deleted.connect(self._on_project_deleted)
        self.project_manager_thread.error_occurred.connect(self._on_error_occurred)

    def _load_projects(self) -> None:
        """Load projects from the manager."""
        self.status_bar.showMessage("Loading projects...")
        self.project_manager_thread.load_projects()

    def _on_projects_loaded(self, projects: List[Dict[str, Any]]) -> None:
        """Handle projects loaded from manager."""
        self.project_table.load_projects(projects)
        self._update_statistics(projects)
        self.status_bar.showMessage(f"Loaded {len(projects)} projects")

    def _update_statistics(self, projects: List[Dict[str, Any]]) -> None:
        """Update the statistics display."""
        total_projects = len(projects)
        self.total_projects_label.setText(f"Total Projects: {total_projects}")
        self.active_projects_label.setText(
            f"Active Projects: {total_projects}"
        )  # All projects are considered active
        self.recent_projects_label.setText(
            f"Recent Projects: {min(total_projects, 5)}"
        )  # Show up to 5 as recent

    def _on_search_changed(self, search_text: str) -> None:
        """Handle search text changes."""
        self.project_table.search_projects(search_text)

    def _on_project_selected(self, project_data: Dict[str, Any]) -> None:
        """Handle project selection."""
        self.edit_button.setEnabled(True)
        self.delete_button.setEnabled(True)

    def _on_add_project(self) -> None:
        """Handle add project button click."""
        dialog = ProjectDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            project_data = dialog.get_project_data()
            self.project_manager_thread.save_project(project_data)

    def _on_edit_project(self, project_data: Optional[Dict[str, Any]] = None) -> None:
        """Handle edit project action."""
        if not project_data:
            project_data = self.project_table.get_selected_project()

        if project_data:
            dialog = ProjectDialog(self, project_data)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                updated_data = dialog.get_project_data()
                self.project_manager_thread.save_project(updated_data)

    def _on_delete_project(self) -> None:
        """Handle delete project action."""
        project_id = self.project_table.get_selected_project_id()
        if project_id:
            self.project_manager_thread.delete_project(project_id)

    def _on_project_saved(self, project_data: Dict[str, Any]) -> None:
        """Handle project saved from manager."""
        self.status_bar.showMessage(
            f"Project '{project_data.get('name', '')}' saved successfully"
        )
        self._load_projects()
        self.project_updated.emit()

    def _on_project_deleted(self, project_id: str) -> None:
        """Handle project deleted from manager."""
        self.status_bar.showMessage("Project deleted successfully")
        self._load_projects()
        self.project_updated.emit()

    def _on_error_occurred(self, error_message: str) -> None:
        """Handle errors from manager thread."""
        QMessageBox.critical(
            self,
            "Error",
            f"An error occurred: {error_message}",
            QMessageBox.StandardButton.Ok,
        )
        self.status_bar.showMessage("Error occurred")

    def refresh_data(self) -> None:
        """Refresh the project data."""
        self._load_projects()
        # Emit signal to notify other components that projects have been updated
        self.project_updated.emit()

    def get_project_names(self) -> List[str]:
        """Get list of all project names."""
        return self.project_manager.get_project_names()

    def get_default_project(self) -> str:
        """Get the default project name."""
        return self.project_manager.get_default_project()
