"""
Business Alias Tab Widget

A tab widget for managing business aliases within the main OCR application.
Integrates the alias table and form components with the business mapping manager.
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

from .alias_table import AliasTable
from .alias_form import AliasForm
from ocrinvoice.business.business_mapping_manager_v2 import BusinessMappingManagerV2 as BusinessMappingManager


class AliasManagerThread(QThread):
    """Background thread for alias management operations."""

    # Signals
    aliases_loaded = Signal(list)  # Emits list of aliases
    alias_saved = Signal(dict)  # Emits saved alias data
    alias_deleted = Signal(str)  # Emits deleted company name
    error_occurred = Signal(str)  # Emits error message

    def __init__(self, mapping_manager: BusinessMappingManager):
        super().__init__()
        self.mapping_manager = mapping_manager
        self._operation = None
        self._data = None

    def load_aliases(self):
        """Load aliases from the mapping manager."""
        self._operation = "load"
        self.start()

    def save_alias(self, alias_data: Dict[str, Any]):
        """Save an alias to the mapping manager."""
        self._operation = "save"
        self._data = alias_data
        self.start()

    def delete_alias(self, company_name: str):
        """Delete an alias from the mapping manager."""
        self._operation = "delete"
        self._data = company_name
        self.start()

    def run(self):
        """Run the background operation."""
        try:
            if self._operation == "load":
                # For v2, we don't need to reload config - just load aliases
                aliases = self._load_aliases_from_manager()
                self.aliases_loaded.emit(aliases)
            elif self._operation == "save":
                self._save_alias_to_manager(self._data)
                self.alias_saved.emit(self._data)
            elif self._operation == "delete":
                self._delete_alias_from_manager(self._data)
                self.alias_deleted.emit(self._data)
        except Exception as e:
            self.error_occurred.emit(str(e))

    def _load_aliases_from_manager(self) -> List[Dict[str, Any]]:
        """Load aliases from the business mapping manager."""
        aliases = []

        # Get all businesses from the new structure
        businesses = self.mapping_manager.get_all_businesses()
        
        for business in businesses:
            # Handle both old and new field names for backward compatibility
            business_name = business.get("business_name") or business.get("canonical_name", "")
            keywords = business.get("keywords") or business.get("aliases", [])
            
            for keyword in keywords:
                alias_data = {
                    "company_name": keyword["keyword"],
                    "canonical_name": business_name,  # Keep canonical_name for table compatibility
                    "match_type": keyword["match_type"].title(),  # Convert to title case
                    "usage_count": 0,  # TODO: Implement usage tracking
                    "last_used": "",
                    "fuzzy_matching": keyword.get("fuzzy_matching", True),
                    "case_sensitive": keyword.get("case_sensitive", False),
                    "business_id": business["id"],  # Add business ID for reference
                }
                aliases.append(alias_data)

        return aliases

    def _save_alias_to_manager(self, alias_data: Dict[str, Any]):
        """Save a keyword to the business mapping manager."""
        company_name = alias_data["company_name"]
        canonical_name = alias_data["canonical_name"]
        match_type = alias_data["match_type"].lower()  # Convert to lowercase for new structure

        # First, ensure the business name exists
        if canonical_name not in self.mapping_manager.canonical_names:
            self.mapping_manager.add_canonical_name(canonical_name)

        # Find the business by business name
        business = self.mapping_manager.get_business_by_name(canonical_name)
        if business:
            # Add the keyword to the business
            self.mapping_manager.add_keyword(business["id"], company_name, match_type)  # Changed from add_alias
        else:
            # This shouldn't happen since we just added the business name
            print(f"Warning: Could not find business for business name: {canonical_name}")

    def _delete_alias_from_manager(self, company_name: str):
        """Delete a keyword from the business mapping manager."""
        # Find the business that contains this keyword
        for business in self.mapping_manager.get_all_businesses():
            # Handle both old and new field names for backward compatibility
            keywords = business.get("keywords") or business.get("aliases", [])
            business_name = business.get("business_name") or business.get("canonical_name", "")
            
            for keyword in keywords:
                if keyword["keyword"] == company_name:
                    # Remove the keyword from the business
                    self.mapping_manager.remove_keyword(business["id"], company_name, keyword["match_type"])
                    
                    # Check if this was the last keyword for the business
                    remaining_keywords = self.mapping_manager.get_business_keywords(business["id"])
                    if not remaining_keywords:
                        # Remove the business if it has no more keywords
                        self.mapping_manager.remove_canonical_name(business_name)
                    
                    return
        
        # If we get here, the keyword wasn't found
        print(f"Warning: Could not find keyword to delete: {company_name}")


class NewBusinessDialog(QDialog):
    """Dialog for creating a new business."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🏢 Create New Business")
        self.setModal(True)
        self.setMinimumSize(400, 200)

        layout = QVBoxLayoutDialog(self)

        # Business name input
        name_layout = QHBoxLayout()
        name_label = QLabel("Business Name:")
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Enter the business name...")
        self.name_edit.textChanged.connect(self._on_name_changed)
        self.name_edit.returnPressed.connect(self._on_return_pressed)  # Handle Enter key
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_edit)
        layout.addLayout(name_layout)

        # Description
        desc_label = QLabel(
            "This will create a new business with:\n"
            "• Keyword = Business Name\n"
            "• Match Type = Exact"
        )
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)
        
        self.save_btn = QPushButton("Create Business")
        self.save_btn.setEnabled(False)
        self.save_btn.clicked.connect(self.accept)
        self.save_btn.setDefault(True)  # Make this the default button (activated by Enter)
        button_layout.addWidget(self.save_btn)
        
        layout.addLayout(button_layout)

    def _on_name_changed(self, text: str) -> None:
        """Handle business name text changes."""
        self.save_btn.setEnabled(bool(text.strip()))

    def _on_return_pressed(self) -> None:
        """Handle Enter key press in the business name field."""
        if self.save_btn.isEnabled():
            self.accept()  # Accept the dialog (same as clicking Create Business)

    def get_business_name(self) -> str:
        """Get the entered business name."""
        return self.name_edit.text().strip()


