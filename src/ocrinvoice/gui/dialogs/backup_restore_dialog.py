"""
Backup and Restore Dialog

A dialog for managing business mappings backups and restores.
Provides functionality to create backups, list existing backups,
and restore from backup files.
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QFileDialog,
    QGroupBox,
    QTextEdit,
    QProgressBar,
    QSplitter,
    QFrame,
    QSizePolicy,
    QWidget,
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread, QTimer
from PyQt6.QtGui import QFont, QIcon

from ...business.business_mapping_manager import BusinessMappingManager


class BackupRestoreThread(QThread):
    """Background thread for backup and restore operations."""

    # Signals
    backup_created = pyqtSignal(str)  # Emits backup file path
    backup_restored = pyqtSignal(str)  # Emits restored file path
    backups_loaded = pyqtSignal(list)  # Emits list of backup info
    error_occurred = pyqtSignal(str)  # Emits error message
    progress_updated = pyqtSignal(int)  # Emits progress percentage

    def __init__(self, mapping_manager: BusinessMappingManager):
        super().__init__()
        self.mapping_manager = mapping_manager
        self._operation = None
        self._data = None

    def create_backup(self, backup_path: Optional[str] = None):
        """Create a backup."""
        self._operation = "create_backup"
        self._data = backup_path
        self.start()

    def restore_backup(self, backup_path: str):
        """Restore from backup."""
        self._operation = "restore_backup"
        self._data = backup_path
        self.start()

    def load_backups(self):
        """Load list of available backups."""
        self._operation = "load_backups"
        self.start()

    def run(self):
        """Run the background operation."""
        try:
            self.progress_updated.emit(10)

            if self._operation == "create_backup":
                backup_path = self.mapping_manager.create_backup(self._data)
                self.progress_updated.emit(100)
                self.backup_created.emit(backup_path)

            elif self._operation == "restore_backup":
                success = self.mapping_manager.restore_backup(self._data)
                self.progress_updated.emit(100)
                if success:
                    self.backup_restored.emit(self._data)
                else:
                    self.error_occurred.emit("Failed to restore backup")

            elif self._operation == "load_backups":
                backup_files = self.mapping_manager.list_backups()
                backup_info_list = []

                for backup_path in backup_files:
                    info = self.mapping_manager.get_backup_info(backup_path)
                    if info:
                        backup_info_list.append(info)

                self.progress_updated.emit(100)
                self.backups_loaded.emit(backup_info_list)

        except Exception as e:
            self.error_occurred.emit(str(e))


class BackupRestoreDialog(QDialog):
    """Dialog for backup and restore operations."""

    def __init__(
        self, parent=None, mapping_manager: Optional[BusinessMappingManager] = None
    ):
        super().__init__(parent)
        self.mapping_manager = mapping_manager or BusinessMappingManager()

        # Background thread
        self.backup_thread = BackupRestoreThread(self.mapping_manager)

        self.setWindowTitle("Backup & Restore Business Mappings")
        self.setModal(True)
        self.setMinimumSize(700, 500)

        self._setup_ui()
        self._setup_connections()
        self._load_backups()

    def _setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Title
        title_label = QLabel("Backup & Restore Business Mappings")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(14)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        # Description
        desc_label = QLabel(
            "Create backups of your business mappings or restore from previous backups. "
            "Backups are automatically saved in the config/backups directory."
        )
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)

        # Main content area
        content_splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left panel - Backup operations
        left_panel = self._create_backup_panel()
        content_splitter.addWidget(left_panel)

        # Right panel - Backup list
        right_panel = self._create_backup_list_panel()
        content_splitter.addWidget(right_panel)

        # Set splitter proportions
        content_splitter.setSizes([300, 400])
        layout.addWidget(content_splitter)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.accept)
        button_layout.addWidget(self.close_button)

        layout.addLayout(button_layout)

    def _create_backup_panel(self) -> QWidget:
        """Create the backup operations panel."""
        panel = QWidget()
        layout = QVBoxLayout(panel)

        # Create Backup group
        backup_group = QGroupBox("Create Backup")
        backup_layout = QVBoxLayout(backup_group)

        backup_desc = QLabel(
            "Create a timestamped backup of your current business mappings configuration."
        )
        backup_desc.setWordWrap(True)
        backup_layout.addWidget(backup_desc)

        self.create_backup_button = QPushButton("💾 Create Backup")
        self.create_backup_button.clicked.connect(self._on_create_backup)
        backup_layout.addWidget(self.create_backup_button)

        layout.addWidget(backup_group)

        # Restore Backup group
        restore_group = QGroupBox("Restore Backup")
        restore_layout = QVBoxLayout(restore_group)

        restore_desc = QLabel(
            "Restore business mappings from a backup file. "
            "This will replace your current configuration."
        )
        restore_desc.setWordWrap(True)
        restore_layout.addWidget(restore_desc)

        self.restore_backup_button = QPushButton("📂 Restore from File...")
        self.restore_backup_button.clicked.connect(self._on_restore_backup)
        restore_layout.addWidget(self.restore_backup_button)

        layout.addWidget(restore_group)

        # Current Configuration group
        current_group = QGroupBox("Current Configuration")
        current_layout = QVBoxLayout(current_group)

        self.current_stats_text = QTextEdit()
        self.current_stats_text.setMaximumHeight(120)
        self.current_stats_text.setReadOnly(True)
        current_layout.addWidget(self.current_stats_text)

        layout.addWidget(current_group)
        layout.addStretch()

        return panel

    def _create_backup_list_panel(self) -> QWidget:
        """Create the backup list panel."""
        panel = QWidget()
        layout = QVBoxLayout(panel)

        # Header
        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel("Available Backups"))

        self.refresh_button = QPushButton("🔄 Refresh")
        self.refresh_button.clicked.connect(self._load_backups)
        header_layout.addWidget(self.refresh_button)

        layout.addLayout(header_layout)

        # Backup list
        self.backup_list = QListWidget()
        layout.addWidget(self.backup_list)

        # Backup details
        self.backup_details = QTextEdit()
        self.backup_details.setMaximumHeight(150)
        self.backup_details.setReadOnly(True)
        layout.addWidget(self.backup_details)

        # Restore from list button
        self.restore_from_list_button = QPushButton("📥 Restore Selected Backup")
        self.restore_from_list_button.clicked.connect(self._on_restore_from_list)
        self.restore_from_list_button.setEnabled(False)
        layout.addWidget(self.restore_from_list_button)

        return panel

    def _setup_connections(self):
        """Set up signal connections."""
        # Thread connections
        self.backup_thread.backup_created.connect(self._on_backup_created)
        self.backup_thread.backup_restored.connect(self._on_backup_restored)
        self.backup_thread.backups_loaded.connect(self._on_backups_loaded)
        self.backup_thread.error_occurred.connect(self._on_error_occurred)
        self.backup_thread.progress_updated.connect(self._on_progress_updated)

        # List connections
        self.backup_list.itemSelectionChanged.connect(self._on_backup_selected)

    def _load_backups(self):
        """Load the list of available backups."""
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.backup_thread.load_backups()

    def _update_current_stats(self):
        """Update the current configuration statistics."""
        stats = self.mapping_manager.get_stats()

        stats_text = f"""Official Names: {stats['official_names']}
