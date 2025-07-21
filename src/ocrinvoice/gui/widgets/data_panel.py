"""
Data Panel Widget

Displays extracted data from PDF invoices in an editable format.
"""

import re
from typing import Dict, Any, List, Optional
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QPushButton,
    QLabel,
    QComboBox,
    QLineEdit,
    QCompleter,
    QFileDialog,
    QMessageBox,
    QProgressBar,
    QFrame,
    QApplication,
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QColor, QFont, QPalette

from ocrinvoice.business.business_mapping_manager import BusinessMappingManager
from .delegates import (
    BusinessComboDelegate,
    CategoryComboDelegate,
    DateEditDelegate,
)


class EditableComboBox(QComboBox):
    """
    A QComboBox that allows both selection from dropdown and typing new values.
    Provides autocomplete functionality for existing items.
    """
    
    # Signal emitted when a new item is added
    item_added = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setEditable(True)
        self.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        
        # Set up completer for autocomplete
        self.completer = QCompleter(self)
        self.completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self.setCompleter(self.completer)
        
        # Track if we're currently editing to avoid adding on every keystroke
        self._is_editing = False
        self._last_added_text = ""
        
        # Connect signals
        self.lineEdit().textChanged.connect(self._on_text_changed)
        self.lineEdit().editingFinished.connect(self._on_editing_finished)
        self.lineEdit().returnPressed.connect(self._on_return_pressed)
        
    def _on_text_changed(self, text: str) -> None:
        """Handle text changes in the combo box."""
        self._is_editing = True
        # Update completer model
        self.completer.setModel(self.model())
        
    def _on_editing_finished(self) -> None:
        """Handle when editing is finished (user loses focus)."""
        self._is_editing = False
        self._try_add_current_text()
        
    def _on_return_pressed(self) -> None:
        """Handle when user presses Enter."""
        self._is_editing = False
        self._try_add_current_text()
        
    def _try_add_current_text(self) -> None:
        """Try to add the current text as a new item if it doesn't exist."""
        current_text = self.currentText().strip()
        if not current_text:
            return
            
        # Avoid adding the same text multiple times
        if current_text == self._last_added_text:
            return
            
        # Check if the text exists in the current items
        existing_items = [self.itemText(i) for i in range(self.count())]
        if current_text not in existing_items:
            # Ask user for confirmation before adding
            self._confirm_add_project(current_text)
            

            
    def update_items(self, items: List[str]) -> None:
        """Update the combo box items while preserving the current selection."""
        current_text = self.currentText()
        
        self.clear()
        self.addItem("")  # Empty option
        self.addItems(items)
        
        # Restore selection if it still exists
        if current_text:
            index = self.findText(current_text)
            if index >= 0:
                self.setCurrentIndex(index)
            else:
                # If the previous selection is no longer available, set the text
                self.setCurrentText(current_text)
        
        # Force the completer to update its model
        self.completer.setModel(self.model())
        
        # Force a repaint to ensure the dropdown shows all items
        self.view().update()
        
    def _confirm_add_project(self, project_name: str) -> None:
        """Ask user for confirmation before adding a new project."""
        from PyQt6.QtWidgets import QMessageBox
        
        # Create confirmation dialog
        reply = QMessageBox.question(
            self,
            "Add New Project",
            f"Do you want to add '{project_name}' as a new project?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes  # Default to Yes for better UX
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # User confirmed, add the project
            self._add_project_confirmed(project_name)
        else:
            # User cancelled, clear the text or revert to previous selection
            self.setCurrentText("")
            # Restore previous selection if available
            if self._last_project_selection and self._last_project_selection in [self.itemText(i) for i in range(self.count())]:
                self.setCurrentText(self._last_project_selection)
                
    def _add_project_confirmed(self, project_name: str) -> None:
        """Add the project after user confirmation."""
        # Add the new item
        self.addItem(project_name)
        self._last_added_text = project_name
        # Emit signal for external handling
        self.item_added.emit(project_name)


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

    # Signal emitted when document type selection changes
    document_type_changed = pyqtSignal(str)  # Emits selected document type

    # Signal emitted when category selection changes
    category_changed = pyqtSignal(str)  # Emits selected category

    # Signal emitted when a new business is added
    business_added = pyqtSignal(str)  # Emits the business name that was added

    def __init__(self, parent=None, business_names=None, category_names=None, mapping_manager=None) -> None:
        super().__init__(parent)
        self.current_data: Dict[str, Any] = {}
        self.business_names = business_names or []
        self.category_names = category_names or []
        # Use shared mapping manager if provided, otherwise create new instance
        self.mapping_manager = mapping_manager or BusinessMappingManager()
        
        # Track last project selection to avoid duplicate signals
        self._last_project_selection = ""
        
        self._setup_ui()
        # Connect businessAdded signal
        self.business_delegate.businessAdded.connect(self._on_business_added)
        # Connect categoryAdded signal
        self.category_delegate.categoryAdded.connect(self._on_category_added)
        # Load categories into combo
        self.update_categories(self.category_names)

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

        # Project and Document Type selection section
        project_layout = QHBoxLayout()

        project_label = QLabel("📁 Project:")
        project_layout.addWidget(project_label)

        # Use the new EditableComboBox for projects
        self.project_combo = EditableComboBox()
        self.project_combo.setPlaceholderText("Select a project or type a new one...")
        # Connect to item_added for new projects
        self.project_combo.item_added.connect(self._on_project_added)
        # Connect to currentIndexChanged for when user selects from dropdown
        self.project_combo.currentIndexChanged.connect(self._on_project_selection_changed)
        project_layout.addWidget(self.project_combo)

        # Add some spacing between project and document type
        project_layout.addSpacing(20)

        document_type_label = QLabel("📄 Document Type:")
        project_layout.addWidget(document_type_label)

        self.document_type_combo = QComboBox()
        self.document_type_combo.addItems(["facture", "relevé", "invoice", "statement"])
        self.document_type_combo.currentTextChanged.connect(
            self._on_document_type_changed
        )
        project_layout.addWidget(self.document_type_combo)

        # Add some spacing between document type and category
        project_layout.addSpacing(20)

        category_label = QLabel("📊 Category:")
        project_layout.addWidget(category_label)

        self.category_combo = QComboBox()
        self.category_combo.setPlaceholderText("Select a category...")
        self.category_combo.currentTextChanged.connect(self._on_category_changed)
        project_layout.addWidget(self.category_combo)

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
        self.business_delegate = BusinessComboDelegate(
            self.business_names, self.data_table
        )
        self.data_table.setItemDelegateForRow(0, self.business_delegate)
        self.category_delegate = CategoryComboDelegate(
            self.category_names, self.data_table
        )
        self.data_table.setItemDelegateForRow(3, self.category_delegate)  # Category field

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
        self.rename_btn.setToolTip("Rename the current PDF file based on extracted data")
        self.rename_btn.clicked.connect(self._on_rename_requested)
        button_layout.addWidget(self.rename_btn)

        button_layout.addStretch()
        layout.addLayout(button_layout)

        # Show placeholder initially
        self._show_placeholder()

    def _on_project_changed(self, project_name: str) -> None:
        """Handle project selection changes."""
        # Emit the project change signal
        self.project_changed.emit(project_name)
        
    def _on_project_selection_changed(self, index: int) -> None:
        """Handle when user selects a project from the dropdown."""
        if index >= 0:
            project_name = self.project_combo.itemText(index)
            # Avoid duplicate signals for the same selection
            if project_name != self._last_project_selection:
                self._last_project_selection = project_name
                # Emit the project change signal
                self.project_changed.emit(project_name)

    def _on_project_added(self, project_name: str) -> None:
        """Handle when a new project is added via the editable combo box."""
        # Update the last selection to avoid duplicate signals
        self._last_project_selection = project_name
        # Emit a signal to notify the main window that a new project was added
        # This will be handled by the main window to update the project manager
        self.project_changed.emit(project_name)

    def _on_document_type_changed(self, document_type: str) -> None:
        """Handle document type selection changes."""
        print(f"🔧 [DOCUMENT TYPE CHANGE] Document type changed to: '{document_type}'")
        # Emit the document type change signal
        self.document_type_changed.emit(document_type)

    def _on_category_changed(self, category: str) -> None:
        """Handle category selection changes."""
        print(f"🔧 [CATEGORY CHANGE] Category changed to: '{category}'")
        # Emit the category change signal
        self.category_changed.emit(category)

    def update_projects(self, projects: List[str]) -> None:
        """Update the project dropdown with available projects."""
        self.project_combo.update_items(projects)
        # Force the combo box to refresh its display
        self.project_combo.view().update()

    def set_selected_project(self, project_name: str) -> None:
        """Set the selected project in the dropdown."""
        self.project_combo.setCurrentText(project_name)

    def get_selected_project(self) -> str:
        """Get the currently selected project."""
        return self.project_combo.currentText()

    def get_selected_document_type(self) -> str:
        """Get the currently selected document type."""
        return self.document_type_combo.currentText()

    def set_selected_document_type(self, document_type: str) -> None:
        """Set the selected document type in the dropdown."""
        index = self.document_type_combo.findText(document_type)
        if index >= 0:
            self.document_type_combo.setCurrentIndex(index)

    def update_categories(self, categories: List[str]) -> None:
        """Update the category dropdown with available categories."""
        self.category_combo.clear()
        self.category_combo.addItem("")  # Empty option
        self.category_combo.addItems(categories)

    def set_selected_category(self, category: str) -> None:
        """Set the selected category in the dropdown."""
        index = self.category_combo.findText(category)
        if index >= 0:
            self.category_combo.setCurrentIndex(index)

    def get_selected_category(self) -> str:
        """Get the currently selected category."""
        return self.category_combo.currentText()

    def _recalculate_confidence(self, field_key: str) -> None:
        """Recalculate confidence for a specific field when its value changes."""
        if not self.current_data:
            return

        # Simple confidence calculation based on value quality
        value = self.current_data.get(field_key)
        if value is None or value == "":
            confidence = 0.0
        else:
            confidence = 0.5  # Base confidence for having a value

            # Field-specific confidence adjustments
            if field_key == "company":
                if len(str(value)) > 2:
                    confidence += 0.3
                # Check if it matches known business names
                if hasattr(self, "business_names") and str(value).lower() in [
                    name.lower() for name in self.business_names
                ]:
                    confidence += 0.2
            elif field_key == "total":
                try:
                    amount = float(str(value).replace("$", "").replace(",", ""))
                    if amount > 0:
                        confidence += 0.3
                    if 0.01 <= amount <= 1000000:  # Reasonable range
                        confidence += 0.1
                except (ValueError, TypeError):
                    pass
            elif field_key == "date":
                # Check if it looks like a valid date format
                if re.match(r"\d{4}-\d{2}-\d{2}", str(value)):
                    confidence += 0.3
                elif re.match(r"\d{1,2}/\d{1,2}/\d{4}", str(value)):
                    confidence += 0.2
            elif field_key == "invoice_number":
                if len(str(value)) >= 4:
                    confidence += 0.2
                if re.search(r"[A-Z]", str(value), re.IGNORECASE):
                    confidence += 0.1
                if re.search(r"\d", str(value)):
                    confidence += 0.1

            confidence = min(confidence, 1.0)  # Cap at 1.0

        # Update the confidence value
        confidence_key = f"{field_key}_confidence"
        self.current_data[confidence_key] = confidence

        # Update the display in the table
        self._update_confidence_display(field_key, confidence)

    def _update_confidence_display(self, field_key: str, confidence: float) -> None:
        """Update the confidence display in the table for a specific field."""
        # Find the row for this field
        field_mapping = {
            "company": "Company Name",
            "total": "Total Amount",
            "date": "Invoice Date",
            "invoice_number": "Invoice Number",
        }

        display_name = field_mapping.get(field_key)
        if not display_name:
            return

        for row in range(self.data_table.rowCount()):
            field_item = self.data_table.item(row, 0)
            if field_item and field_item.text() == display_name:
                # Update the confidence cell
                confidence_item = self.data_table.item(row, 2)
                if confidence_item:
                    if confidence is not None:
                        confidence_text = f"{confidence:.1%}"
                        if confidence >= 0.8:
                            confidence_item.setText("🟢 " + confidence_text)
                        elif confidence >= 0.6:
                            confidence_item.setText("🟡 " + confidence_text)
                        else:
                            confidence_item.setText("🔴 " + confidence_text)
                    else:
                        confidence_item.setText("N/A")
                break

    def _on_cell_changed(self, item: QTableWidgetItem) -> None:
        """Handle cell content changes in the data table."""
        if not self.current_data:
            return

        # Handle changes to the Value column (column 1)
        if item.column() == 1:
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

            new_value = item.text().strip()

            # Process the value based on field type
            if field_key == "company":
                self.current_data[field_key] = new_value
            elif field_key == "date":
                # Keep as string for dates
                self.current_data[field_key] = new_value
            elif field_key == "invoice_number":
                # Keep as string for invoice numbers
                self.current_data[field_key] = new_value
            elif field_key == "total":
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

            # Recalculate confidence for this field
            if field_key in ["company", "total", "date", "invoice_number"]:
                self._recalculate_confidence(field_key)

        # Handle changes to the Confidence column (column 2)
        elif item.column() == 2:
            user_data = item.data(Qt.ItemDataRole.UserRole)
            if user_data and isinstance(user_data, dict):
                confidence_key = user_data.get("confidence_key")
                if confidence_key:
                    new_value = item.text().strip()

                    # Remove emoji and % symbol, then convert to float
                    new_value = (
                        new_value.replace("🟢 ", "")
                        .replace("🟡 ", "")
                        .replace("🔴 ", "")
                        .replace("%", "")
                        .strip()
                    )

                    try:
                        if new_value and new_value.lower() != "n/a":
                            float_value = float(new_value) / 100.0
                            self.current_data[confidence_key] = float_value
                        else:
                            self.current_data[confidence_key] = 0.0
                    except ValueError:
                        # Keep original value if conversion fails
                        pass

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

            # Confidence indicator (if available) - make editable
            if field_key in ["company", "total", "date", "invoice_number"]:
                confidence_key = f"{field_key}_confidence"
                confidence_value = data.get(confidence_key, 0)

                if confidence_value is not None:
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

                # Make confidence editable
                confidence_item.setFlags(
                    confidence_item.flags() | Qt.ItemFlag.ItemIsEditable
                )
                confidence_item.setData(
                    Qt.ItemDataRole.UserRole,
                    {"field": field_key, "confidence_key": confidence_key},
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



    def _on_business_added(self, business_name: str) -> None:
        """Handle a new business being added via the delegate."""
        print(
            f"[DEBUG] DataPanelWidget: Adding new business '{business_name}' to mapping manager."
        )
        # Add the canonical name
        added = self.mapping_manager.add_canonical_name(business_name)
        if added:
            print(
                f"[DEBUG] DataPanelWidget: Successfully added '{business_name}' to mapping manager."
            )
            # Get the business and add a self-referencing keyword
            business = self.mapping_manager.get_business_by_name(business_name)
            if business:
                self.mapping_manager.add_keyword(business["id"], business_name, "exact")  # Changed from add_alias
                print(
                    f"[DEBUG] DataPanelWidget: Added self-referencing keyword mapping for '{business_name}'."
                )
            # Reload business names from mapping manager
            self.business_names = self.mapping_manager.get_all_dropdown_names()
            self.business_delegate.business_list = self.business_names
            self.business_added.emit(business_name) # Emit the new signal
        else:
            print(
                f"[DEBUG] DataPanelWidget: '{business_name}' already exists in mapping manager."
            )

    def _on_category_added(self, category_name: str) -> None:
        """Handle a new category being added via the delegate."""
        print(
            f"[DEBUG] DataPanelWidget: Adding new category '{category_name}' to category list."
        )
        if category_name not in self.category_names:
            self.category_names.append(category_name)
            self.category_delegate.category_list = self.category_names
            print(
                f"[DEBUG] DataPanelWidget: Successfully added '{category_name}' to category list."
            )
        else:
            print(
                f"[DEBUG] DataPanelWidget: '{category_name}' already exists in category list."
            )
