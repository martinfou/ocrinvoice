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
from ..business.business_mapping_manager import BusinessMappingManager


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
                # Reload configuration before loading aliases
                self.mapping_manager.reload_config()
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

        # Get exact matches
        exact_matches = self.mapping_manager.config.get("exact_matches", {})
        for company_name, canonical_name in exact_matches.items():
            alias_data = {
                "company_name": company_name,
                "canonical_name": canonical_name,
                "match_type": "Exact",
                "usage_count": 0,  # TODO: Implement usage tracking
                "last_used": "",
                "fuzzy_matching": True,
                "case_sensitive": False,
            }
            aliases.append(alias_data)

        # Get partial matches
        partial_matches = self.mapping_manager.config.get("partial_matches", {})
        for company_name, canonical_name in partial_matches.items():
            alias_data = {
                "company_name": company_name,
                "canonical_name": canonical_name,
                "match_type": "Partial",
                "usage_count": 0,  # TODO: Implement usage tracking
                "last_used": "",
                "fuzzy_matching": True,
                "case_sensitive": False,
            }
            aliases.append(alias_data)

        # Get fuzzy candidates
        fuzzy_candidates = self.mapping_manager.config.get("fuzzy_candidates", [])
        for canonical_name in fuzzy_candidates:
            alias_data = {
                "company_name": canonical_name,  # Use canonical name as company name for fuzzy
                "canonical_name": canonical_name,
                "match_type": "Fuzzy",
                "usage_count": 0,  # TODO: Implement usage tracking
                "last_used": "",
                "fuzzy_matching": True,
                "case_sensitive": False,
            }
            aliases.append(alias_data)

        return aliases

    def _save_alias_to_manager(self, alias_data: Dict[str, Any]):
        """Save an alias to the business mapping manager."""
        company_name = alias_data["company_name"]
        canonical_name = alias_data["canonical_name"]
        match_type = alias_data["match_type"]

        # Add to appropriate mapping type
        if match_type == "Exact":
            self.mapping_manager.add_mapping(
                company_name, canonical_name, "exact_matches"
            )
        elif match_type == "Partial":
            self.mapping_manager.add_mapping(
                company_name, canonical_name, "partial_matches"
            )
        elif match_type == "Fuzzy":
            # For fuzzy matches, add to fuzzy_candidates if not already there
            if canonical_name not in self.mapping_manager.config.get(
                "fuzzy_candidates", []
            ):
                self.mapping_manager.config.setdefault("fuzzy_candidates", []).append(
                    canonical_name
                )

        # Save the configuration
        self.mapping_manager._save_config()

    def _delete_alias_from_manager(self, company_name: str):
        """Delete an alias from the business mapping manager."""
        # Remove from exact matches
        if company_name in self.mapping_manager.config.get("exact_matches", {}):
            del self.mapping_manager.config["exact_matches"][company_name]

        # Remove from partial matches
        if company_name in self.mapping_manager.config.get("partial_matches", {}):
            del self.mapping_manager.config["partial_matches"][company_name]

        # Remove from fuzzy candidates (for fuzzy matches, company_name is the canonical_name)
        fuzzy_candidates = self.mapping_manager.config.get("fuzzy_candidates", [])
        if company_name in fuzzy_candidates:
            fuzzy_candidates.remove(company_name)

        # Ensure the configuration is properly saved
        try:
            self.mapping_manager._save_config()
        except Exception as e:
            print(f"Error saving configuration after deletion: {e}")
            raise


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

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        # Initialize business mapping manager
        self.mapping_manager = BusinessMappingManager()

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
        title_label = QLabel("Business Aliases Manager")
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

        # Add button
        self.add_button = QPushButton("➕ Add Alias")
        self.add_button.setStyleSheet(
            "QPushButton { background-color: #27ae60; color: white; border: none; "
            "padding: 8px 16px; border-radius: 4px; font-weight: bold; }"
            "QPushButton:hover { background-color: #229954; }"
        )
        self.add_button.clicked.connect(self._on_add_alias)
        toolbar_layout.addWidget(self.add_button)

        # Edit button
        self.edit_button = QPushButton("✏️ Edit Alias")
        self.edit_button.setStyleSheet(
            "QPushButton { background-color: #f39c12; color: white; border: none; "
            "padding: 8px 16px; border-radius: 4px; font-weight: bold; }"
            "QPushButton:hover { background-color: #e67e22; }"
            "QPushButton:disabled { background-color: #bdc3c7; }"
        )
        self.edit_button.clicked.connect(self._on_edit_alias)
        self.edit_button.setEnabled(False)
        toolbar_layout.addWidget(self.edit_button)

        # Delete button
        self.delete_button = QPushButton("🗑️ Delete Alias")
        self.delete_button.setStyleSheet(
            "QPushButton { background-color: #e74c3c; color: white; border: none; "
            "padding: 8px 16px; border-radius: 4px; font-weight: bold; }"
            "QPushButton:hover { background-color: #c0392b; }"
            "QPushButton:disabled { background-color: #bdc3c7; }"
        )
        self.delete_button.clicked.connect(self._on_delete_alias)
        self.delete_button.setEnabled(False)
        toolbar_layout.addWidget(self.delete_button)

        toolbar_layout.addStretch()

        # Refresh button
        self.refresh_button = QPushButton("🔄 Refresh")
        self.refresh_button.setStyleSheet(
            "QPushButton { background-color: #3498db; color: white; border: none; "
            "padding: 8px 16px; border-radius: 4px; font-weight: bold; }"
            "QPushButton:hover { background-color: #2980b9; }"
        )
        self.refresh_button.clicked.connect(self._load_aliases)
        toolbar_layout.addWidget(self.refresh_button)

        # Backup/Restore button
        self.backup_button = QPushButton("💾 Backup/Restore")
        self.backup_button.setStyleSheet(
            "QPushButton { background-color: #9b59b6; color: white; border: none; "
            "padding: 8px 16px; border-radius: 4px; font-weight: bold; }"
            "QPushButton:hover { background-color: #8e44ad; }"
        )
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

        self.total_aliases_label = QLabel("Total Aliases: 0")
        self.exact_matches_label = QLabel("Exact Matches: 0")
        self.partial_matches_label = QLabel("Partial Matches: 0")
        self.fuzzy_matches_label = QLabel("Fuzzy Matches: 0")

        stats_layout.addWidget(self.total_aliases_label)
        stats_layout.addWidget(self.exact_matches_label)
        stats_layout.addWidget(self.partial_matches_label)
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
        self.alias_table.load_aliases(aliases)
        self._update_statistics(aliases)
        self.status_bar.showMessage(f"Loaded {len(aliases)} aliases")

    def _update_statistics(self, aliases: List[Dict[str, Any]]) -> None:
        """Update the statistics panel."""
        total = len(aliases)
        exact = len([a for a in aliases if a.get("match_type") == "Exact"])
        partial = len([a for a in aliases if a.get("match_type") == "Partial"])
        fuzzy = len([a for a in aliases if a.get("match_type") == "Fuzzy"])

        self.total_aliases_label.setText(f"Total Aliases: {total}")
        self.exact_matches_label.setText(f"Exact Matches: {exact}")
        self.partial_matches_label.setText(f"Partial Matches: {partial}")
        self.fuzzy_matches_label.setText(f"Fuzzy Matches: {fuzzy}")

    def _on_search_changed(self, search_text: str) -> None:
        """Handle search text changes."""
        self.alias_table.search_aliases(search_text)

    def _on_alias_selected(self, alias_data: Dict[str, Any]) -> None:
        """Handle alias selection."""
        self.edit_button.setEnabled(True)
        self.delete_button.setEnabled(True)

    def _on_add_alias(self) -> None:
        """Handle add alias button click."""
        official_names = self.mapping_manager.get_official_names()
        dialog = AliasDialog(self, official_names=official_names)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            alias_data = dialog.get_alias_data()
            self.alias_thread.save_alias(alias_data)

    def _on_edit_alias(self, alias_data: Optional[Dict[str, Any]] = None) -> None:
        """Handle edit alias button click."""
        if alias_data is None:
            alias_data = self.alias_table.get_selected_alias()
            if not alias_data:
                return
        official_names = self.mapping_manager.get_official_names()
        dialog = AliasDialog(self, alias_data, official_names=official_names)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            alias_data = dialog.get_alias_data()
            self.alias_thread.save_alias(alias_data)

    def _on_alias_updated(self, alias_data: Dict[str, Any]) -> None:
        """Handle alias updated via direct editing."""
        self.alias_thread.save_alias(alias_data)

    def _on_delete_alias(self) -> None:
        """Handle delete alias button click."""
        alias_data = self.alias_table.get_selected_alias()
        if not alias_data:
            return

        company_name = alias_data["company_name"]
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete the alias for '{company_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.alias_thread.delete_alias(company_name)

    def _on_alias_saved(self, alias_data: Dict[str, Any]) -> None:
        """Handle alias saved."""
        self.status_bar.showMessage(f"Alias saved: {alias_data['company_name']}")
        self.alias_updated.emit()

        # Add a small delay to ensure file is saved before reloading
        from PyQt6.QtCore import QTimer

        QTimer.singleShot(100, self._load_aliases)

    def _on_alias_deleted(self, company_name: str) -> None:
        """Handle alias deleted."""
        self.status_bar.showMessage(f"Alias deleted: {company_name}")
        self.alias_updated.emit()

        # Clear the table selection before reloading
        self.alias_table.clearSelection()
        self.edit_button.setEnabled(False)
        self.delete_button.setEnabled(False)

        # Add a small delay to ensure file is saved before reloading
        from PyQt6.QtCore import QTimer

        QTimer.singleShot(100, self._load_aliases)

    def _on_error_occurred(self, error_message: str) -> None:
        """Handle error from background thread."""
        QMessageBox.critical(self, "Error", f"An error occurred: {error_message}")
        self.status_bar.showMessage("Error occurred")

    def refresh_data(self) -> None:
        """Refresh the alias data."""
        self._load_aliases()

    def _on_backup_restore(self) -> None:
        """Handle backup/restore button click."""
        try:
            from .dialogs.backup_restore_dialog import BackupRestoreDialog

            dialog = BackupRestoreDialog(self, self.mapping_manager)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                # Refresh data after backup/restore operations
                self._load_aliases()
        except ImportError as e:
            QMessageBox.warning(
                self,
                "Backup/Restore Not Available",
                "Backup and restore functionality is not available.\n\n"
                f"Error: {str(e)}",
            )
