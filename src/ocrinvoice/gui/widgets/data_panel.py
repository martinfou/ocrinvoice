"""
Data Panel Widget

Displays extracted data from PDF invoices in an editable format.
"""

from typing import Dict, Any
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QHBoxLayout,
    QPushButton,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont


class DataPanelWidget(QWidget):
    """Widget for displaying and editing extracted invoice data."""

    # Signal emitted when rename is requested
    rename_requested = pyqtSignal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Set up the user interface."""
        layout = QVBoxLayout(self)

        # Title with unified blue/gray theme
        title = QLabel("📄 Extracted Data")
        title.setStyleSheet(
            "font-size: 16px; font-weight: bold; margin-bottom: 15px; "
            "color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 5px;"
        )
        layout.addWidget(title)

        # Data table
        self.data_table = QTableWidget()
        self.data_table.setColumnCount(3)
        self.data_table.setHorizontalHeaderLabels(["Field", "Value", "Confidence"])

        # Set table properties with better styling
        header = self.data_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)

        self.data_table.setAlternatingRowColors(True)
        self.data_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        
        # Apply unified blue/gray theme to the table
        self.data_table.setStyleSheet(
            "QTableWidget { "
            "background-color: white; "
            "gridline-color: #ecf0f1; "
            "border: 1px solid #bdc3c7; "
            "border-radius: 4px; "
            "}"
            "QTableWidget::item { "
            "padding: 8px; "
            "border-bottom: 1px solid #ecf0f1; "
            "}"
            "QTableWidget::item:selected { "
            "background-color: #3498db; "
            "color: white; "
            "}"
            "QHeaderView::section { "
            "background-color: #34495e; "
            "color: white; "
            "padding: 8px; "
            "border: none; "
            "font-weight: bold; "
            "}"
        )

        layout.addWidget(self.data_table)

        # Action buttons with unified blue/gray theme
        button_layout = QHBoxLayout()

        self.export_btn = QPushButton("💾 Export Data")
        self.export_btn.setEnabled(False)
        self.export_btn.setToolTip("Export extracted data to JSON/CSV format")
        self.export_btn.clicked.connect(self._export_data)
        self.export_btn.setStyleSheet(
            "QPushButton { background-color: #3498db; color: white; border: none; "
            "padding: 8px 16px; border-radius: 4px; font-weight: bold; }"
            "QPushButton:hover { background-color: #2980b9; }"
            "QPushButton:disabled { background-color: #bdc3c7; color: #7f8c8d; }"
        )
        button_layout.addWidget(self.export_btn)

        self.clear_btn = QPushButton("🗑️ Clear Data")
        self.clear_btn.setEnabled(False)
        self.clear_btn.setToolTip("Clear all extracted data")
        self.clear_btn.clicked.connect(self.clear_data)
        self.clear_btn.setStyleSheet(
            "QPushButton { background-color: #e74c3c; color: white; border: none; "
            "padding: 8px 16px; border-radius: 4px; font-weight: bold; }"
            "QPushButton:hover { background-color: #c0392b; }"
            "QPushButton:disabled { background-color: #bdc3c7; color: #7f8c8d; }"
        )
        button_layout.addWidget(self.clear_btn)

        # Add rename button
        self.rename_btn = QPushButton("📝 Rename File")
        self.rename_btn.setEnabled(False)
        self.rename_btn.setToolTip("Rename the current file using the template")
        self.rename_btn.clicked.connect(self._on_rename_requested)
        self.rename_btn.setStyleSheet(
            "QPushButton { background-color: #5dade2; color: white; border: none; "
            "padding: 8px 16px; border-radius: 4px; font-weight: bold; }"
            "QPushButton:hover { background-color: #3498db; }"
            "QPushButton:disabled { background-color: #bdc3c7; color: #7f8c8d; }"
        )
        button_layout.addWidget(self.rename_btn)

        button_layout.addStretch()
        layout.addLayout(button_layout)

        # Placeholder text
        self._show_placeholder()

    def _show_placeholder(self) -> None:
        """Show placeholder text when no data is available."""
        self.data_table.setRowCount(1)
        self.data_table.setColumnCount(3)
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
            return

        # Debug: Print the data being processed
        print(f"[DEBUG] DataPanel updating with data: {data}")

        # Clear existing data and spans
        self.data_table.clear()
        # Clear any existing spans by setting row count to 0 first
        self.data_table.setRowCount(0)
        # Ensure table has proper column count
        self.data_table.setColumnCount(3)

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
            self.data_table.setItem(row, 0, field_item)

            # Value
            raw_value = data.get(field_key, "")

            # Debug: Print each field value
            print(f"[DEBUG] Field '{field_key}': {raw_value} (type: {type(raw_value)})")

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
                value = (
                    f"{raw_value:.1%}"
                    if isinstance(raw_value, (int, float))
                    else str(raw_value)
                )
            else:
                value = str(raw_value) if raw_value else "Not extracted"

            # Create and set the value item
            value_item = QTableWidgetItem(value)
            self.data_table.setItem(row, 1, value_item)

            # Confidence (placeholder for now)
            confidence_item = QTableWidgetItem("N/A")
            confidence_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
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

    def _export_data(self) -> None:
        """Export the current data (placeholder for now)."""
        # TODO: Implement export functionality
        pass

    def _on_rename_requested(self) -> None:
        """Handle rename button click."""
        self.rename_requested.emit()
