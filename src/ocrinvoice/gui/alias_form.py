"""
Business Alias Form Widget

A form widget for adding and editing business aliases with validation
and preview functionality.
"""

from typing import Dict, Any, Optional, List
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
    QMessageBox,
    QGroupBox,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont


class AliasForm(QWidget):
    """
    Form widget for adding and editing business aliases.

    Provides input fields for company name, canonical name, match type,
    and validation with preview functionality.
    """

    # Custom signals
    alias_saved = pyqtSignal(dict)  # Emitted when alias is saved
    alias_cancelled = pyqtSignal()  # Emitted when form is cancelled

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        official_names: Optional[List[str]] = None,
    ) -> None:
        super().__init__(parent)

        # Form data
        self._current_alias: Optional[Dict[str, Any]] = None
        self._is_edit_mode = False
        self._official_names = official_names or []

        # Set up the UI
        self._setup_ui()
        self._setup_connections()
        self._setup_validation()

    def _setup_ui(self) -> None:
        """Set up the user interface components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Title
        self.title_label = QLabel("Add New Business Alias")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(14)
        self.title_label.setFont(title_font)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title_label)

        # Form group
        form_group = QGroupBox("Alias Information")
        form_layout = QFormLayout(form_group)
        form_layout.setSpacing(10)

        # Company Name field
        self.company_name_edit = QLineEdit()
        self.company_name_edit.setPlaceholderText(
            "Enter company name as it appears on invoices"
        )
        self.company_name_edit.setToolTip(
            "The company name that appears on invoices (e.g., 'Hydro Quebec')"
        )
        self.company_name_edit.setMinimumWidth(300)  # 50% longer than default
        form_layout.addRow("Company Name:", self.company_name_edit)

        # Canonical Name field
        self.canonical_name_combo = QComboBox()
        self.canonical_name_combo.setEditable(False)
        self.canonical_name_combo.setToolTip(
            "Select the official or canonical name for the company (e.g., 'HYDRO-QUÉBEC')"
        )
        self.canonical_name_combo.addItems(self._official_names)
        self.canonical_name_combo.setMinimumWidth(
            300
        )  # Same size as company name field
        form_layout.addRow("Canonical Name:", self.canonical_name_combo)

        # Match Type field
        self.match_type_combo = QComboBox()
        self.match_type_combo.addItems(["Exact", "Variant", "Fuzzy"])
        self.match_type_combo.setToolTip("Type of matching to use for this alias")
        form_layout.addRow("Match Type:", self.match_type_combo)

        # Options group
        options_group = QGroupBox("Matching Options")
        options_layout = QVBoxLayout(options_group)

        # Fuzzy matching checkbox
        self.fuzzy_matching_check = QCheckBox("Enable fuzzy matching")
        self.fuzzy_matching_check.setToolTip(
            "Allow approximate string matching for this alias"
        )
        self.fuzzy_matching_check.setChecked(True)
        options_layout.addWidget(self.fuzzy_matching_check)

        # Case sensitive checkbox
        self.case_sensitive_check = QCheckBox("Case sensitive matching")
        self.case_sensitive_check.setToolTip("Require exact case matching")
        self.case_sensitive_check.setChecked(False)
        options_layout.addWidget(self.case_sensitive_check)

        layout.addWidget(form_group)
        layout.addWidget(options_group)

        # Preview section
        preview_group = QGroupBox("Preview")
        preview_layout = QVBoxLayout(preview_group)

        self.preview_label = QLabel("Preview will appear here when you enter data...")
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        preview_layout.addWidget(self.preview_label)

        layout.addWidget(preview_group)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.cancel_button = QPushButton("Cancel")
        button_layout.addWidget(self.cancel_button)

        self.save_button = QPushButton("Save Alias")
        self.save_button.setEnabled(False)
        self.save_button.setDefault(True)  # Make save button the default
        button_layout.addWidget(self.save_button)

        layout.addLayout(button_layout)

    def _setup_connections(self) -> None:
        """Set up signal connections."""
        # Text change connections for real-time preview
        self.company_name_edit.textChanged.connect(self._update_preview)
        self.canonical_name_combo.currentTextChanged.connect(self._update_preview)
        self.match_type_combo.currentTextChanged.connect(self._update_preview)

        # Button connections
        self.save_button.clicked.connect(self._on_save)
        self.cancel_button.clicked.connect(self._on_cancel)

        # Validation connections
        self.company_name_edit.textChanged.connect(self._validate_form)
        self.canonical_name_combo.currentTextChanged.connect(self._validate_form)

    def _setup_validation(self) -> None:
        """Set up form validation."""
        # Add validation styles
        self._valid_style = ""
        self._invalid_style = ""
        self._normal_style = ""

    def _update_preview(self) -> None:
        """Update the preview section with current form data."""
        company_name = self.company_name_edit.text().strip()
        canonical_name = self.canonical_name_combo.currentText().strip()
        match_type = self.match_type_combo.currentText()

        if company_name and canonical_name:
            preview_text = f'"{company_name}" → "{canonical_name}"\n'
            preview_text += f"Match Type: {match_type}\n"

            if self.fuzzy_matching_check.isChecked():
                preview_text += "✓ Fuzzy matching enabled\n"
            if self.case_sensitive_check.isChecked():
                preview_text += "✓ Case sensitive matching\n"

            self.preview_label.setText(preview_text)
        else:
            self.preview_label.setText(
                "Preview will appear here when you enter data..."
            )

    def _validate_form(self) -> None:
        """Validate the form and enable/disable save button."""
        company_name = self.company_name_edit.text().strip()
        canonical_name = self.canonical_name_combo.currentText().strip()

        is_valid = bool(company_name and canonical_name)

        # Update field styles
        if company_name:
            self.company_name_edit.setStyleSheet(self._valid_style)
        elif company_name == "":
            self.company_name_edit.setStyleSheet(self._normal_style)
        else:
            self.company_name_edit.setStyleSheet(self._invalid_style)

        if canonical_name:
            self.canonical_name_combo.setStyleSheet(self._valid_style)
        elif canonical_name == "":
            self.canonical_name_combo.setStyleSheet(self._normal_style)
        else:
            self.canonical_name_combo.setStyleSheet(self._invalid_style)

        # Enable/disable save button
        self.save_button.setEnabled(is_valid)
        
        # Ensure save button remains the default when valid
        if is_valid:
            self.save_button.setDefault(True)
            self.cancel_button.setDefault(False)

    def _on_save(self) -> None:
        """Handle save button click."""
        if not self._validate_form_data():
            return

        alias_data = self._get_form_data()
        self.alias_saved.emit(alias_data)

    def _on_cancel(self) -> None:
        """Handle cancel button click."""
        self.alias_cancelled.emit()

    def _validate_form_data(self) -> bool:
        """Validate form data and show error messages if needed."""
        company_name = self.company_name_edit.text().strip()
        canonical_name = self.canonical_name_combo.currentText().strip()

        errors = []

        if not company_name:
            errors.append("Company name is required")
        elif len(company_name) < 2:
            errors.append("Company name must be at least 2 characters")

        if not canonical_name:
            errors.append("Canonical name is required")
        elif len(canonical_name) < 2:
            errors.append("Canonical name must be at least 2 characters")

        if errors:
            error_message = "Please fix the following errors:\n\n" + "\n".join(
                f"• {error}" for error in errors
            )
            QMessageBox.warning(self, "Validation Error", error_message)
            return False

        return True

    def _get_form_data(self) -> Dict[str, Any]:
        """Get the current form data as a dictionary."""
        return {
            "company_name": self.company_name_edit.text().strip(),
            "canonical_name": self.canonical_name_combo.currentText().strip(),
            "match_type": self.match_type_combo.currentText(),
            "fuzzy_matching": self.fuzzy_matching_check.isChecked(),
            "case_sensitive": self.case_sensitive_check.isChecked(),
            "usage_count": 0,
            "last_used": "",
            "created_date": "",  # Will be set by the manager
        }

    def load_alias(self, alias_data: Dict[str, Any]) -> None:
        """Load alias data into the form for editing."""
        self._is_edit_mode = True
        self._current_alias = alias_data.copy()
        self.title_label.setText("Edit Business Alias")
        self.company_name_edit.setText(alias_data.get("company_name", ""))
        canonical_name = alias_data.get("canonical_name", "")
        idx = self.canonical_name_combo.findText(canonical_name)
        if idx >= 0:
            self.canonical_name_combo.setCurrentIndex(idx)
        else:
            self.canonical_name_combo.setCurrentIndex(0)
        match_type = alias_data.get("match_type", "Exact")
        idx = self.match_type_combo.findText(match_type)
        if idx >= 0:
            self.match_type_combo.setCurrentIndex(idx)
        self.fuzzy_matching_check.setChecked(alias_data.get("fuzzy_matching", True))
        self.case_sensitive_check.setChecked(alias_data.get("case_sensitive", False))
        self._update_preview()
        self._validate_form()

    def clear_form(self) -> None:
        """Clear the form and reset to add mode."""
        self._current_alias = None
        self._is_edit_mode = False

        # Reset title
        self.title_label.setText("Add New Business Alias")

        # Clear form fields
        self.company_name_edit.clear()
        self.canonical_name_combo.setCurrentIndex(0)
        self.fuzzy_matching_check.setChecked(True)
        self.case_sensitive_check.setChecked(False)

        # Reset styles
        self.company_name_edit.setStyleSheet(self._normal_style)
        self.canonical_name_combo.setStyleSheet(self._normal_style)

        # Update preview
        self._update_preview()

    def is_edit_mode(self) -> bool:
        """Check if the form is in edit mode."""
        return self._is_edit_mode

    def get_current_alias(self) -> Optional[Dict[str, Any]]:
        """Get the currently loaded alias data."""
        return self._current_alias

    def set_official_names(self, official_names: List[str]) -> None:
        """Set the list of official names for the canonical name dropdown."""
        self._official_names = official_names
        self.canonical_name_combo.clear()
        self.canonical_name_combo.addItems(self._official_names)
