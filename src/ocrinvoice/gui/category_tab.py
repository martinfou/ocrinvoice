"""
Category Tab Widget

A tab widget for managing CRA expense categories within the main OCR application.
Integrates the category table and form components with the category manager.
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

from .category_table import CategoryTable
from .category_form import CategoryForm
from ocrinvoice.business.category_manager import CategoryManager


class CategoryManagerThread(QThread):
    """Background thread for category management operations."""

    # Signals
    categories_loaded = Signal(list)  # Emits list of categories
    category_saved = Signal(dict)  # Emits saved category data
    category_deleted = Signal(str)  # Emits deleted category ID
    error_occurred = Signal(str)  # Emits error message

    def __init__(self, category_manager: CategoryManager):
        super().__init__()
        self.category_manager = category_manager
        self._operation = None
        self._data = None

    def load_categories(self):
        """Load categories from the category manager."""
        self._operation = "load"
        self.start()

    def save_category(self, category_data: Dict[str, Any]):
        """Save a category to the category manager."""
        self._operation = "save"
        self._data = category_data
        self.start()

    def delete_category(self, category_id: str):
        """Delete a category from the category manager."""
        self._operation = "delete"
        self._data = category_id
        self.start()

    def run(self):
        """Run the background operation."""
        try:
            if self._operation == "load":
                # Reload configuration before loading categories
                self.category_manager.reload_categories()
                categories = self.category_manager.get_categories()
                self.categories_loaded.emit(categories)
            elif self._operation == "save":
                self._save_category_to_manager(self._data)
                self.category_saved.emit(self._data)
            elif self._operation == "delete":
                self._delete_category_from_manager(self._data)
                self.category_deleted.emit(self._data)
        except Exception as e:
            self.error_occurred.emit(str(e))

    def _save_category_to_manager(self, category_data: Dict[str, Any]):
        """Save a category to the category manager."""
        category_id = category_data.get("id")
        name = category_data.get("name", "")
        description = category_data.get("description", "")
        cra_code = category_data.get("cra_code", "")

        if category_id:
            # Update existing category
            success = self.category_manager.update_category(category_id, name, description, cra_code)
            if not success:
                raise ValueError(f"Category with ID {category_id} not found")
        else:
            # Add new category
            new_id = self.category_manager.add_category(name, description, cra_code)
            category_data["id"] = new_id

    def _delete_category_from_manager(self, category_id: str):
        """Delete a category from the category manager."""
        success = self.category_manager.delete_category(category_id)
        if not success:
            raise ValueError(f"Category with ID {category_id} not found")


class CategoryDialog(QDialog):
    """Dialog for adding/editing categories."""

    def __init__(self, parent=None, category_data=None):
        super().__init__(parent)
        self.setWindowTitle("Add/Edit Category")
        self.setModal(True)
        self.setMinimumSize(500, 400)

        layout = QVBoxLayoutDialog(self)

        # Create category form
        self.category_form = CategoryForm()
        layout.addWidget(self.category_form)

        # Load category data if provided (edit mode)
        if category_data:
            self.category_form.load_category(category_data)

        # Connect form signals
        self.category_form.category_saved.connect(self.accept)
        self.category_form.form_cancelled.connect(self.reject)

    def get_category_data(self):
        """Get the category data from the form."""
        return self.category_form.get_category_data()


class CategoryTab(QWidget):
    """
    Category management tab for the main OCR application.

    Provides a complete interface for managing CRA expense categories with
    table view, search, add/edit functionality, and integration with
    the category manager.
    """

    # Custom signals
    category_updated = pyqtSignal()  # Emitted when categories are modified

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.category_manager = CategoryManager()
        self.category_manager_thread = CategoryManagerThread(self.category_manager)
        self._setup_ui()
        self._setup_connections()
        self._load_categories()

    def _setup_ui(self) -> None:
        """Set up the user interface components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Header section
        header_layout = QHBoxLayout()

        # Title
        title_label = QLabel("Category Manager")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(16)
        title_label.setFont(title_font)
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        # Search box
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("🔍 Search categories...")
        self.search_edit.setMaximumWidth(300)
        self.search_edit.textChanged.connect(self._on_search_changed)
        header_layout.addWidget(self.search_edit)

        layout.addLayout(header_layout)

        # Toolbar section
        toolbar_layout = QHBoxLayout()

        # Add button
        self.add_button = QPushButton("➕ Add Category")
        self.add_button.clicked.connect(self._on_add_category)
        toolbar_layout.addWidget(self.add_button)

        # Edit button
        self.edit_button = QPushButton("✏️ Edit Category")
        self.edit_button.clicked.connect(self._on_edit_category)
        self.edit_button.setEnabled(False)
        toolbar_layout.addWidget(self.edit_button)

        # Delete button
        self.delete_button = QPushButton("🗑️ Delete Category")
        self.delete_button.clicked.connect(self._on_delete_category)
        self.delete_button.setEnabled(False)
        toolbar_layout.addWidget(self.delete_button)

        toolbar_layout.addStretch()

        # Refresh button
        self.refresh_button = QPushButton("🔄 Refresh")
        self.refresh_button.clicked.connect(self._load_categories)
        toolbar_layout.addWidget(self.refresh_button)

        # Backup button
        self.backup_button = QPushButton("💾 Backup")
        self.backup_button.clicked.connect(self._on_backup_categories)
        toolbar_layout.addWidget(self.backup_button)

        layout.addLayout(toolbar_layout)

        # Main content area
        content_splitter = QSplitter(Qt.Orientation.Horizontal)

        # Category table
        self.category_table = CategoryTable()
        content_splitter.addWidget(self.category_table)

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

        self.total_categories_label = QLabel("Total Categories: 0")
        self.cra_codes_label = QLabel("CRA Codes: 0")
        self.recent_categories_label = QLabel("Recent Categories: 0")

        stats_layout.addWidget(self.total_categories_label)
        stats_layout.addWidget(self.cra_codes_label)
        stats_layout.addWidget(self.recent_categories_label)

        layout.addWidget(stats_group)
        layout.addStretch()

        return panel

    def _setup_connections(self) -> None:
        """Set up signal connections."""
        # Table signals
        self.category_table.category_selected.connect(self._on_category_selected)
        self.category_table.category_double_clicked.connect(self._on_edit_category)
        self.category_table.delete_category_requested.connect(
            self._on_delete_category_requested
        )

        # Thread signals
        self.category_manager_thread.categories_loaded.connect(self._on_categories_loaded)
        self.category_manager_thread.category_saved.connect(self._on_category_saved)
        self.category_manager_thread.category_deleted.connect(self._on_category_deleted)
        self.category_manager_thread.error_occurred.connect(self._on_error_occurred)

    def _load_categories(self) -> None:
        """Load categories from the category manager."""
        self.status_bar.showMessage("Loading categories...")
        self.category_manager_thread.load_categories()

    def _on_categories_loaded(self, categories: List[Dict[str, Any]]) -> None:
        """Handle categories loaded from the manager."""
        self.category_table.load_categories(categories)
        self._update_statistics(categories)
        self.status_bar.showMessage(f"Loaded {len(categories)} categories")

    def _update_statistics(self, categories: List[Dict[str, Any]]) -> None:
        """Update the statistics panel."""
        total = len(categories)
        cra_codes = len(set(cat.get("cra_code", "") for cat in categories))
        recent = len([cat for cat in categories if cat.get("created_date", "")])

        self.total_categories_label.setText(f"Total Categories: {total}")
        self.cra_codes_label.setText(f"CRA Codes: {cra_codes}")
        self.recent_categories_label.setText(f"Recent Categories: {recent}")

    def _on_search_changed(self, search_text: str) -> None:
        """Handle search text changes."""
        self.category_table.search_categories(search_text)

    def _on_category_selected(self, category_data: Dict[str, Any]) -> None:
        """Handle category selection."""
        self.edit_button.setEnabled(True)
        self.delete_button.setEnabled(True)

    def _on_add_category(self) -> None:
        """Handle add category button click."""
        dialog = CategoryDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            category_data = dialog.get_category_data()
            self.category_manager_thread.save_category(category_data)

    def _on_edit_category(self, category_data: Optional[Dict[str, Any]] = None) -> None:
        """Handle edit category button click."""
        if category_data is None:
            category_data = self.category_table.get_selected_category()
            if not category_data:
                return
        dialog = CategoryDialog(self, category_data)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            category_data = dialog.get_category_data()
            self.category_manager_thread.save_category(category_data)

    def _on_delete_category(self) -> None:
        """Handle delete category button click."""
        category_data = self.category_table.get_selected_category()
        if not category_data:
            QMessageBox.warning(self, "No Selection", "Please select a category to delete.")
            return

        category_id = category_data["id"]
        name = category_data["name"]
        
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete the category '{name}'?\n\n"
            f"CRA Code: {category_data.get('cra_code', 'N/A')}\n"
            "This action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.category_manager_thread.delete_category(category_id)

    def _on_delete_category_requested(self, category_id: str) -> None:
        """Handle delete category request from table context menu."""
        category_data = self.category_manager.get_category(category_id)
        if category_data:
            name = category_data["name"]
            reply = QMessageBox.question(
                self,
                "Confirm Delete",
                f"Are you sure you want to delete the category '{name}'?\n\n"
                f"CRA Code: {category_data.get('cra_code', 'N/A')}\n"
                "This action cannot be undone.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )

            if reply == QMessageBox.StandardButton.Yes:
                self.category_manager_thread.delete_category(category_id)

    def _on_category_saved(self, category_data: Dict[str, Any]) -> None:
        """Handle category saved."""
        self.status_bar.showMessage(f"Category saved: {category_data['name']}")
        self.category_updated.emit()

        # Add a small delay to ensure file is saved before reloading
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(100, self._load_categories)

    def _on_category_deleted(self, category_id: str) -> None:
        """Handle category deleted."""
        self.status_bar.showMessage("Category deleted")
        self.category_updated.emit()

        # Clear the table selection and disable buttons
        self.category_table.clearSelection()
        self.edit_button.setEnabled(False)
        self.delete_button.setEnabled(False)

        # Clear any active search to ensure we see all data
        self.search_edit.clear()

        # Add a small delay to ensure file is saved before reloading
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(100, self._load_categories)

    def _on_error_occurred(self, error_message: str) -> None:
        """Handle error from background thread."""
        QMessageBox.critical(self, "Error", f"An error occurred: {error_message}")
        self.status_bar.showMessage("Error occurred")

    def _on_backup_categories(self) -> None:
        """Handle backup button click."""
        try:
            backup_file = self.category_manager.backup_categories()
            if backup_file:
                QMessageBox.information(
                    self,
                    "Backup Created",
                    f"Categories backed up successfully to:\n{backup_file}",
                    QMessageBox.StandardButton.Ok,
                )
                self.status_bar.showMessage("Backup created successfully")
            else:
                QMessageBox.warning(
                    self,
                    "Backup Failed",
                    "Failed to create backup.",
                    QMessageBox.StandardButton.Ok,
                )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Backup Error",
                f"Error creating backup: {str(e)}",
                QMessageBox.StandardButton.Ok,
            )

    def refresh_data(self) -> None:
        """Refresh the category data."""
        self._load_categories()

    def get_category_names(self) -> List[str]:
        """Get list of category names."""
        return self.category_manager.get_category_names()

    def get_category_codes(self) -> List[str]:
        """Get list of CRA codes."""
        return self.category_manager.get_category_codes()

    def get_default_category(self) -> str:
        """Get the default category name."""
        categories = self.category_manager.get_categories()
        if categories:
            return categories[0].get("name", "")
        return "" 