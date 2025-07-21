"""
Official Names Tab Widget

A tab widget for managing official business names within the main OCR application.
Integrates the official names table with the business mapping manager.
"""

from typing import Optional, List
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
    QDialogButtonBox,
    QVBoxLayout as QVBoxLayoutDialog,
    QGroupBox,
    QStatusBar,
    QInputDialog,
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread, pyqtSignal as Signal
from PyQt6.QtGui import QFont

from .official_names_table import OfficialNamesTable
from ocrinvoice.business.business_mapping_manager import BusinessMappingManager


class OfficialNamesManagerThread(QThread):
    """Background thread for official names management operations."""

    # Signals
    official_names_loaded = Signal(list)  # Emits list of official names
    official_name_saved = Signal(str)  # Emits saved official name
    official_name_updated = Signal(str, str)  # Emits old and new official name
    official_name_deleted = Signal(str)  # Emits deleted official name
    error_occurred = Signal(str)  # Emits error message

    def __init__(self, mapping_manager: BusinessMappingManager):
        super().__init__()
        self.mapping_manager = mapping_manager
        self._operation = None
        self._data = None

    def load_official_names(self):
        """Load official names from the mapping manager."""
        self._operation = "load"
        self.start()

    def add_official_name(self, name: str):
        """Add an official name to the mapping manager."""
        self._operation = "add"
        self._data = name
        self.start()

    def update_official_name(self, old_name: str, new_name: str):
        """Update an official name in the mapping manager."""
        self._operation = "update"
        self._data = (old_name, new_name)
        self.start()

    def delete_official_name(self, name: str):
        """Delete an official name from the mapping manager."""
        self._operation = "delete"
        self._data = name
        self.start()

    def run(self):
        """Run the background operation."""
        try:
            if self._operation == "load":
                # Reload configuration before loading official names
                self.mapping_manager.reload_config()
                official_names = self.mapping_manager.get_official_names()
                self.official_names_loaded.emit(official_names)
            elif self._operation == "add":
                success = self.mapping_manager.add_official_name(self._data)
                if success:
                    self.official_name_saved.emit(self._data)
                else:
                    self.error_occurred.emit(
                        f"Official name '{self._data}' already exists"
                    )
            elif self._operation == "update":
                old_name, new_name = self._data
                success = self.mapping_manager.update_official_name(old_name, new_name)
                if success:
                    self.official_name_updated.emit(old_name, new_name)
                else:
                    self.error_occurred.emit(
                        f"Failed to update official name '{old_name}' to '{new_name}'"
                    )
            elif self._operation == "delete":
                success = self.mapping_manager.remove_official_name(self._data)
                if success:
                    self.official_name_deleted.emit(self._data)
                else:
                    self.error_occurred.emit(
                        f"Failed to delete official name '{self._data}'"
                    )
        except Exception as e:
            self.error_occurred.emit(str(e))


