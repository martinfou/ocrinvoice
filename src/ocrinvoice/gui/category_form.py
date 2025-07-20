"""
Category Form Widget

A form widget for adding and editing CRA expense categories in the GUI.
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


class CategoryForm(QWidget):
    """
    Form widget for adding and editing CRA expense categories.

    Provides input fields for:
    - Category Name
    - Description
    - CRA Code
    """

    # Custom signals
    category_saved = pyqtSignal(dict)  # Emitted when category is saved
    form_cancelled = pyqtSignal()  # Emitted when form is cancelled

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_category_id: Optional[str] = None
        self._setup_ui()
        self._setup_connections()

    def _setup_ui(self) -> None:
        """Set up the form UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        # Category Details Group
        details_group = QGroupBox("Category Details")
        details_layout = QVBoxLayout(details_group)

        # Category Name
        name_layout = QVBoxLayout()
        name_label = QLabel("Category Name:")
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText(
            "Enter category name (e.g., Office Supplies)"
        )
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_edit)
        details_layout.addLayout(name_layout)

        # Generated Name Preview
        preview_layout = QVBoxLayout()
        preview_label = QLabel("Generated Name:")
        self.preview_edit = QLineEdit()
        self.preview_edit.setPlaceholderText("Will be generated automatically")
        self.preview_edit.setReadOnly(True)
        self.preview_edit.setStyleSheet("QLineEdit { background-color: #f0f0f0; }")
        preview_layout.addWidget(preview_label)
        preview_layout.addWidget(self.preview_edit)
        details_layout.addLayout(preview_layout)

        # CRA Code
        code_layout = QVBoxLayout()
        code_label = QLabel("CRA Code:")
        self.code_edit = QLineEdit()
        self.code_edit.setPlaceholderText("Enter CRA expense code (e.g., 8520)")
        self.code_edit.setMaximumWidth(200)
        code_layout.addWidget(code_label)
        code_layout.addWidget(self.code_edit)
        details_layout.addLayout(code_layout)

        # Description
        desc_layout = QVBoxLayout()
        desc_label = QLabel("Description:")
        self.desc_edit = QTextEdit()
        self.desc_edit.setPlaceholderText("Enter category description (optional)")
        self.desc_edit.setMaximumHeight(100)
        desc_layout.addWidget(desc_label)
        desc_layout.addWidget(self.desc_edit)
        details_layout.addLayout(desc_layout)

        layout.addWidget(details_group)

        # Help text
        help_text = QLabel(
            "💡 Tip: Use standard CRA expense categories for tax purposes. "
            "Common codes include:\n"
            "• 8811 - Office stationery and supplies\n"
            "• 8523 - Meals and entertainment\n"
            "• 9200 - Travel expenses\n"
            "• 9281 - Motor vehicle expenses\n"
            "• 8860 - Professional fees\n"
            "• 8521 - Advertising\n"
            "• 8690 - Insurance\n"
            "• 9220 - Utilities\n"
            "• 8910 - Rent\n"
            "• 8810 - Office expenses\n"
            "• 8960 - Repairs and maintenance\n"
            "• Each CRA code can only be used once\n"
            "• Category names are automatically generated as: CRA-code-lowercase-words"
        )
        help_text.setWordWrap(True)
        layout.addWidget(help_text)

        # Action Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.cancel_btn = QPushButton("Cancel")

        self.save_btn = QPushButton("Save Category")
        self.save_btn.setDefault(True)  # Make save button the default

        button_layout.addWidget(self.cancel_btn)
        button_layout.addWidget(self.save_btn)
        layout.addLayout(button_layout)

    def _setup_connections(self) -> None:
        """Set up signal connections."""
        self.save_btn.clicked.connect(self._save_category)
        self.cancel_btn.clicked.connect(self._cancel_form)
        self.name_edit.textChanged.connect(self._validate_form)
        self.name_edit.textChanged.connect(self._update_preview)
        self.code_edit.textChanged.connect(self._validate_form)
        self.code_edit.textChanged.connect(self._update_preview)
        self.name_edit.returnPressed.connect(self._save_category)
        self.code_edit.returnPressed.connect(self._save_category)

    def load_category(self, category_data: Dict[str, str]) -> None:
        """
        Load category data into the form for editing.

        Args:
            category_data: Category dictionary with id, name, description, cra_code
        """
        self.current_category_id = category_data.get("id")
        
        # Extract original category name from kebab-case name
        kebab_name = category_data.get("name", "")
        cra_code = category_data.get("cra_code", "")
        
        if kebab_name and cra_code and kebab_name.startswith(f"{cra_code}-"):
            # Extract the words part after the CRA code
            words_part = kebab_name[len(f"{cra_code}-"):]
            # Convert back to readable format (replace hyphens with spaces, title case)
            original_name = words_part.replace('-', ' ').title()
            self.name_edit.setText(original_name)
        else:
            # Fallback to original name if not in expected format
            self.name_edit.setText(category_data.get("name", ""))
        
        self.desc_edit.setPlainText(category_data.get("description", ""))
        self.code_edit.setText(cra_code)
        self._validate_form()
        self._update_preview()

    def clear_form(self) -> None:
        """Clear the form for adding a new category."""
        self.current_category_id = None
        self.name_edit.clear()
        self.desc_edit.clear()
        self.code_edit.clear()
        self.preview_edit.clear()
        self._validate_form()

    def get_category_data(self) -> Dict[str, str]:
        """
        Get the current category data from the form.

        Returns:
            Dictionary with category data
        """
        # Generate the kebab-case name from CRA code and category name
        cra_code = self.code_edit.text().strip()
        category_name = self.name_edit.text().strip()
        generated_name = self._generate_kebab_name(cra_code, category_name)
        
        return {
            "id": self.current_category_id,
            "name": generated_name,  # Use the generated kebab-case name
            "description": self.desc_edit.toPlainText().strip(),
            "cra_code": cra_code,
        }

    def _validate_form(self) -> bool:
        """
        Validate the form data.

        Returns:
            True if form is valid, False otherwise
        """
        name = self.name_edit.text().strip()
        code = self.code_edit.text().strip()
        is_valid = bool(name and code)

        self.save_btn.setEnabled(is_valid)

        # Update save button text based on mode
        if self.current_category_id:
            self.save_btn.setText("Update Category")
        else:
            self.save_btn.setText("Save Category")

        # Ensure save button remains the default when valid
        if is_valid:
            self.save_btn.setDefault(True)
            self.cancel_btn.setDefault(False)

        return is_valid

    def _generate_kebab_name(self, cra_code: str, category_name: str) -> str:
        """
        Generate kebab-case name from CRA code and category name.
        
        Args:
            cra_code: The CRA code (e.g., "8520")
            category_name: The category name (e.g., "Office Supplies")
            
        Returns:
            Kebab-case name (e.g., "8520-office-supplies")
        """
        if not cra_code or not category_name:
            return ""
        
        # Convert category name to lowercase and replace spaces/special chars with hyphens
        import re
        words = re.sub(r'[^\w\s-]', '', category_name.lower())  # Remove special chars except hyphens
        words = re.sub(r'[-\s]+', '-', words)  # Replace spaces and multiple hyphens with single hyphen
        words = words.strip('-')  # Remove leading/trailing hyphens
        
        # Combine CRA code and words
        return f"{cra_code}-{words}"

    def _update_preview(self) -> None:
        """Update the generated name preview."""
        cra_code = self.code_edit.text().strip()
        category_name = self.name_edit.text().strip()
        
        if cra_code and category_name:
            generated_name = self._generate_kebab_name(cra_code, category_name)
            self.preview_edit.setText(generated_name)
        else:
            self.preview_edit.clear()

    def _save_category(self) -> None:
        """Save the category data."""
        if not self._validate_form():
            return

        category_data = self.get_category_data()

        # Validate category name
        name = category_data["name"]
        if not name:
            QMessageBox.warning(
                self,
                "Validation Error",
                "Category name cannot be empty.",
                QMessageBox.StandardButton.Ok,
            )
            self.name_edit.setFocus()
            return

        # Validate CRA code
        code = category_data["cra_code"]
        if not code:
            QMessageBox.warning(
                self,
                "Validation Error",
                "CRA code cannot be empty.",
                QMessageBox.StandardButton.Ok,
            )
            self.code_edit.setFocus()
            return

        # Validate CRA code format (should be numeric)
        if not code.isdigit():
            QMessageBox.warning(
                self,
                "Validation Error",
                "CRA code should be a numeric value.",
                QMessageBox.StandardButton.Ok,
            )
            self.code_edit.setFocus()
            return

        # Emit save signal
        self.category_saved.emit(category_data)

    def _cancel_form(self) -> None:
        """Cancel the form operation."""
        self.form_cancelled.emit()

    def set_focus(self) -> None:
        """Set focus to the name field."""
        self.name_edit.setFocus()
        self.name_edit.selectAll() 