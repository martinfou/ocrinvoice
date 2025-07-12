"""
Data Panel Widget

Displays extracted data from PDF invoices in an editable format.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem


class DataPanelWidget(QWidget):
    """Widget for displaying and editing extracted invoice data."""
    
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._setup_ui()
        
    def _setup_ui(self) -> None:
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Extracted Data")
        title.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(title)
        
        # Data table (placeholder)
        self.data_table = QTableWidget()
        self.data_table.setColumnCount(2)
        self.data_table.setHorizontalHeaderLabels(["Field", "Value"])
        self.data_table.setRowCount(0)
        layout.addWidget(self.data_table)
        
        # Placeholder text
        self.data_table.setPlaceholderText("No data extracted yet")
        
    def update_data(self, data: dict) -> None:
        """Update the displayed data."""
        # TODO: Implement data display logic
        pass
        
    def clear_data(self) -> None:
        """Clear the displayed data."""
        self.data_table.setRowCount(0)
