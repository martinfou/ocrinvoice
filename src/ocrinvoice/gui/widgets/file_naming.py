"""
File Naming Widget

Provides GUI interface for file naming template system with live preview.
"""

from typing import Dict, Any, Optional, Tuple
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QComboBox,
    QPushButton,
    QTextEdit,
    QGroupBox,
    QCheckBox,
    QMessageBox,
    QFileDialog,
)
from PyQt6.QtCore import pyqtSignal

from ...utils.file_manager import FileManager


class FileNamingWidget(QWidget):
    """Widget for managing file naming templates and preview."""

    # Signal emitted when template changes
    template_changed = pyqtSignal(str)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.config: Dict[str, Any] = {}
        self.extracted_data: Dict[str, Any] = {}
        self.original_filename: str = ""
        self.full_file_path: str = ""  # Store the full file path
        self.file_manager: Optional[FileManager] = None
        self._setup_ui()
        self._setup_connections()

    def _setup_ui(self) -> None:
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # Title with unified blue/gray theme
        title = QLabel("File Naming")
        title.setStyleSheet(
            "font-size: 16px; font-weight: bold; margin-bottom: 15px; "
            "color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 5px;"
        )
        layout.addWidget(title)

        # Template Builder Group
        template_group = QGroupBox("Naming Template")
        template_layout = QVBoxLayout(template_group)

        # Template format input
        format_layout = QHBoxLayout()
        format_label = QLabel("Template Format:")
        self.template_input = QLineEdit()
        self.template_input.setPlaceholderText("Enter template format...")
        self.template_input.setText("{documentType}_{company}_{date}_{total}.pdf")
        format_layout.addWidget(format_label)
        format_layout.addWidget(self.template_input)
        template_layout.addLayout(format_layout)

        # Template builder buttons
        builder_layout = QHBoxLayout()
        builder_label = QLabel("Add Field:")

        self.field_combo = QComboBox()
        self.field_combo.addItems(
            [
                "Document Type",
                "Company Name",
                "Date",
                "Total Amount",
                "Invoice Number",
                "Custom Text",
            ]
        )

        self.add_field_btn = QPushButton("Add")
        self.add_field_btn.setToolTip("Add the selected field to the template")
        self.add_field_btn.clicked.connect(self._add_template_field)
        self.add_field_btn.setStyleSheet(
            "QPushButton { background-color: #3498db; color: white; border: none; "
            "padding: 6px 12px; border-radius: 4px; font-weight: bold; }"
            "QPushButton:hover { background-color: #2980b9; }"
        )

        builder_layout.addWidget(builder_label)
        builder_layout.addWidget(self.field_combo)
        builder_layout.addWidget(self.add_field_btn)
        builder_layout.addStretch()
        template_layout.addLayout(builder_layout)

        # Template presets
        preset_layout = QHBoxLayout()
        preset_label = QLabel("Presets:")
        self.preset_combo = QComboBox()
        self.preset_combo.addItems(
            [
                "Default: {documentType}_{company}_{date}_{total}.pdf",
                "Simple: {company}_{date}.pdf",
                "Detailed: {date}_{company}_{total}_{invoice_number}.pdf",
                "Custom...",
            ]
        )
        self.preset_combo.currentTextChanged.connect(self._on_preset_changed)

        preset_layout.addWidget(preset_label)
        preset_layout.addWidget(self.preset_combo)
        preset_layout.addStretch()
        template_layout.addLayout(preset_layout)

        layout.addWidget(template_group)

        # Options Group
        options_group = QGroupBox("Options")
        options_layout = QVBoxLayout(options_group)

        # Document type selection
        doc_type_layout = QHBoxLayout()
        doc_type_label = QLabel("Document Type:")
        self.doc_type_combo = QComboBox()
        self.doc_type_combo.addItems(["facture", "relevé", "invoice", "statement"])
        doc_type_layout.addWidget(doc_type_label)
        doc_type_layout.addWidget(self.doc_type_combo)
        doc_type_layout.addStretch()
        options_layout.addLayout(doc_type_layout)

        # File management options
        self.rename_enabled_cb = QCheckBox("Enable file renaming")
        self.rename_enabled_cb.setChecked(True)
        options_layout.addWidget(self.rename_enabled_cb)

        self.backup_original_cb = QCheckBox("Create backup of original file")
        self.backup_original_cb.setChecked(False)
        self.backup_original_cb.setToolTip(
            "Creates a backup copy before renaming the file"
        )
        options_layout.addWidget(self.backup_original_cb)

        # Backup location (optional)
        backup_layout = QHBoxLayout()
        backup_label = QLabel("Backup Location:")
        self.backup_location_edit = QLineEdit()
        self.backup_location_edit.setPlaceholderText("Same folder (default)")
        self.backup_location_edit.setEnabled(False)
        backup_browse_btn = QPushButton("Browse...")
        backup_browse_btn.setEnabled(False)
        backup_browse_btn.clicked.connect(self._on_select_backup_location)

        backup_layout.addWidget(backup_label)
        backup_layout.addWidget(self.backup_location_edit)
        backup_layout.addWidget(backup_browse_btn)
        backup_layout.addStretch()
        options_layout.addLayout(backup_layout)

        # Connect backup checkbox to enable/disable backup location
        self.backup_original_cb.toggled.connect(self._on_backup_toggled)

        self.dry_run_cb = QCheckBox("Dry run (preview only)")
        self.dry_run_cb.setChecked(False)
        options_layout.addWidget(self.dry_run_cb)

        layout.addWidget(options_group)

        # Preview Group
        preview_group = QGroupBox("Live Preview")
        preview_layout = QVBoxLayout(preview_group)

        # Original filename with full path
        original_layout = QHBoxLayout()
        original_label = QLabel("Original:")
        self.original_filename_label = QLabel("No file selected")
        self.original_filename_label.setStyleSheet(
            "color: #2c3e50; font-style: italic;"
        )
        self.original_filename_label.setToolTip("Click to see full path")
        self.original_filename_label.mousePressEvent = self._show_full_path
        original_layout.addWidget(original_label)
        original_layout.addWidget(self.original_filename_label)
        original_layout.addStretch()
        preview_layout.addLayout(original_layout)

        # New filename preview with full path
        new_layout = QHBoxLayout()
        new_label = QLabel("New Name:")
        self.new_filename_label = QLabel("No preview available")
        self.new_filename_label.setStyleSheet("color: #2c3e50; font-style: italic;")
        self.new_filename_label.setToolTip("Click to see full path")
        self.new_filename_label.mousePressEvent = self._show_new_full_path
        new_layout.addWidget(new_label)
        new_layout.addWidget(self.new_filename_label)
        new_layout.addStretch()
        preview_layout.addLayout(new_layout)

        # Preview details
        self.preview_details = QTextEdit()
        self.preview_details.setMaximumHeight(80)
        self.preview_details.setReadOnly(True)
        self.preview_details.setStyleSheet(
            "background-color: #ecf0f1; border: 1px solid #bdc3c7; border-radius: 4px;"
        )
        preview_layout.addWidget(self.preview_details)

        layout.addWidget(preview_group)

        # Action buttons with unified blue/gray theme
        action_layout = QHBoxLayout()

        self.rename_btn = QPushButton("Rename File")
        self.rename_btn.setEnabled(False)
        self.rename_btn.setToolTip("Rename the current file using the template")
        self.rename_btn.clicked.connect(self._rename_file)
        self.rename_btn.setStyleSheet(
            "QPushButton { background-color: #3498db; color: white; border: none; "
            "padding: 8px 16px; border-radius: 4px; font-weight: bold; }"
            "QPushButton:hover { background-color: #2980b9; }"
            "QPushButton:disabled { background-color: #bdc3c7; color: #7f8c8d; }"
        )

        self.open_folder_btn = QPushButton("Open Folder")
        self.open_folder_btn.setEnabled(False)
        self.open_folder_btn.setToolTip("Open the folder containing the current file")
        self.open_folder_btn.clicked.connect(self._open_folder)
        self.open_folder_btn.setStyleSheet(
            "QPushButton { background-color: #5dade2; color: white; border: none; "
            "padding: 8px 16px; border-radius: 4px; font-weight: bold; }"
            "QPushButton:hover { background-color: #3498db; }"
            "QPushButton:disabled { background-color: #bdc3c7; color: #7f8c8d; }"
        )

        action_layout.addWidget(self.rename_btn)
        action_layout.addWidget(self.open_folder_btn)
        action_layout.addStretch()

        layout.addLayout(action_layout)

    def _setup_connections(self) -> None:
        """Set up signal connections."""
        self.template_input.textChanged.connect(self._on_template_changed)
        self.doc_type_combo.currentTextChanged.connect(self._update_preview)
        self.rename_enabled_cb.toggled.connect(self._update_preview)
        self.backup_original_cb.toggled.connect(self._update_preview)
        self.dry_run_cb.toggled.connect(self._update_preview)

    def _add_template_field(self) -> None:
        """Add a field to the template."""
        field = self.field_combo.currentText()

        # Map field names to template variables
        field_map = {
            "Document Type": "{documentType}",
            "Company Name": "{company}",
            "Date": "{date}",
            "Total Amount": "{total}",
            "Invoice Number": "{invoice_number}",
            "Custom Text": "{custom}",
        }

        template_var = field_map.get(field, field)

        if field == "Custom Text":
            # Prompt for custom text
            custom_text, ok = QLineEdit.getText(
                self, "Custom Text", "Enter custom text:"
            )
            if ok and custom_text:
                template_var = custom_text

        # Append to the current text
        current_text = self.template_input.text()
        self.template_input.setText(current_text + template_var)

    def _on_preset_changed(self, preset: str) -> None:
        """Handle preset template selection."""
        if preset == "Custom...":
            return  # Don't change template for custom option

        # Extract template from preset text
        template = preset.split(": ", 1)[1] if ": " in preset else preset
        self.template_input.setText(template)

    def _validate_template(self, template: str) -> Tuple[bool, str]:
        """Validate the template format."""
        if not template:
            return False, "Template cannot be empty"

        # Check for required fields
        required_fields = ["{documentType}", "{company}", "{date}", "{total}"]
        missing_fields = []
        for field in required_fields:
            if field not in template:
                missing_fields.append(field)

        if missing_fields:
            return False, f"Missing required fields: {', '.join(missing_fields)}"

        # Check for invalid characters in template
        invalid_chars = '<>:"/\\|?*'
        found_invalid = []
        for char in invalid_chars:
            if char in template:
                found_invalid.append(char)

        if found_invalid:
            return False, f"Invalid characters in template: {', '.join(found_invalid)}"

        # Check if template ends with .pdf
        if not template.endswith(".pdf"):
            return False, "Template must end with .pdf extension"

        return True, "Template is valid"

    def _validate_filename(self, filename: str) -> Tuple[bool, str]:
        """Validate the generated filename."""
        if not filename:
            return False, "Filename cannot be empty"

        # Check for invalid characters
        invalid_chars = '<>:"/\\|?*'
        found_invalid = []
        for char in invalid_chars:
            if char in filename:
                found_invalid.append(char)

        if found_invalid:
            return False, f"Invalid characters in filename: {', '.join(found_invalid)}"

        # Check filename length (Windows limit is 260 chars)
        if len(filename) > 260:
            return False, "Filename too long (max 260 characters)"

        # Check if filename is too short
        if len(filename) < 5:  # At least "a.pdf"
            return False, "Filename too short"

        return True, "Filename is valid"

    def _on_template_changed(self) -> None:
        """Handle template format changes."""
        template = self.template_input.text()

        # Validate template
        is_valid, message = self._validate_template(template)

        # Update template input styling based on validation
        if is_valid:
            self.template_input.setStyleSheet("")
        else:
            self.template_input.setStyleSheet(
                "border: 1px solid red; background-color: #fff0f0;"
            )

        # Update preview
        self._update_preview()

        # Emit signal
        self.template_changed.emit(template)

        # Show validation message in status if invalid
        if not is_valid:
            # Find parent window to show status message
            parent = self.parent()
            while parent and not hasattr(parent, "status_bar"):
                parent = parent.parent()
            if parent and hasattr(parent, "status_bar"):
                parent.status_bar.showMessage(f"Template validation: {message}")

    def update_config(self, config: Dict[str, Any]) -> None:
        """Update the configuration."""
        self.config = config

        # Update file manager
        self._update_file_manager()

        # Update UI with config values
        file_config = config.get("file_management", {})

        # Set template format
        template_format = file_config.get(
            "rename_format", "{documentType}_{company}_{date}_{total}.pdf"
        )
        self.template_input.setText(template_format)

        # Set document type
        doc_type = file_config.get("document_type", "facture")
        index = self.doc_type_combo.findText(doc_type)
        if index >= 0:
            self.doc_type_combo.setCurrentIndex(index)

        # Set options
        self.rename_enabled_cb.setChecked(file_config.get("rename_files", True))
        self.backup_original_cb.setChecked(file_config.get("backup_original", False))
        self.dry_run_cb.setChecked(file_config.get("rename_dry_run", False))

    def update_data(
        self,
        extracted_data: Dict[str, Any],
        original_filename: str = "",
        full_file_path: str = "",
    ) -> None:
        """Update with extracted data, original filename, and full file path."""
        self.extracted_data = extracted_data
        self.original_filename = original_filename
        self.full_file_path = full_file_path

        # Update preview
        self._update_preview()

        # Enable/disable buttons
        has_data = bool(extracted_data and original_filename and full_file_path)
        self.rename_btn.setEnabled(has_data and self.rename_enabled_cb.isChecked())
        self.open_folder_btn.setEnabled(has_data)

    def _update_file_manager(self) -> None:
        """Update the file manager with current configuration."""
        # Create file management config
        file_config = {
            "rename_files": self.rename_enabled_cb.isChecked(),
            "rename_format": self.template_input.text(),
            "rename_dry_run": self.dry_run_cb.isChecked(),
            "backup_original": self.backup_original_cb.isChecked(),
            "document_type": self.doc_type_combo.currentText(),
        }

        # Update main config
        self.config["file_management"] = file_config

        # Create file manager
        self.file_manager = FileManager(self.config)

    def _update_preview(self) -> None:
        """Update the live preview."""
        if not self.extracted_data or not self.original_filename:
            self.new_filename_label.setText("No preview available")
            self.preview_details.clear()
            return

        # Update file manager
        self._update_file_manager()

        if not self.file_manager:
            return

        try:
            # Generate preview filename
            preview_filename = self.file_manager.format_filename(self.extracted_data)

            # Validate filename
            is_valid, message = self._validate_filename(preview_filename)

            # Update labels
            self.original_filename_label.setText(self.original_filename)
            self.new_filename_label.setText(preview_filename)

            # Update filename label styling based on validation
            if is_valid:
                self.new_filename_label.setStyleSheet(
                    "color: #666; font-style: italic;"
                )
            else:
                self.new_filename_label.setStyleSheet("color: red; font-style: italic;")

            # Update preview details
            details = self._generate_preview_details()
            if not is_valid:
                details += f"\n\nValidation Error: {message}"
            self.preview_details.setPlainText(details)

            # Enable/disable rename button based on validation
            self.rename_btn.setEnabled(self.rename_enabled_cb.isChecked() and is_valid)

        except Exception as e:
            self.new_filename_label.setText(f"Error: {str(e)}")
            self.new_filename_label.setStyleSheet("color: red; font-style: italic;")
            self.preview_details.clear()

    def _generate_preview_details(self) -> str:
        """Generate detailed preview information."""
        if not self.extracted_data:
            return "No data available"

        details = []
        details.append("Template Variables:")

        # Show available data
        data_mapping = {
            "documentType": self.doc_type_combo.currentText(),
            "company": self.extracted_data.get("company", "unknown"),
            "date": self.extracted_data.get("date", "unknown"),
            "total": self.extracted_data.get("total", "unknown"),
            "invoice_number": self.extracted_data.get("invoice_number", "unknown"),
        }

        for key, value in data_mapping.items():
            details.append(f"  {key}: {value}")

        details.append("")
        details.append("Options:")
        details.append(f"  Rename enabled: {self.rename_enabled_cb.isChecked()}")
        details.append(f"  Dry run: {self.dry_run_cb.isChecked()}")
        details.append(f"  Backup original: {self.backup_original_cb.isChecked()}")

        return "\n".join(details)

    def _show_full_path(self, event) -> None:
        """Show the full path of the original file."""
        if self.full_file_path:
            QMessageBox.information(
                self, "Original File Path", f"Full path:\n{self.full_file_path}"
            )

    def _show_new_full_path(self, event) -> None:
        """Show the full path of the new file."""
        if (
            self.full_file_path
            and self.new_filename_label.text() != "No preview available"
        ):
            from pathlib import Path

            file_path = Path(self.full_file_path)
            new_path = file_path.parent / self.new_filename_label.text()
            QMessageBox.information(self, "New File Path", f"Full path:\n{new_path}")

    def _rename_file(self) -> None:
        """Rename the current file."""
        if (
            not self.extracted_data
            or not self.original_filename
            or not self.full_file_path
        ):
            QMessageBox.warning(
                self, "Error", "No file or data available for renaming."
            )
            return

        if not self.file_manager:
            QMessageBox.warning(self, "Error", "File manager not initialized.")
            return

        # Get the new filename
        new_filename = self.new_filename_label.text()

        if new_filename == "No preview available":
            QMessageBox.warning(self, "Error", "No valid filename preview available.")
            return

        # Check for file conflicts
        if not self._check_file_conflict(new_filename):
            return  # User cancelled

        try:
            from pathlib import Path
            import shutil

            # Get the original file path
            original_path = Path(self.full_file_path)
            new_path = original_path.parent / new_filename

            # Show confirmation with full paths
            reply = QMessageBox.question(
                self,
                "Confirm Rename",
                f"Rename file?\n\n" f"From: {original_path}\n" f"To: {new_path}",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )

            if reply == QMessageBox.StandardButton.Yes:
                # Create backup if enabled
                if self.backup_original_cb.isChecked():
                    backup_path = original_path.parent / f"backup_{original_path.name}"
                    shutil.copy2(original_path, backup_path)

                # Perform the rename
                if self.dry_run_cb.isChecked():
                    QMessageBox.information(
                        self,
                        "Dry Run",
                        f"DRY RUN - Would rename:\n{original_path}\n→\n{new_path}",
                    )
                else:
                    original_path.rename(new_path)
                    QMessageBox.information(
                        self,
                        "Success",
                        f"File renamed successfully!\n\n"
                        f"From: {original_path}\n"
                        f"To: {new_path}",
                    )

                    # Update the stored path
                    self.full_file_path = str(new_path)
                    self.original_filename = new_path.name
                    self.original_filename_label.setText(self.original_filename)

                    # Update status in main window
                    parent = self.parent()
                    while parent and not hasattr(parent, "status_bar"):
                        parent = parent.parent()
                    if parent and hasattr(parent, "status_bar"):
                        parent.status_bar.showMessage(f"✅ File renamed: {new_path}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to rename file:\n{str(e)}")

    def _check_file_conflict(self, new_filename: str) -> bool:
        """Check if a file conflict exists and handle it."""
        if not self.full_file_path:
            return True  # No path available, skip conflict check

        from pathlib import Path

        # Get the actual directory from the full file path
        original_path = Path(self.full_file_path)
        new_path = original_path.parent / new_filename

        if new_path.exists():
            # File conflict detected
            reply = QMessageBox.question(
                self,
                "File Conflict",
                f"The file already exists:\n{new_path}\n\n"
                f"Would you like to:\n"
                f"• Add timestamp to make it unique\n"
                f"• Overwrite the existing file\n"
                f"• Cancel the operation",
                QMessageBox.StandardButton.Yes
                | QMessageBox.StandardButton.No
                | QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Yes,
            )

            if reply == QMessageBox.StandardButton.Yes:
                # Add timestamp
                return self._add_timestamp_to_filename(new_filename)
            elif reply == QMessageBox.StandardButton.No:
                # Overwrite
                return True
            else:
                # Cancel
                return False

        return True

    def _add_timestamp_to_filename(self, filename: str) -> bool:
        """Add timestamp to filename to make it unique."""
        from datetime import datetime

        # Add timestamp to filename
        timestamp = datetime.now().strftime("%H%M%S")
        name_without_ext = filename[:-4]  # Remove .pdf
        new_filename = f"{name_without_ext}_{timestamp}.pdf"

        # Update the preview
        self.new_filename_label.setText(new_filename)

        return True

    def _open_folder(self) -> None:
        """Open the folder containing the current file."""
        if not self.full_file_path:
            QMessageBox.warning(self, "Error", "No file selected.")
            return

        try:
            import subprocess
            import sys
            from pathlib import Path

            # Get the actual directory from the full file path
            file_path = Path(self.full_file_path)
            folder_path = file_path.parent

            # Open folder based on platform
            if sys.platform == "darwin":  # macOS
                subprocess.run(["open", str(folder_path)])
            elif sys.platform == "win32":  # Windows
                subprocess.run(["explorer", str(folder_path)])
            else:  # Linux
                subprocess.run(["xdg-open", str(folder_path)])

            QMessageBox.information(self, "Success", f"Opened folder: {folder_path}")

        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not open folder: {str(e)}")

    def _on_backup_toggled(self, enabled: bool) -> None:
        """Handle backup checkbox toggle."""
        self.backup_location_edit.setEnabled(enabled)
        # Find the backup browse button and enable/disable it
        for child in self.findChildren(QPushButton):
            if (
                child.text() == "Browse..."
                and child.parent() == self.backup_location_edit.parent()
            ):
                child.setEnabled(enabled)
                break

    def _on_select_backup_location(self) -> None:
        """Handle backup location selection."""
        backup_dir = QFileDialog.getExistingDirectory(
            self, "Select Backup Directory", "", QFileDialog.Option.ShowDirsOnly
        )
        if backup_dir:
            self.backup_location_edit.setText(backup_dir)

    def get_config(self) -> Dict[str, Any]:
        """Get the current configuration."""
        return self.config
