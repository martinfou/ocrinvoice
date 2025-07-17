"""
Data Panel Widget

Displays extracted data from PDF invoices in an editable format.
"""

from typing import Dict, Any, List
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QHBoxLayout,
    QPushButton,
    QComboBox,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor
from .delegates import DateEditDelegate, BusinessComboDelegate


class EditableTableWidget(QTableWidget):
    """Custom table widget that handles editing state properly."""

    def __init__(self, parent=None):
        super().__init__(parent)

    def editItem(self, item):
        """Override editItem to ensure proper text visibility during editing."""
        # Set the item's background to a light color and text to dark for editing
        item.setBackground(QColor("#f8f9fa"))
        item.setForeground(QColor("#2c3e50"))
        super().editItem(item)


class DataPanelWidget(QWidget):
    """Widget for displaying and editing extracted invoice data."""

    # Signal emitted when rename is requested
    rename_requested = pyqtSignal()

    # Signal emitted when data is changed by user
    data_changed = pyqtSignal(dict)  # Emits updated data dictionary

    # Signal emitted when project selection changes
    project_changed = pyqtSignal(str)  # Emits selected project name

    def __init__(self, parent=None, business_names=None) -> None:
        super().__init__(parent)
        self.current_data: Dict[str, Any] = {}
        self.business_names = business_names or []
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Set up the user interface."""
        layout = QVBoxLayout(self)

        # Title
        title = QLabel("📄 Extracted Data (Double-click values to edit)")
        title.setToolTip(
            "Values in the table are editable. Double-click any value to edit it "
            "and see real-time file name updates."
        )
        layout.addWidget(title)

        # Project selection section
        project_layout = QHBoxLayout()

        project_label = QLabel("📁 Project:")
        project_layout.addWidget(project_label)

        self.project_combo = QComboBox()
        self.project_combo.setPlaceholderText("Select a project...")
        self.project_combo.currentTextChanged.connect(self._on_project_changed)
        project_layout.addWidget(self.project_combo)

        project_layout.addStretch()
        layout.addLayout(project_layout)

        # Data table
        self.data_table = EditableTableWidget()
        self.data_table.setColumnCount(3)
        self.data_table.setHorizontalHeaderLabels(["Field", "Value", "Confidence"])

        # Set table properties with better styling
        header = self.data_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)

        self.data_table.setAlternatingRowColors(True)
        self.data_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

        # Make the table editable
        self.data_table.setEditTriggers(
            QTableWidget.EditTrigger.DoubleClicked
            | QTableWidget.EditTrigger.EditKeyPressed
        )

        # Connect cell changed signal
        self.data_table.itemChanged.connect(self._on_cell_changed)

        # Connect editing signals to handle visual feedback
        self.data_table.itemSelectionChanged.connect(self._on_selection_changed)

        layout.addWidget(self.data_table)

        # Assign delegates
        self.date_delegate = DateEditDelegate(self.data_table)
        self.data_table.setItemDelegateForRow(2, self.date_delegate)
        self.business_delegate = BusinessComboDelegate(self.business_names, self.data_table)
        self.data_table.setItemDelegateForRow(0, self.business_delegate)

        # Action buttons
        button_layout = QHBoxLayout()

        self.export_btn = QPushButton("💾 Export Data")
        self.export_btn.setEnabled(False)
        self.export_btn.setToolTip("Export extracted data to JSON/CSV format")
        self.export_btn.clicked.connect(self._export_data)
        button_layout.addWidget(self.export_btn)

        self.clear_btn = QPushButton("🗑️ Clear Data")
        self.clear_btn.setEnabled(False)
        self.clear_btn.setToolTip("Clear all extracted data")
        self.clear_btn.clicked.connect(self.clear_data)
        button_layout.addWidget(self.clear_btn)

        # Add rename button
        self.rename_btn = QPushButton("📝 Rename File")
        self.rename_btn.setEnabled(False)
        self.rename_btn.setToolTip("Rename the current file using the template")
        self.rename_btn.clicked.connect(self._on_rename_requested)
        button_layout.addWidget(self.rename_btn)

        button_layout.addStretch()
        layout.addLayout(button_layout)

        # Placeholder text
        self._show_placeholder()

    def _on_project_changed(self, project_name: str) -> None:
        """Handle project selection change."""
        if project_name:
            self.project_changed.emit(project_name)

    def update_projects(self, projects: List[str]) -> None:
        """Update the project dropdown with available projects."""
        self.project_combo.clear()
        self.project_combo.addItem("")  # Empty option
        self.project_combo.addItems(projects)

    def set_selected_project(self, project_name: str) -> None:
        """Set the selected project in the dropdown."""
        index = self.project_combo.findText(project_name)
        if index >= 0:
            self.project_combo.setCurrentIndex(index)

    def get_selected_project(self) -> str:
        """Get the currently selected project."""
        return self.project_combo.currentText()

    def _on_cell_changed(self, item: QTableWidgetItem) -> None:
        """Handle cell content changes in the data table."""
        if not self.current_data:
            return

        # Only handle changes to the Value column (column 1)
        if item.column() != 1:
            return

        row = item.row()
        field_name = self.data_table.item(row, 0).text()

        # Map display names back to field keys
        field_mapping = {
            "Company Name": "company",
            "Total Amount": "total",
            "Invoice Date": "date",
            "Invoice Number": "invoice_number",
            "Parser Type": "parser_type",
            "Valid": "is_valid",
            "Overall Confidence": "confidence",
        }

        field_key = field_mapping.get(field_name)
        if not field_key:
            return

        new_value = item.text()

        # Process the value based on field type
        if field_key == "total":
            # Remove currency symbols and convert to float
            try:
                # Remove $ and other currency symbols
                clean_value = new_value.replace("$", "").replace(",", "").strip()
                if clean_value:
                    float_value = float(clean_value)
                    self.current_data[field_key] = float_value
                else:
                    self.current_data[field_key] = None
            except ValueError:
                # Keep as string if not a valid number
                self.current_data[field_key] = new_value
        elif field_key == "is_valid":
            # Convert to boolean
            self.current_data[field_key] = new_value.lower() in ["yes", "true", "1"]
        elif field_key == "confidence":
            # Remove % and convert to float
            try:
                clean_value = new_value.replace("%", "").strip()
                if clean_value:
                    float_value = float(clean_value) / 100.0
                    self.current_data[field_key] = float_value
                else:
                    self.current_data[field_key] = None
            except ValueError:
                # Keep as string if not a valid number
                self.current_data[field_key] = new_value
        else:
            # Keep as string for other fields
            self.current_data[field_key] = new_value

        # Emit the updated data
        self.data_changed.emit(self.current_data.copy())

    def _on_selection_changed(self) -> None:
        """Handle selection changes to ensure proper text visibility."""
        # Ensure all editable items have proper text color
        for row in range(self.data_table.rowCount()):
            for col in range(self.data_table.columnCount()):
                item = self.data_table.item(row, col)
                if item and col == 1:  # Value column
                    pass

    def _show_placeholder(self) -> None:
        """Show placeholder text when no data is available."""
        self.data_table.setRowCount(1)
        self.data_table.setColumnCount(3)
        self.data_table.setHorizontalHeaderLabels(["Field", "Value", "Confidence"])
        placeholder_item = QTableWidgetItem("No data extracted yet")
        placeholder_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.data_table.setItem(0, 0, placeholder_item)
        self.data_table.setSpan(0, 0, 1, 3)

    def update_data(self, data: Dict[str, Any]) -> None:
        """Update the displayed data."""
        if not data:
            self._show_placeholder()
            self.export_btn.setEnabled(False)
            self.clear_btn.setEnabled(False)
            self.rename_btn.setEnabled(False)
            self.current_data = {}
            return

        # Store the current data
        self.current_data = data.copy()

        # Clear existing data and spans
        self.data_table.clear()
        # Clear any existing spans by setting row count to 0 first
        self.data_table.setRowCount(0)
        # Ensure table has proper column count and headers
        self.data_table.setColumnCount(3)
        self.data_table.setHorizontalHeaderLabels(["Field", "Value", "Confidence"])

        # Define the fields to display and their display names
        fields = [
            ("company", "Company Name"),
            ("total", "Total Amount"),
            ("date", "Invoice Date"),
            ("invoice_number", "Invoice Number"),
            ("parser_type", "Parser Type"),
            ("is_valid", "Valid"),
            ("confidence", "Overall Confidence"),
        ]

        # Set up table
        self.data_table.setRowCount(len(fields))

        for row, (field_key, display_name) in enumerate(fields):
            # Field name
            field_item = QTableWidgetItem(display_name)
            field_item.setFont(QFont("Arial", 9, QFont.Weight.Bold))
            field_item.setFlags(
                field_item.flags() & ~Qt.ItemFlag.ItemIsEditable
            )  # Make field name non-editable
            self.data_table.setItem(row, 0, field_item)

            # Value
            raw_value = data.get(field_key, "")

            # Process the value based on field type
            if field_key == "company":
                if raw_value and raw_value != "Unknown":
                    # Improve company name display
                    if isinstance(raw_value, str):
                        value = raw_value.title()  # Capitalize properly
                    else:
                        value = str(raw_value).title()
                else:
                    value = "Not extracted"
            elif field_key == "total" and raw_value:
                value = (
                    f"${raw_value:.2f}"
                    if isinstance(raw_value, (int, float))
                    else str(raw_value)
                )
            elif field_key == "is_valid":
                value = "Yes" if raw_value else "No"
            elif field_key == "confidence" and raw_value:
                if isinstance(raw_value, (int, float)):
                    value = f"{raw_value:.1%}"
                else:
                    value = str(raw_value)
            else:
                value = str(raw_value) if raw_value else "Not extracted"

            # Set value - make it editable
            value_item = QTableWidgetItem(value)
            value_item.setFlags(value_item.flags() | Qt.ItemFlag.ItemIsEditable)
            self.data_table.setItem(row, 1, value_item)

            # Confidence indicator (if available) - make non-editable
            if field_key in ["company", "total", "date", "invoice_number"]:
                confidence_key = f"{field_key}_confidence"
                confidence_value = data.get(confidence_key, 0)

                if confidence_value:
                    if isinstance(confidence_value, (int, float)):
                        confidence_text = f"{confidence_value:.1%}"
                        # Color code based on confidence
                        if confidence_value >= 0.8:
                            confidence_item = QTableWidgetItem("🟢 " + confidence_text)
                        elif confidence_value >= 0.6:
                            confidence_item = QTableWidgetItem("🟡 " + confidence_text)
                        else:
                            confidence_item = QTableWidgetItem("🔴 " + confidence_text)
                    else:
                        confidence_item = QTableWidgetItem(str(confidence_value))
                else:
                    confidence_item = QTableWidgetItem("N/A")

                confidence_item.setFlags(
                    confidence_item.flags() & ~Qt.ItemFlag.ItemIsEditable
                )
                self.data_table.setItem(row, 2, confidence_item)
            else:
                # For non-confidence fields, show empty or N/A
                confidence_item = QTableWidgetItem("")
                confidence_item.setFlags(
                    confidence_item.flags() & ~Qt.ItemFlag.ItemIsEditable
                )
                self.data_table.setItem(row, 2, confidence_item)

        # Enable buttons
        self.export_btn.setEnabled(True)
        self.clear_btn.setEnabled(True)
        self.rename_btn.setEnabled(True)

    def clear_data(self) -> None:
        """Clear the displayed data."""
        self._show_placeholder()
        self.export_btn.setEnabled(False)
        self.clear_btn.setEnabled(False)
        self.rename_btn.setEnabled(False)
        self.current_data = {}

    def _export_data(self) -> None:
        """Export the current data (placeholder for now)."""
        # TODO: Implement export functionality
        pass

    def _on_rename_requested(self) -> None:
        """Handle rename button click."""
        self.rename_requested.emit()
