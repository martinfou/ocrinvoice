"""
Mapping Form Widget

A form widget for adding and editing business mappings with
real-time validation and preview functionality.
"""

from typing import Dict, Any, Optional
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QLineEdit,
    QComboBox,
    QCheckBox,
    QPushButton,
    QLabel,
    QFrame,
    QMessageBox,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont


class MappingForm(QWidget):
    """
    Form widget for adding and editing business mappings.

    Provides input fields for trigger term and business canonical name,
    with real-time validation and preview functionality.
    """

    # Custom signals
    mapping_saved = pyqtSignal(dict)  # Emitted when mapping is saved
    mapping_cancelled = pyqtSignal()  # Emitted when form is cancelled

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        # Form data
        self._current_mode = "add"  # "add" or "edit"
        self._original_data: Dict[str, Any] = {}

        # Setup UI
        self._setup_ui()
        self._setup_validation()
        self._setup_connections()

        # Initial state
        self._update_preview()

    def _setup_ui(self) -> None:
        """Set up the user interface components."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Title
        title_label = QLabel("Add New Mapping")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)

        # Form layout
        form_layout = QFormLayout()
        form_layout.setSpacing(10)

        # Trigger Term field
        self.trigger_edit = QLineEdit()
        self.trigger_edit.setPlaceholderText("Enter trigger term (e.g., Hydro Quebec)")
        self.trigger_edit.setMinimumHeight(35)
        form_layout.addRow("Trigger Term:", self.trigger_edit)

        # Business Canonical Name field
        self.official_edit = QLineEdit()
        self.official_edit.setPlaceholderText(
            "Enter business canonical name (e.g., HYDRO-QUÉBEC)"
        )
        self.official_edit.setMinimumHeight(35)
        form_layout.addRow("Business Canonical Name:", self.official_edit)

        # Match Type field
        self.match_type_combo = QComboBox()
        self.match_type_combo.addItems(["Exact Match", "Partial Match"])
        self.match_type_combo.setMinimumHeight(35)
        form_layout.addRow("Match Type:", self.match_type_combo)

        main_layout.addLayout(form_layout)

        # Options frame
        options_frame = QFrame()
        options_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        options_layout = QVBoxLayout(options_frame)

        # Options title
        options_title = QLabel("Options")
        options_title.setFont(QFont("", weight=QFont.Weight.Bold))
        options_layout.addWidget(options_title)

        # Case sensitive checkbox
        self.case_sensitive_check = QCheckBox("Case sensitive matching")
        self.case_sensitive_check.setChecked(True)
        options_layout.addWidget(self.case_sensitive_check)

        # Fuzzy matching checkbox
        self.fuzzy_match_check = QCheckBox("Enable fuzzy matching")
        self.fuzzy_match_check.setChecked(False)
        options_layout.addWidget(self.fuzzy_match_check)

        main_layout.addWidget(options_frame)

        # Preview frame
        preview_frame = QFrame()
        preview_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        preview_layout = QVBoxLayout(preview_frame)

        # Preview title
        preview_title = QLabel("Preview")
        preview_title.setFont(QFont("", weight=QFont.Weight.Bold))
        preview_layout.addWidget(preview_title)

        # Preview label
        self.preview_label = QLabel(
            "Enter trigger term and business canonical name to see preview"
        )
        self.preview_label.setWordWrap(True)
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setMinimumHeight(40)
        self.preview_label.setStyleSheet(
            """
            QLabel {
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 10px;
            }
        """
        )
        preview_layout.addWidget(self.preview_label)

        main_layout.addWidget(preview_frame)

        # Buttons layout
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()

        # Cancel button
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setMinimumHeight(35)
        self.cancel_button.setMinimumWidth(80)
        buttons_layout.addWidget(self.cancel_button)

        # Save button
        self.save_button = QPushButton("Save")
        self.save_button.setMinimumHeight(35)
        self.save_button.setMinimumWidth(80)
        self.save_button.setDefault(True)
        buttons_layout.addWidget(self.save_button)

        main_layout.addLayout(buttons_layout)

        # Validation label
        self.validation_label = QLabel("")
        self.validation_label.setWordWrap(True)
        self.validation_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.validation_label.setMinimumHeight(30)
        main_layout.addWidget(self.validation_label)

    def _setup_validation(self) -> None:
        """Set up validation for form fields."""
        # Connect text change signals for validation
        self.trigger_edit.textChanged.connect(self._validate_form)
        self.official_edit.textChanged.connect(self._validate_form)

    def _setup_connections(self) -> None:
        """Set up signal/slot connections."""
        # Button connections
        self.save_button.clicked.connect(self._save_mapping)
        self.cancel_button.clicked.connect(self._cancel_form)

        # Text change connections for preview
        self.trigger_edit.textChanged.connect(self._update_preview)
        self.official_edit.textChanged.connect(self._update_preview)
        self.match_type_combo.currentTextChanged.connect(self._update_preview)

    def show_add_mode(self) -> None:
        """Show the form in add mode."""
        self._current_mode = "add"
        self._clear_form()
        self._update_title("Add New Mapping")
        self.save_button.setText("Add Mapping")

    def show_edit_mode(self, mapping_data: Dict[str, Any]) -> None:
        """Show the form in edit mode with existing data."""
        self._current_mode = "edit"
        self._original_data = mapping_data.copy()
        self._populate_form(mapping_data)
        self._update_title("Edit Mapping")
        self.save_button.setText("Update Mapping")

    def _update_title(self, title: str) -> None:
        """Update the form title."""
        # Find the title label (first QLabel in the layout)
        for i in range(self.layout().count()):  # type: ignore[union-attr]
            item = self.layout().itemAt(i)  # type: ignore[union-attr]
            if item.widget() and isinstance(item.widget(), QLabel):  # type: ignore[union-attr]
                item.widget().setText(title)  # type: ignore[union-attr]
                break

    def _clear_form(self) -> None:
        """Clear all form fields."""
        self.trigger_edit.clear()
        self.official_edit.clear()
        self.match_type_combo.setCurrentIndex(0)
        self.case_sensitive_check.setChecked(True)
        self.fuzzy_match_check.setChecked(False)
        self._original_data = {}

    def _populate_form(self, mapping_data: Dict[str, Any]) -> None:
        """Populate form fields with existing data."""
        self.trigger_edit.setText(mapping_data.get("mapping", ""))
        self.official_edit.setText(mapping_data.get("official_name", ""))

        # Set match type
        match_type = mapping_data.get("match_type", "Exact")
        if match_type == "Exact":
            self.match_type_combo.setCurrentIndex(0)
        else:
            self.match_type_combo.setCurrentIndex(1)

    def _validate_form(self) -> None:
        """Validate form fields and update validation message."""
        trigger = self.trigger_edit.text().strip()
        official = self.official_edit.text().strip()

        errors = []

        # Check for empty fields
        if not trigger:
            errors.append("Trigger term is required")

        if not official:
            errors.append("Business canonical name is required")

        # Check for minimum length
        if trigger and len(trigger) < 2:
            errors.append("Trigger term must be at least 2 characters")

        if official and len(official) < 2:
            errors.append("Business canonical name must be at least 2 characters")

        # Check for duplicate (in edit mode, exclude current mapping)
        if trigger and official:
            # TODO: Check for duplicates in the mapping manager
            pass

        # Update validation message
        if errors:
            error_text = " • ".join(errors)
            self.validation_label.setText(error_text)
            self.validation_label.setStyleSheet("color: red; font-weight: bold;")
            self.save_button.setEnabled(False)
        else:
            self.validation_label.setText("✓ Form is valid")
            self.validation_label.setStyleSheet("color: green; font-weight: bold;")
            self.save_button.setEnabled(True)

    def _update_preview(self) -> None:
        """Update the preview display."""
        trigger = self.trigger_edit.text().strip()
        official = self.official_edit.text().strip()
        match_type = self.match_type_combo.currentText()

        if trigger and official:
            preview_text = f'"{trigger}" → "{official}"\n({match_type})'
            self.preview_label.setText(preview_text)
        else:
            self.preview_label.setText(
                "Enter trigger term and business canonical name to see preview"
            )

    def _save_mapping(self) -> None:
        """Save the mapping data."""
        # Validate form
        self._validate_form()
        if not self.save_button.isEnabled():
            return

        # Collect form data
        mapping_data = {
            "mapping": self.trigger_edit.text().strip(),
            "official_name": self.official_edit.text().strip(),
            "match_type": self.match_type_combo.currentText().lower().replace(" ", "_"),
            "case_sensitive": self.case_sensitive_check.isChecked(),
            "fuzzy_match": self.fuzzy_match_check.isChecked(),
        }

        # Convert match type to internal format
        if mapping_data["match_type"] == "exact_match":
            mapping_data["match_type"] = "exact_matches"
        else:
            mapping_data["match_type"] = "partial_matches"

        # Emit save signal
        self.mapping_saved.emit(mapping_data)

    def _cancel_form(self) -> None:
        """Cancel the form and emit cancel signal."""
        # Check if there are unsaved changes
        if self._has_unsaved_changes():
            reply = QMessageBox.question(
                self,
                "Unsaved Changes",
                "You have unsaved changes. Are you sure you want to cancel?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )

            if reply == QMessageBox.StandardButton.No:
                return

        self.mapping_cancelled.emit()

    def _has_unsaved_changes(self) -> bool:
        """Check if there are unsaved changes in the form."""
        if self._current_mode == "add":
            # In add mode, check if any field has content
            return bool(self.trigger_edit.text().strip()) or bool(
                self.official_edit.text().strip()
            )
        else:
            # In edit mode, compare with original data
            current_trigger = self.trigger_edit.text().strip()
            current_official = self.official_edit.text().strip()
            current_match_type = self.match_type_combo.currentText()

            original_trigger = self._original_data.get("mapping", "")
            original_official = self._original_data.get("official_name", "")
            original_match_type = self._original_data.get("match_type", "Exact")

            return (
                current_trigger != original_trigger
                or current_official != original_official
                or current_match_type != original_match_type
            )

    def get_form_data(self) -> Dict[str, Any]:
        """Get the current form data."""
        return {
            "mapping": self.trigger_edit.text().strip(),
            "official_name": self.official_edit.text().strip(),
            "match_type": self.match_type_combo.currentText(),
            "case_sensitive": self.case_sensitive_check.isChecked(),
            "fuzzy_match": self.fuzzy_match_check.isChecked(),
        }

    def set_form_data(self, data: Dict[str, Any]) -> None:
        """Set form data from dictionary."""
        self.trigger_edit.setText(data.get("mapping", ""))
        self.official_edit.setText(data.get("official_name", ""))

        match_type = data.get("match_type", "Exact Match")
        index = self.match_type_combo.findText(match_type)
        if index >= 0:
            self.match_type_combo.setCurrentIndex(index)

        self.case_sensitive_check.setChecked(data.get("case_sensitive", True))
        self.fuzzy_match_check.setChecked(data.get("fuzzy_match", False))