class AddOfficialNameDialog(QDialog):
    """Dialog for adding new official names."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Official Business Name")
        self.setModal(True)
        self.setMinimumSize(400, 150)

        layout = QVBoxLayoutDialog(self)

        # Title
        title_label = QLabel("Add New Official Business Name")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(12)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        # Description
        desc_label = QLabel(
            "Official business names are the canonical names that all aliases resolve to. "
            "They represent the standardized names for businesses."
        )
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #666; margin: 10px 0;")
        layout.addWidget(desc_label)

        # Input field
        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel("Official Name:"))
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Enter official business name")
        input_layout.addWidget(self.name_edit)
        layout.addLayout(input_layout)

        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        # Connect validation
        self.name_edit.textChanged.connect(self._validate_input)
        button_box.button(QDialogButtonBox.StandardButton.Ok).setEnabled(False)

    def _validate_input(self):
        """Validate the input and enable/disable OK button."""
        name = self.name_edit.text().strip()
        is_valid = len(name) >= 2
        button = self.findChild(QDialogButtonBox).button(
            QDialogButtonBox.StandardButton.Ok
        )
        button.setEnabled(is_valid)

    def get_official_name(self):
        """Get the entered official name."""
        return self.name_edit.text().strip()


class OfficialNamesTab(QWidget):
    """
    Official Names management tab for the main OCR application.

    Provides a complete interface for managing official business names with
    table view, search, add/edit functionality, and integration with
    the business mapping manager.
    """

    # Custom signals
    official_names_updated = pyqtSignal()  # Emitted when official names are modified

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        # Initialize business mapping manager
        self.mapping_manager = BusinessMappingManager()

        # Background thread for operations
        self.official_names_thread = OfficialNamesManagerThread(self.mapping_manager)

        # Set up the UI
        self._setup_ui()
        self._setup_connections()

        # Load initial data
        self._load_official_names()

    def _setup_ui(self) -> None:
        """Set up the user interface components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Header section
        header_layout = QHBoxLayout()

        # Title
        title_label = QLabel("Official Business Names Manager")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(16)
        title_label.setFont(title_font)
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        # Search box
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("🔍 Search official names...")
        self.search_edit.setMaximumWidth(300)
        self.search_edit.textChanged.connect(self._on_search_changed)
        header_layout.addWidget(self.search_edit)

        layout.addLayout(header_layout)

        # Toolbar section
        toolbar_layout = QHBoxLayout()

        # Add button
        self.add_button = QPushButton("➕ Add Official Name")
        self.add_button.clicked.connect(self._on_add_official_name)
        toolbar_layout.addWidget(self.add_button)

        # Edit button
        self.edit_button = QPushButton("✏️ Edit Name")
        self.edit_button.clicked.connect(self._on_edit_official_name)
        self.edit_button.setEnabled(False)
        toolbar_layout.addWidget(self.edit_button)

        # Delete button
        self.delete_button = QPushButton("🗑️ Delete Name")
        self.delete_button.clicked.connect(self._on_delete_official_name)
        self.delete_button.setEnabled(False)
        toolbar_layout.addWidget(self.delete_button)

        toolbar_layout.addStretch()

        # Refresh button
        self.refresh_button = QPushButton("🔄 Refresh")
        self.refresh_button.clicked.connect(self._load_official_names)
        toolbar_layout.addWidget(self.refresh_button)

        layout.addLayout(toolbar_layout)

        # Main content area
        content_splitter = QSplitter(Qt.Orientation.Horizontal)

        # Official names table
        self.official_names_table = OfficialNamesTable()
        content_splitter.addWidget(self.official_names_table)

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

        self.total_names_label = QLabel("Total Official Names: 0")
        self.used_names_label = QLabel("Names with Aliases: 0")
        self.unused_names_label = QLabel("Unused Names: 0")

        stats_layout.addWidget(self.total_names_label)
        stats_layout.addWidget(self.used_names_label)
        stats_layout.addWidget(self.unused_names_label)

        layout.addWidget(stats_group)

        # Information group
        info_group = QGroupBox("Information")
        info_layout = QVBoxLayout(info_group)

        info_text = QLabel(
            "Official names are the canonical business names that all aliases resolve to. "
            "They represent the standardized names for businesses in your system."
        )
        info_text.setWordWrap(True)
        info_layout.addWidget(info_text)

        layout.addWidget(info_group)
        layout.addStretch()

        return panel

    def _setup_connections(self) -> None:
        """Set up signal connections."""
        # Table connections
        self.official_names_table.official_name_selected.connect(
            self._on_official_name_selected
        )
        self.official_names_table.official_name_double_clicked.connect(
            self._on_edit_official_name
        )
        self.official_names_table.official_name_updated.connect(
            self._on_official_name_updated
        )
        self.official_names_table.official_name_deleted.connect(
            self._on_official_name_deleted
        )

        # Thread connections
        self.official_names_thread.official_names_loaded.connect(
            self._on_official_names_loaded
        )
        self.official_names_thread.official_name_saved.connect(
            self._on_official_name_saved
        )
        self.official_names_thread.official_name_updated.connect(
            self._on_official_name_updated
        )
        self.official_names_thread.official_name_deleted.connect(
            self._on_official_name_deleted
        )
        self.official_names_thread.error_occurred.connect(self._on_error_occurred)

    def _load_official_names(self) -> None:
        """Load official names from the business mapping manager."""
        self.status_bar.showMessage("Loading official names...")
        self.official_names_thread.load_official_names()

    def _on_official_names_loaded(self, official_names: List[str]) -> None:
        """Handle official names loaded from the manager."""
        self.official_names_table.load_official_names(official_names)
        self._update_statistics(official_names)
        self.status_bar.showMessage(f"Loaded {len(official_names)} official names")

    def _update_statistics(self, official_names: List[str]) -> None:
        """Update the statistics panel."""
        total = len(official_names)

        # Count names that have aliases
        used_names = 0
        exact_matches = self.mapping_manager.config.get("exact_matches", {})
        partial_matches = self.mapping_manager.config.get("partial_matches", {})
        fuzzy_candidates = self.mapping_manager.config.get("fuzzy_candidates", [])

        for name in official_names:
            if (
                name in exact_matches.values()
                or name in partial_matches.values()
                or name in fuzzy_candidates
            ):
                used_names += 1

        unused_names = total - used_names

        self.total_names_label.setText(f"Total Official Names: {total}")
        self.used_names_label.setText(f"Names with Aliases: {used_names}")
        self.unused_names_label.setText(f"Unused Names: {unused_names}")

    def _on_search_changed(self, search_text: str) -> None:
        """Handle search text changes."""
        self.official_names_table.search_official_names(search_text)

    def _on_official_name_selected(self, official_name: str) -> None:
        """Handle official name selection."""
        self.edit_button.setEnabled(True)
        self.delete_button.setEnabled(True)

    def _on_add_official_name(self) -> None:
        """Handle add official name button click."""
        dialog = AddOfficialNameDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            official_name = dialog.get_official_name()
            self.official_names_thread.add_official_name(official_name)

    def _on_edit_official_name(self, official_name: Optional[str] = None) -> None:
        """Handle edit official name button click."""
        if official_name is None:
            official_name = self.official_names_table.get_selected_official_name()
            if not official_name:
                return

        new_name, ok = QInputDialog.getText(
            self, "Edit Official Name", "Enter new official name:", text=official_name
        )

        if ok and new_name.strip() and new_name.strip() != official_name:
            new_name = new_name.strip()
            self.official_names_thread.update_official_name(official_name, new_name)

    def _on_delete_official_name(self) -> None:
        """Handle delete official name button click."""
        official_name = self.official_names_table.get_selected_official_name()
        if not official_name:
            return

        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete the official name '{official_name}'?\n\n"
            "This will also remove all aliases that reference this name.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        , QMessageBox.StandardButton.Yes)

        if reply == QMessageBox.StandardButton.Yes:
            self.official_names_thread.delete_official_name(official_name)

    def _on_official_name_saved(self, official_name: str) -> None:
        """Handle official name saved."""
        self.status_bar.showMessage(f"Official name saved: {official_name}")
        self.official_names_updated.emit()

        # Add a small delay to ensure file is saved before reloading
        from PyQt6.QtCore import QTimer

        QTimer.singleShot(100, self._load_official_names)

    def _on_official_name_updated(self, old_name: str, new_name: str) -> None:
        """Handle official name updated."""
        self.status_bar.showMessage(f"Official name updated: {old_name} → {new_name}")
        self.official_names_updated.emit()

        # Add a small delay to ensure file is saved before reloading
        from PyQt6.QtCore import QTimer

        QTimer.singleShot(100, self._load_official_names)

    def _on_official_name_deleted(self, official_name: str) -> None:
        """Handle official name deleted."""
        self.status_bar.showMessage(f"Official name deleted: {official_name}")
        self.official_names_updated.emit()

        # Clear the table selection before reloading
        self.official_names_table.clearSelection()
        self.edit_button.setEnabled(False)
        self.delete_button.setEnabled(False)

        # Add a small delay to ensure file is saved before reloading
        from PyQt6.QtCore import QTimer

        QTimer.singleShot(100, self._load_official_names)

    def _on_error_occurred(self, error_message: str) -> None:
        """Handle error from background thread."""
        QMessageBox.critical(self, "Error", f"An error occurred: {error_message}")
        self.status_bar.showMessage("Error occurred")

    def refresh_data(self) -> None:
        """Refresh the official names data."""
        self._load_official_names()