class AliasDialog(QDialog):
    """Dialog for adding/editing aliases."""

    def __init__(self, parent=None, alias_data=None, official_names=None):
        super().__init__(parent)
        self.setWindowTitle("Add/Edit Business Alias")
        self.setModal(True)
        self.setMinimumSize(500, 400)

        layout = QVBoxLayoutDialog(self)

        # Create alias form
        self.alias_form = AliasForm()
        layout.addWidget(self.alias_form)

        # Load alias data if provided (edit mode)
        if alias_data:
            self.alias_form.load_alias(alias_data)

        # Pass official names to the form
        if official_names:
            self.alias_form.set_official_names(official_names)

        # Connect signals
        self.alias_form.alias_saved.connect(self.accept)
        self.alias_form.alias_cancelled.connect(self.reject)

    def get_alias_data(self):
        """Get the alias data from the form."""
        return self.alias_form._get_form_data()


class BusinessAliasTab(QWidget):
    """
    Business Alias management tab for the main OCR application.

    Provides a complete interface for managing business aliases with
    table view, search, add/edit functionality, and integration with
    the business mapping manager.
    """

    # Custom signals
    alias_updated = pyqtSignal()  # Emitted when aliases are modified

    def __init__(self, parent: Optional[QWidget] = None, mapping_manager: Optional[BusinessMappingManager] = None) -> None:
        super().__init__(parent)

        # Use shared business mapping manager if provided, otherwise create new instance
        self.mapping_manager = mapping_manager or BusinessMappingManager()

        # Background thread for operations
        self.alias_thread = AliasManagerThread(self.mapping_manager)

        # Set up the UI
        self._setup_ui()
        self._setup_connections()

        # Load initial data
        self._load_aliases()

    def _setup_ui(self) -> None:
        """Set up the user interface components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Header section
        header_layout = QHBoxLayout()

        # Title
        title_label = QLabel("Business Manager")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(16)
        title_label.setFont(title_font)
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        # Search box
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("🔍 Search aliases...")
        self.search_edit.setMaximumWidth(300)
        self.search_edit.textChanged.connect(self._on_search_changed)
        header_layout.addWidget(self.search_edit)

        layout.addLayout(header_layout)

        # Toolbar section
        toolbar_layout = QHBoxLayout()

        # Add new business button
        self.add_business_button = QPushButton("🏢 New Business")
        self.add_business_button.setToolTip("Create a new business with exact match")
        self.add_business_button.clicked.connect(self._on_add_new_business)
        toolbar_layout.addWidget(self.add_business_button)

        # Add keyword button
        self.add_button = QPushButton("➕ Add Keyword")
        self.add_button.setToolTip("Add a keyword for an existing business")
        self.add_button.clicked.connect(self._on_add_alias)
        toolbar_layout.addWidget(self.add_button)

        # Edit button
        self.edit_button = QPushButton("✏️ Edit Keyword")
        self.edit_button.clicked.connect(self._on_edit_alias)
        self.edit_button.setEnabled(False)
        toolbar_layout.addWidget(self.edit_button)

        # Delete button
        self.delete_button = QPushButton("🗑️ Delete Keyword")
        self.delete_button.clicked.connect(self._on_delete_alias)
        self.delete_button.setEnabled(False)
        toolbar_layout.addWidget(self.delete_button)

        toolbar_layout.addStretch()

        # Backup/Restore button
        self.backup_button = QPushButton("💾 Backup/Restore")
        self.backup_button.clicked.connect(self._on_backup_restore)
        toolbar_layout.addWidget(self.backup_button)

        layout.addLayout(toolbar_layout)

        # Main content area
        content_splitter = QSplitter(Qt.Orientation.Horizontal)

        # Alias table
        self.alias_table = AliasTable()
        content_splitter.addWidget(self.alias_table)

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

        self.total_aliases_label = QLabel("Total Keywords: 0")
        self.exact_matches_label = QLabel("Exact Matches: 0")
        self.variant_matches_label = QLabel("Variant Matches: 0")
        self.fuzzy_matches_label = QLabel("Fuzzy Matches: 0")

        stats_layout.addWidget(self.total_aliases_label)
        stats_layout.addWidget(self.exact_matches_label)
        stats_layout.addWidget(self.variant_matches_label)
        stats_layout.addWidget(self.fuzzy_matches_label)

        layout.addWidget(stats_group)
        layout.addStretch()

        return panel

    def _setup_connections(self) -> None:
        """Set up signal connections."""
        # Table connections
        self.alias_table.alias_selected.connect(self._on_alias_selected)
        self.alias_table.alias_double_clicked.connect(self._on_edit_alias)
        self.alias_table.alias_updated.connect(self._on_alias_updated)
        self.alias_table.alias_deletion_requested.connect(
            self._on_delete_alias_requested
        )

        # Thread connections
        self.alias_thread.aliases_loaded.connect(self._on_aliases_loaded)
        self.alias_thread.alias_saved.connect(self._on_alias_saved)
        self.alias_thread.alias_deleted.connect(self._on_alias_deleted)
        self.alias_thread.error_occurred.connect(self._on_error_occurred)

    def _load_aliases(self) -> None:
        """Load aliases from the business mapping manager."""
        self.status_bar.showMessage("Loading aliases...")
        self.alias_thread.load_aliases()

    def _on_aliases_loaded(self, aliases: List[Dict[str, Any]]) -> None:
        """Handle aliases loaded from the manager."""
        # Clear any active search to ensure we see all data
        self.search_edit.clear()
        
        # Load aliases into table
        self.alias_table.load_aliases(aliases)
        
        # Update statistics
        self._update_statistics(aliases)
        
        # Update status
        self.status_bar.showMessage(f"Loaded {len(aliases)} keywords")

    def _update_statistics(self, aliases: List[Dict[str, Any]]) -> None:
        """Update the statistics panel."""
        total = len(aliases)
        exact = len([a for a in aliases if a.get("match_type") == "Exact"])
        variant = len([a for a in aliases if a.get("match_type") == "Variant"])
        fuzzy = len([a for a in aliases if a.get("match_type") == "Fuzzy"])

        self.total_aliases_label.setText(f"Total Keywords: {total}")
        self.exact_matches_label.setText(f"Exact Matches: {exact}")
        self.variant_matches_label.setText(f"Variant Matches: {variant}")
        self.fuzzy_matches_label.setText(f"Fuzzy Matches: {fuzzy}")

    def _on_search_changed(self, search_text: str) -> None:
        """Handle search text changes."""
        self.alias_table.search_aliases(search_text)

    def _on_alias_selected(self, alias_data: Dict[str, Any]) -> None:
        """Handle alias selection."""
        self.edit_button.setEnabled(True)
        self.delete_button.setEnabled(True)

    def _on_add_new_business(self) -> None:
        """Handle add new business button click."""
        dialog = NewBusinessDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            business_name = dialog.get_business_name()
            if business_name:
                # Create keyword data with business name as both keyword and business name
                alias_data = {
                    "company_name": business_name,  # This is the keyword
                    "canonical_name": business_name,  # This is the business name
                    "match_type": "Exact",
                    "usage_count": 0,
                    "last_used": "",
                    "fuzzy_matching": True,
                    "case_sensitive": False,
                }
                self.alias_thread.save_alias(alias_data)

    def _on_add_alias(self) -> None:
        """Handle add keyword button click."""
        business_names = self.mapping_manager.get_canonical_names()
        dialog = AliasDialog(self, official_names=business_names)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            alias_data = dialog.get_alias_data()
            self.alias_thread.save_alias(alias_data)

    def _on_edit_alias(self, alias_data: Optional[Dict[str, Any]] = None) -> None:
        """Handle edit keyword button click."""
        if alias_data is None:
            alias_data = self.alias_table.get_selected_alias()
            if not alias_data:
                return
        business_names = self.mapping_manager.get_canonical_names()
        dialog = AliasDialog(self, alias_data, official_names=business_names)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            alias_data = dialog.get_alias_data()
            self.alias_thread.save_alias(alias_data)

    def _on_alias_updated(self, alias_data: Dict[str, Any]) -> None:
        """Handle alias updated via direct editing."""
        self.alias_thread.save_alias(alias_data)

    def _on_delete_alias(self) -> None:
        """Handle delete alias button click."""
        # Try multiple methods to get the selected alias
        alias_data = None
        
        # Method 1: Try get_selected_alias
        alias_data = self.alias_table.get_selected_alias()
        
        # Method 2: If that fails, try currentRow
        if not alias_data:
            current_row = self.alias_table.currentRow()
            if current_row >= 0:
                alias_data = self.alias_table.get_alias_at_row(current_row)
        
        # Method 3: If that fails, try selection model
        if not alias_data:
            selection_model = self.alias_table.selectionModel()
            if selection_model and selection_model.hasSelection():
                selected_rows = selection_model.selectedRows()
                if selected_rows:
                    row = selected_rows[0].row()
                    alias_data = self.alias_table.get_alias_at_row(row)
        
        if not alias_data:
            QMessageBox.warning(self, "No Selection", "Please select a keyword to delete.")
            return

        company_name = alias_data["company_name"]
        business_name = alias_data["canonical_name"]
        
        # Show more detailed confirmation message
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete the keyword?\n\n"
            f"Keyword: '{company_name}'\n"
            f"Business: '{business_name}'\n"
            f"Match Type: {alias_data.get('match_type', 'Unknown')}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.alias_thread.delete_alias(company_name)

    def _on_delete_alias_requested(self, alias_data: Dict[str, Any]) -> None:
        """Handle delete keyword request from table context menu."""
        company_name = alias_data["company_name"]
        business_name = alias_data["canonical_name"]
        
        # Show more detailed confirmation message
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete the keyword?\n\n"
            f"Keyword: '{company_name}'\n"
            f"Business: '{business_name}'\n"
            f"Match Type: {alias_data.get('match_type', 'Unknown')}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.alias_thread.delete_alias(company_name)

    def _on_alias_saved(self, alias_data: Dict[str, Any]) -> None:
        """Handle alias saved."""
        self.status_bar.showMessage(f"Keyword saved: {alias_data['company_name']}")
        self.alias_updated.emit()

        # Add a small delay to ensure file is saved before reloading
        from PyQt6.QtCore import QTimer

        QTimer.singleShot(100, self._load_aliases)

    def _on_alias_deleted(self, company_name: str) -> None:
        """Handle alias deleted."""
        self.status_bar.showMessage(f"Keyword deleted: {company_name}")
        self.alias_updated.emit()

        # Clear the table selection and disable buttons
        self.alias_table.clearSelection()
        self.edit_button.setEnabled(False)
        self.delete_button.setEnabled(False)

        # Clear any active search to ensure we see all data
        self.search_edit.clear()

        # Add a longer delay to ensure file is saved and system is stable before reloading
        from PyQt6.QtCore import QTimer

        QTimer.singleShot(200, self._safe_reload_aliases)

    def _safe_reload_aliases(self) -> None:
        """Safely reload aliases with error handling."""
        try:
            # Disable sorting temporarily to prevent issues during reload
            self.alias_table.setSortingEnabled(False)
            
            # Reload the aliases
            self._load_aliases()
            
            # Re-enable sorting after a short delay
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(100, lambda: self.alias_table.setSortingEnabled(True))
            
        except Exception as e:
            # If reload fails, show error and try to recover
            QMessageBox.warning(
                self,
                "Reload Error",
                f"Failed to reload data after deletion: {str(e)}\n\nTrying to recover...",
            )
            # Try to recover by forcing a reload
            try:
                self._load_aliases()
            except Exception as e2:
                QMessageBox.critical(
                    self,
                    "Recovery Failed",
                    f"Failed to recover from deletion error: {str(e2)}",
                )

    def _on_error_occurred(self, error_message: str) -> None:
        """Handle error from background thread."""
        QMessageBox.critical(self, "Error", f"An error occurred: {error_message}")
        self.status_bar.showMessage("Error occurred")

    def _on_backup_restore(self) -> None:
        """Handle backup/restore button click."""
        try:
            from .dialogs.backup_restore_dialog import BackupRestoreDialog

            dialog = BackupRestoreDialog(self, self.mapping_manager)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                # Reload data after backup/restore operations
                self._load_aliases()
        except ImportError as e:
            QMessageBox.warning(
                self,
                "Backup/Restore Not Available",
                "Backup and restore functionality is not available.\n\n"
                f"Error: {str(e)}",
            )
