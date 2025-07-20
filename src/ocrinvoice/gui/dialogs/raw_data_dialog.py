"""
Raw Data Dialog

A modal dialog for displaying the complete raw data structure
extracted from PDF processing, useful for debugging and inspection.
"""

import json
from typing import Dict, Any, Optional
from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QTextEdit,
    QPushButton,
    QLabel,
    QSplitter,
    QTreeWidget,
    QTreeWidgetItem,
    QHeaderView,
    QTabWidget,
    QWidget,
    QFrame,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QTextCursor, QSyntaxHighlighter, QTextCharFormat, QColor


class JSONHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for JSON text."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_formats()
    
    def _setup_formats(self):
        """Set up text formats for different JSON elements."""
        # String format (green)
        self.string_format = QTextCharFormat()
        self.string_format.setForeground(QColor("#008000"))
        self.string_format.setFontWeight(QFont.Weight.Bold)
        
        # Number format (blue)
        self.number_format = QTextCharFormat()
        self.number_format.setForeground(QColor("#0000FF"))
        
        # Boolean format (purple)
        self.boolean_format = QTextCharFormat()
        self.boolean_format.setForeground(QColor("#800080"))
        self.boolean_format.setFontWeight(QFont.Weight.Bold)
        
        # Null format (red)
        self.null_format = QTextCharFormat()
        self.null_format.setForeground(QColor("#FF0000"))
        self.null_format.setFontWeight(QFont.Weight.Bold)
        
        # Key format (dark blue)
        self.key_format = QTextCharFormat()
        self.key_format.setForeground(QColor("#000080"))
        self.key_format.setFontWeight(QFont.Weight.Bold)
    
    def highlightBlock(self, text):
        """Highlight a block of text."""
        import re
        
        # Highlight strings
        string_pattern = r'"[^"]*"'
        for match in re.finditer(string_pattern, text):
            self.setFormat(match.start(), match.end() - match.start(), self.string_format)
        
        # Highlight numbers
        number_pattern = r'\b\d+\.?\d*\b'
        for match in re.finditer(number_pattern, text):
            self.setFormat(match.start(), match.end() - match.start(), self.number_format)
        
        # Highlight booleans
        boolean_pattern = r'\b(true|false)\b'
        for match in re.finditer(boolean_pattern, text, re.IGNORECASE):
            self.setFormat(match.start(), match.end() - match.start(), self.boolean_format)
        
        # Highlight null
        null_pattern = r'\bnull\b'
        for match in re.finditer(null_pattern, text, re.IGNORECASE):
            self.setFormat(match.start(), match.end() - match.start(), self.null_format)
        
        # Highlight keys (strings followed by colon)
        key_pattern = r'"([^"]*)"\s*:'
        for match in re.finditer(key_pattern, text):
            self.setFormat(match.start(1), match.end(1) - match.start(1), self.key_format)