Exact Matches: {stats['exact_matches']}
Partial Matches: {stats['partial_matches']}
Fuzzy Candidates: {stats['fuzzy_candidates']}
Total Businesses: {stats['total_businesses']}"""

        self.current_stats_text.setText(stats_text)

    def _on_create_backup(self):
        """Handle create backup button click."""
        reply = QMessageBox.question(
            self,
            "Create Backup",
            "Create a backup of your current business mappings configuration?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes,
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            self.backup_thread.create_backup()

    def _on_restore_backup(self):
        """Handle restore backup button click."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Backup File", "", "JSON Files (*.json);;All Files (*)"
        )

        if file_path:
            reply = QMessageBox.warning(
                self,
                "Restore Backup",
                "This will replace your current business mappings configuration. "
                "A backup of your current configuration will be created first. "
                "Do you want to continue?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )

            if reply == QMessageBox.StandardButton.Yes:
                self.progress_bar.setVisible(True)
                self.progress_bar.setValue(0)
                self.backup_thread.restore_backup(file_path)

    def _on_restore_from_list(self):
        """Handle restore from list button click."""
        current_item = self.backup_list.currentItem()
        if not current_item:
            return

        backup_path = current_item.data(Qt.ItemDataRole.UserRole)
        if not backup_path:
            return

        reply = QMessageBox.warning(
            self,
            "Restore Backup",
            f"Restore business mappings from backup:\n{os.path.basename(backup_path)}\n\n"
            "This will replace your current configuration. "
            "A backup of your current configuration will be created first. "
            "Do you want to continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            self.backup_thread.restore_backup(backup_path)

    def _on_backup_created(self, backup_path: str):
        """Handle backup created successfully."""
        self.progress_bar.setVisible(False)
        QMessageBox.information(
            self,
            "Backup Created",
            f"Backup created successfully:\n{os.path.basename(backup_path)}",
        )
        self._load_backups()
        self._update_current_stats()

    def _on_backup_restored(self, backup_path: str):
        """Handle backup restored successfully."""
        self.progress_bar.setVisible(False)
        QMessageBox.information(
            self,
            "Backup Restored",
            f"Backup restored successfully from:\n{os.path.basename(backup_path)}",
        )
        self._load_backups()
        self._update_current_stats()

    def _on_backups_loaded(self, backup_info_list: List[Dict[str, Any]]):
        """Handle backups loaded successfully."""
        self.progress_bar.setVisible(False)
        self.backup_list.clear()

        for backup_info in backup_info_list:
            # Create display text
            created_time = datetime.fromtimestamp(backup_info["created_time"])
            display_text = f"{created_time.strftime('%Y-%m-%d %H:%M:%S')} - "
            display_text += f"{backup_info['official_names_count']} official names, "
            display_text += f"{backup_info['exact_matches_count']} exact matches"

            item = QListWidgetItem(display_text)
            item.setData(Qt.ItemDataRole.UserRole, backup_info["file_path"])
            self.backup_list.addItem(item)

    def _on_backup_selected(self):
        """Handle backup selection changed."""
        current_item = self.backup_list.currentItem()
        if not current_item:
            self.backup_details.clear()
            self.restore_from_list_button.setEnabled(False)
            return

        backup_path = current_item.data(Qt.ItemDataRole.UserRole)
        if not backup_path:
            return

        # Get backup info
        backup_info = self.mapping_manager.get_backup_info(backup_path)
        if not backup_info:
            return

        # Display backup details
        created_time = datetime.fromtimestamp(backup_info["created_time"])
        modified_time = datetime.fromtimestamp(backup_info["modified_time"])

        details_text = f"""File: {os.path.basename(backup_path)}
Size: {backup_info['file_size']} bytes
Created: {created_time.strftime('%Y-%m-%d %H:%M:%S')}
Modified: {modified_time.strftime('%Y-%m-%d %H:%M:%S')}

Configuration:
- Official Names: {backup_info['official_names_count']}
- Exact Matches: {backup_info['exact_matches_count']}
- Partial Matches: {backup_info['partial_matches_count']}
- Fuzzy Candidates: {backup_info['fuzzy_candidates_count']}"""

        self.backup_details.setText(details_text)
        self.restore_from_list_button.setEnabled(True)

    def _on_error_occurred(self, error_message: str):
        """Handle error occurred."""
        self.progress_bar.setVisible(False)
        QMessageBox.critical(self, "Error", f"An error occurred:\n{error_message}")

    def _on_progress_updated(self, progress: int):
        """Handle progress update."""
        self.progress_bar.setValue(progress)

    def showEvent(self, event):
        """Handle dialog show event."""
        super().showEvent(event)
        self._update_current_stats()
