"""
Project Form Widget

A form widget for adding and editing projects in the GUI.
"""

from typing import Dict, Optional
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QTextEdit,
    QPushButton,
    QGroupBox,
    QMessageBox,
)
from PyQt6.QtCore import pyqtSignal


class ProjectForm(QWidget):
    """
    Form widget for adding and editing projects.

    Provides input fields for:
    - Project Name
    - Description
    """

    # Custom signals
    project_saved = pyqtSignal(dict)  # Emitted when project is saved
    form_cancelled = pyqtSignal()  # Emitted when form is cancelled

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_project_id: Optional[str] = None
        self._setup_ui()
        self._setup_connections()

    def _setup_ui(self) -> None:
        """Set up the form UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        # Project Details Group
        details_group = QGroupBox("Project Details")
        details_layout = QVBoxLayout(details_group)

        # Project Name
        name_layout = QVBoxLayout()
        name_label = QLabel("Project Name:")
        name_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText(
            "Enter project name (e.g., Kitchen Renovation)"
        )
        self.name_edit.setStyleSheet(
            """
            QLineEdit {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 4px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
        """
        )
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_edit)
        details_layout.addLayout(name_layout)

        # Description
        desc_layout = QVBoxLayout()
        desc_label = QLabel("Description:")
        desc_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
        self.desc_edit = QTextEdit()
        self.desc_edit.setPlaceholderText("Enter project description (optional)")
        self.desc_edit.setMaximumHeight(100)
        self.desc_edit.setStyleSheet(
            """
            QTextEdit {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 4px;
                font-size: 14px;
            }
            QTextEdit:focus {
                border-color: #3498db;
            }
        """
        )
        desc_layout.addWidget(desc_label)
        desc_layout.addWidget(self.desc_edit)
        details_layout.addLayout(desc_layout)

        layout.addWidget(details_group)

        # Help text
        help_text = QLabel(
            "💡 Tip: Project names with multiple words will be automatically "
            "converted to use hyphens (e.g., 'Kitchen Renovation' becomes 'kitchen-renovation')"
        )
        help_text.setStyleSheet(
            """
            color: #7f8c8d;
            font-style: italic;
            padding: 8px;
            background-color: #ecf0f1;
            border-radius: 4px;
            border-left: 4px solid #3498db;
        """
        )
        help_text.setWordWrap(True)
        layout.addWidget(help_text)

        # Action Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """
        )

        self.save_btn = QPushButton("Save Project")
        self.save_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
                color: #7f8c8d;
            }
        """
        )

        button_layout.addWidget(self.cancel_btn)
        button_layout.addWidget(self.save_btn)
        layout.addLayout(button_layout)

    def _setup_connections(self) -> None:
        """Set up signal connections."""
        self.save_btn.clicked.connect(self._save_project)
        self.cancel_btn.clicked.connect(self._cancel_form)
        self.name_edit.textChanged.connect(self._validate_form)
        self.name_edit.returnPressed.connect(self._save_project)

    def load_project(self, project_data: Dict[str, str]) -> None:
        """
        Load project data into the form for editing.

        Args:
            project_data: Project dictionary with id, name, description
        """
        self.current_project_id = project_data.get("id")
        self.name_edit.setText(project_data.get("name", ""))
        self.desc_edit.setPlainText(project_data.get("description", ""))
        self._validate_form()

    def clear_form(self) -> None:
        """Clear the form for adding a new project."""
        self.current_project_id = None
        self.name_edit.clear()
        self.desc_edit.clear()
        self._validate_form()

    def get_project_data(self) -> Dict[str, str]:
        """
        Get the current project data from the form.

        Returns:
            Dictionary with project data
        """
        return {
            "id": self.current_project_id,
            "name": self.name_edit.text().strip(),
            "description": self.desc_edit.toPlainText().strip(),
        }

    def _validate_form(self) -> bool:
        """
        Validate the form data.

        Returns:
            True if form is valid, False otherwise
        """
        name = self.name_edit.text().strip()
        is_valid = bool(name)

        self.save_btn.setEnabled(is_valid)

        # Update save button text based on mode
        if self.current_project_id:
            self.save_btn.setText("Update Project")
        else:
            self.save_btn.setText("Save Project")

        return is_valid

    def _save_project(self) -> None:
        """Save the project data."""
        if not self._validate_form():
            return

        project_data = self.get_project_data()

        # Validate project name
        name = project_data["name"]
        if not name:
            QMessageBox.warning(
                self,
                "Validation Error",
                "Project name cannot be empty.",
                QMessageBox.StandardButton.Ok,
            )
            self.name_edit.setFocus()
            return

        # Emit save signal
        self.project_saved.emit(project_data)

    def _cancel_form(self) -> None:
        """Cancel the form operation."""
        self.form_cancelled.emit()

    def set_focus(self) -> None:
        """Set focus to the name field."""
        self.name_edit.setFocus()
        self.name_edit.selectAll()