class RawDataDialog(QDialog):
    """Modal dialog for displaying raw extracted data."""
    
    def __init__(self, data: Dict[str, Any], parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.data = data
        self.setWindowTitle("📊 Raw Extracted Data")
        self.setModal(True)
        self.setMinimumSize(800, 600)
        self.setup_ui()
        self.populate_data()
    
    def setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        
        # Header
        header_label = QLabel("📊 Complete Raw Data Structure")
        header_font = QFont()
        header_font.setBold(True)
        header_font.setPointSize(14)
        header_label.setFont(header_font)
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header_label)
        
        # Description
        desc_label = QLabel(
            "This shows the complete data structure extracted from the PDF, "
            "including all fields, confidence values, and metadata."
        )
        desc_label.setWordWrap(True)
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(desc_label)
        
        # Tab widget for different views
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # JSON View Tab
        self.create_json_tab()
        
        # Tree View Tab
        self.create_tree_tab()
        
        # Summary Tab
        self.create_summary_tab()
        
        # Buttons
        button_layout = QHBoxLayout()
        
        copy_btn = QPushButton("📋 Copy JSON")
        copy_btn.setToolTip("Copy the formatted JSON to clipboard")
        copy_btn.clicked.connect(self.copy_json_to_clipboard)
        button_layout.addWidget(copy_btn)
        
        save_btn = QPushButton("💾 Save JSON")
        save_btn.setToolTip("Save the raw data as a JSON file")
        save_btn.clicked.connect(self.save_json_file)
        button_layout.addWidget(save_btn)
        
        button_layout.addStretch()
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
    
    def create_json_tab(self):
        """Create the JSON formatted view tab."""
        json_widget = QWidget()
        json_layout = QVBoxLayout(json_widget)
        
        # JSON text editor
        self.json_text = QTextEdit()
        self.json_text.setReadOnly(True)
        self.json_text.setFont(QFont("Consolas", 10))
        
        # Apply syntax highlighting
        self.json_highlighter = JSONHighlighter(self.json_text.document())
        
        json_layout.addWidget(self.json_text)
        
        self.tab_widget.addTab(json_widget, "📄 JSON View")
    
    def create_tree_tab(self):
        """Create the tree view tab."""
        tree_widget = QWidget()
        tree_layout = QVBoxLayout(tree_widget)
        
        # Tree widget
        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderLabels(["Field", "Value", "Type"])
        self.tree_widget.setAlternatingRowColors(True)
        
        # Set column widths
        header = self.tree_widget.header()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        
        tree_layout.addWidget(self.tree_widget)
        
        self.tab_widget.addTab(tree_widget, "🌳 Tree View")
    
    def create_summary_tab(self):
        """Create the summary view tab."""
        summary_widget = QWidget()
        summary_layout = QVBoxLayout(summary_widget)
        
        # Summary text
        self.summary_text = QTextEdit()
        self.summary_text.setReadOnly(True)
        self.summary_text.setFont(QFont("Arial", 10))
        summary_layout.addWidget(self.summary_text)
        
        self.tab_widget.addTab(summary_widget, "📋 Summary")
    
    def populate_data(self):
        """Populate all views with the data."""
        # Create a copy of data with processed raw_text for display
        display_data = self.data.copy()
        
        # Process raw_text to replace \n with actual line breaks for display
        if "raw_text" in display_data and isinstance(display_data["raw_text"], str):
            # Replace literal \n with actual line breaks for display
            display_data["raw_text"] = display_data["raw_text"].replace("\\n", "\n")
        
        # Populate JSON view with custom formatting for raw_text
        try:
            # Create a custom JSON-like format that shows raw_text with actual line breaks
            json_lines = []
            json_lines.append("{")
            
            for i, (key, value) in enumerate(display_data.items()):
                if key == "raw_text" and isinstance(value, str):
                    # Special formatting for raw_text to show actual line breaks
                    json_lines.append(f'  "{key}": """')
                    json_lines.append(value)
                    json_lines.append('"""')
                else:
                    # Normal JSON formatting for other fields
                    if isinstance(value, str):
                        json_lines.append(f'  "{key}": "{value}"')
                    else:
                        json_lines.append(f'  "{key}": {json.dumps(value, ensure_ascii=False)}')
                
                if i < len(display_data) - 1:
                    json_lines[-1] += ","
            
            json_lines.append("}")
            formatted_json = "\n".join(json_lines)
            self.json_text.setPlainText(formatted_json)
        except Exception as e:
            self.json_text.setPlainText(f"Error formatting JSON: {str(e)}\n\nRaw data: {str(display_data)}")
        
        # Populate tree view
        self.populate_tree_view()
        
        # Populate summary view
        self.populate_summary_view()
    
    def populate_tree_view(self):
        """Populate the tree view with data."""
        self.tree_widget.clear()
        
        # Create a copy of data with processed raw_text for display
        display_data = self.data.copy()
        
        # Process raw_text to replace \n with actual line breaks for display
        if "raw_text" in display_data and isinstance(display_data["raw_text"], str):
            # Replace literal \n with actual line breaks for display
            display_data["raw_text"] = display_data["raw_text"].replace("\\n", "\n")
        
        def add_item(parent, key, value):
            """Recursively add items to the tree."""
            if isinstance(value, dict):
                # Create parent item for dictionary
                item = QTreeWidgetItem(parent)
                item.setText(0, str(key))
                item.setText(1, f"<{len(value)} items>")
                item.setText(2, "dict")
                
                # Add child items
                for k, v in value.items():
                    add_item(item, k, v)
            elif isinstance(value, list):
                # Create parent item for list
                item = QTreeWidgetItem(parent)
                item.setText(0, str(key))
                item.setText(1, f"<{len(value)} items>")
                item.setText(2, "list")
                
                # Add child items
                for i, v in enumerate(value):
                    add_item(item, f"[{i}]", v)
            else:
                # Create leaf item
                item = QTreeWidgetItem(parent)
                item.setText(0, str(key))
                item.setText(1, str(value))
                item.setText(2, type(value).__name__)
        
        # Add root items
        for key, value in display_data.items():
            add_item(self.tree_widget, key, value)
        
        # Expand all items
        self.tree_widget.expandAll()
    
    def populate_summary_view(self):
        """Populate the summary view."""
        summary_lines = []
        
        # Create a copy of data with processed raw_text for display
        display_data = self.data.copy()
        
        # Process raw_text to replace \n with actual line breaks for display
        if "raw_text" in display_data and isinstance(display_data["raw_text"], str):
            # Replace literal \n with actual line breaks for display
            display_data["raw_text"] = display_data["raw_text"].replace("\\n", "\n")
        
        # Basic statistics
        summary_lines.append("📊 DATA SUMMARY")
        summary_lines.append("=" * 50)
        summary_lines.append(f"Total fields: {len(display_data)}")
        summary_lines.append("")
        
        # Main fields
        summary_lines.append("🏢 MAIN FIELDS:")
        main_fields = ["company", "total", "date", "invoice_number"]
        for field in main_fields:
            value = display_data.get(field)
            confidence = display_data.get(f"{field}_confidence")
            if value is not None:
                summary_lines.append(f"  • {field}: {value}")
                if confidence is not None:
                    summary_lines.append(f"    Confidence: {confidence:.1%}")
            else:
                summary_lines.append(f"  • {field}: Not found")
        summary_lines.append("")
        
        # Confidence summary
        confidence_fields = [f for f in display_data.keys() if f.endswith("_confidence")]
        if confidence_fields:
            summary_lines.append("🎯 CONFIDENCE VALUES:")
            for field in confidence_fields:
                confidence = display_data.get(field)
                if confidence is not None:
                    summary_lines.append(f"  • {field}: {confidence:.1%}")
            summary_lines.append("")
        
        # Overall confidence
        overall_confidence = display_data.get("confidence")
        if overall_confidence is not None:
            summary_lines.append(f"📈 OVERALL CONFIDENCE: {overall_confidence:.1%}")
            summary_lines.append("")
        
        # Metadata
        summary_lines.append("📋 METADATA:")
        metadata_fields = ["parser_type", "parsed_at", "is_valid", "extraction_methods"]
        for field in metadata_fields:
            value = display_data.get(field)
            if value is not None:
                summary_lines.append(f"  • {field}: {value}")
        
        # Raw text preview
        raw_text = display_data.get("raw_text", "")
        if raw_text:
            summary_lines.append("")
            summary_lines.append("📄 RAW TEXT PREVIEW:")
            summary_lines.append("-" * 30)
            # Show first 500 characters
            preview = raw_text[:500]
            if len(raw_text) > 500:
                preview += "..."
            summary_lines.append(preview)
        
        self.summary_text.setPlainText("\n".join(summary_lines))
    
    def copy_json_to_clipboard(self):
        """Copy the formatted JSON to clipboard."""
        try:
            formatted_json = json.dumps(self.data, indent=2, ensure_ascii=False)
            clipboard = self.window().windowHandle().screen().grabWindow(0)
            # Use QApplication.clipboard() instead
            from PyQt6.QtWidgets import QApplication
            QApplication.clipboard().setText(formatted_json)
            
            # Show success message
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.information(self, "Copied", "JSON data copied to clipboard!")
        except Exception as e:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Error", f"Failed to copy to clipboard: {str(e)}")
    
    def save_json_file(self):
        """Save the raw data as a JSON file."""
        try:
            from PyQt6.QtWidgets import QFileDialog
            filename, _ = QFileDialog.getSaveFileName(
                self,
                "Save Raw Data",
                "raw_data.json",
                "JSON Files (*.json);;All Files (*)"
            )
            
            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(self.data, f, indent=2, ensure_ascii=False)
                
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.information(self, "Saved", f"Raw data saved to {filename}")
        except Exception as e:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Error", f"Failed to save file: {str(e)}") 