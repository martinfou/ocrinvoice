"""
OCR Main Window

Main application window for the OCR Invoice Parser GUI.
"""

import sys
from typing import Optional, Dict, Any
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QTabWidget,
    QVBoxLayout,
    QWidget,
    QPushButton,
    QFileDialog,
    QMessageBox,
    QLabel,
    QHBoxLayout,
    QSplitter,
    QFrame,
    QComboBox,
    QLineEdit,
    QStatusBar,
    QProgressBar,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QAction, QKeySequence, QCloseEvent

from .widgets.pdf_preview import PDFPreviewWidget
from .widgets.data_panel import DataPanelWidget
from .widgets.file_naming import FileNamingWidget

# Import OCR parsing functionality
from ..parsers.invoice_parser import InvoiceParser
from ..config import get_config


class OCRProcessingThread(QThread):
    """Background thread for OCR processing to avoid blocking the GUI."""

    # Signals to communicate with the main thread
    processing_started = pyqtSignal()
    processing_finished = pyqtSignal(dict)  # Emits extracted data
    processing_error = pyqtSignal(str)  # Emits error message

    def __init__(self, pdf_path: str, config: Dict[str, Any]):
        super().__init__()
        self.pdf_path = pdf_path
        self.config = config

    def run(self) -> None:
        """Run OCR processing in background thread."""
        try:
            self.processing_started.emit()

            # Initialize parser with config
            parser = InvoiceParser(self.config)

            # Parse the PDF
            result = parser.parse(self.pdf_path)

            # Debug: Check if "rona" is in the raw text
            raw_text = result.get("raw_text", "")
            print(f"[DEBUG] Raw text contains 'rona': {'rona' in raw_text.lower()}")
            print(f"[DEBUG] Raw text contains 'RONA': {'RONA' in raw_text}")
            print(f"[DEBUG] Raw text sample (first 500 chars): {raw_text[:500]}")

            # Emit the result
            self.processing_finished.emit(result)

        except Exception as e:
            self.processing_error.emit(str(e))


class OCRMainWindow(QMainWindow):
    """Main application window for the OCR Invoice Parser GUI."""

    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)

        # Load configuration
        self.config = get_config()

        # Initialize OCR parser
        self.ocr_parser = InvoiceParser(self.config)

        # OCR processing thread
        self.ocr_thread: Optional[OCRProcessingThread] = None

        # Current PDF path
        self.current_pdf_path: Optional[str] = None

        # Extracted data
        self.extracted_data: Optional[Dict[str, Any]] = None

        # Set up the UI
        self._setup_ui()
        self._setup_menu_bar()
        self._setup_status_bar()
        self._setup_connections()

        # Set window properties
        self.setWindowTitle("OCR Invoice Parser")
        self.setGeometry(100, 100, 1200, 800)

    def _setup_ui(self) -> None:
        """Set up the main user interface components."""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(8)

        # Create tab widget for navigation
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.TabPosition.North)
        main_layout.addWidget(self.tab_widget)

        # Create tabs
        self._create_single_pdf_tab()
        self._create_file_naming_tab()
        self._create_settings_tab()

    def _create_single_pdf_tab(self) -> None:
        """Create the Single PDF processing tab."""
        single_pdf_widget = QWidget()
        layout = QVBoxLayout(single_pdf_widget)

        # Create file selection area
        file_layout = QVBoxLayout()

        # Select PDF button
        self.select_pdf_btn = QPushButton("Select PDF")
        self.select_pdf_btn.clicked.connect(self._on_select_pdf)
        file_layout.addWidget(self.select_pdf_btn)

        # Add drag and drop area under the button
        self.drop_area = QLabel("Drag and drop PDF files here")
        self.drop_area.setStyleSheet(
            (
                "border: 2px dashed #ccc; padding: 5px; background: #f9f9f9; "
                "margin-top: 10px;"
            )
        )
        self.drop_area.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.drop_area.setFixedHeight(40)  # Set fixed height to 25% of original size
        file_layout.addWidget(self.drop_area)

        layout.addLayout(file_layout)

        # Add OCR progress bar
        self.ocr_progress = QProgressBar()
        self.ocr_progress.setVisible(False)
        self.ocr_progress.setRange(0, 0)  # Indeterminate progress
        self.ocr_progress.setFormat("Processing PDF with OCR...")
        layout.addWidget(self.ocr_progress)

        # Main content area: PDF preview and data panel side by side
        content_splitter = QSplitter(Qt.Orientation.Horizontal)

        # PDF Preview (left side)
        self.pdf_preview = PDFPreviewWidget()
        content_splitter.addWidget(self.pdf_preview)

        # Data Panel (right side)
        self.data_panel = DataPanelWidget()
        content_splitter.addWidget(self.data_panel)

        # Set initial splitter sizes (60% PDF, 40% data)
        content_splitter.setSizes([600, 400])

        layout.addWidget(content_splitter)

        self.tab_widget.addTab(single_pdf_widget, "Single PDF")

    def _create_file_naming_tab(self) -> None:
        """Create the File Naming tab."""
        # Create file naming widget
        self.file_naming_widget = FileNamingWidget()

        # Update with current config
        self.file_naming_widget.update_config(self.config)

        # Connect template changes to config updates
        self.file_naming_widget.template_changed.connect(self._on_template_changed)

        self.tab_widget.addTab(self.file_naming_widget, "File Naming")

    def _create_settings_tab(self) -> None:
        """Create the settings tab with basic configuration options."""
        settings_widget = QWidget()
        layout = QVBoxLayout(settings_widget)

        # Settings title
        title_label = QLabel("OCR Invoice Parser Settings")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(title_label)

        # OCR Settings Section
        ocr_group = QFrame()
        ocr_group.setFrameShape(QFrame.Shape.StyledPanel)
        ocr_layout = QVBoxLayout(ocr_group)

        ocr_title = QLabel("OCR Settings")
        ocr_title.setStyleSheet("font-size: 14px; font-weight: bold;")
        ocr_layout.addWidget(ocr_title)

        # Language setting
        lang_layout = QHBoxLayout()
        lang_label = QLabel("OCR Language:")
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["eng", "fra", "spa", "deu"])
        self.lang_combo.setCurrentText("eng")
        lang_layout.addWidget(lang_label)
        lang_layout.addWidget(self.lang_combo)
        lang_layout.addStretch()
        ocr_layout.addLayout(lang_layout)

        layout.addWidget(ocr_group)

        # Output Settings Section
        output_group = QFrame()
        output_group.setFrameShape(QFrame.Shape.StyledPanel)
        output_layout = QVBoxLayout(output_group)

        output_title = QLabel("Output Settings")
        output_title.setStyleSheet("font-size: 14px; font-weight: bold;")
        output_layout.addWidget(output_title)

        # Output directory setting
        dir_layout = QHBoxLayout()
        dir_label = QLabel("Output Directory:")
        self.dir_edit = QLineEdit()
        self.dir_edit.setPlaceholderText("Select output directory...")
        dir_btn = QPushButton("Browse...")
        dir_btn.clicked.connect(self._on_select_output_dir)
        dir_layout.addWidget(dir_label)
        dir_layout.addWidget(self.dir_edit)
        dir_layout.addWidget(dir_btn)
        output_layout.addLayout(dir_layout)

        layout.addWidget(output_group)

        # Business Settings Section
        business_group = QFrame()
        business_group.setFrameShape(QFrame.Shape.StyledPanel)
        business_layout = QVBoxLayout(business_group)

        business_title = QLabel("Business Settings")
        business_title.setStyleSheet("font-size: 14px; font-weight: bold;")
        business_layout.addWidget(business_title)

        # Business alias file setting
        alias_layout = QHBoxLayout()
        alias_label = QLabel("Business Alias File:")
        self.alias_edit = QLineEdit()
        self.alias_edit.setPlaceholderText("Path to business alias file...")
        alias_btn = QPushButton("Browse...")
        alias_btn.clicked.connect(self._on_select_alias_file)
        alias_layout.addWidget(alias_label)
        alias_layout.addWidget(self.alias_edit)
        alias_layout.addWidget(alias_btn)
        business_layout.addLayout(alias_layout)

        layout.addWidget(business_group)

        # Save/Cancel buttons
        button_layout = QHBoxLayout()
        save_btn = QPushButton("Save Settings")
        save_btn.clicked.connect(self._on_save_settings)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self._on_cancel_settings)
        button_layout.addStretch()
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)

        self.tab_widget.addTab(settings_widget, "Settings")

    def _setup_menu_bar(self) -> None:
        """Set up the menu bar with basic menu items."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")

        # Exit action
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.setStatusTip("Exit the application")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Help menu
        help_menu = menubar.addMenu("&Help")

        # About action
        about_action = QAction("&About", self)
        about_action.setStatusTip("About OCR Invoice Parser")
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def _setup_status_bar(self) -> None:
        """Set up the status bar for user feedback."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

    def _setup_connections(self) -> None:
        """Set up signal connections."""
        self.tab_widget.currentChanged.connect(self._on_tab_changed)

    def _on_tab_changed(self, index: int) -> None:
        """Handle tab changes."""
        tab_name = self.tab_widget.tabText(index)
        self.status_bar.showMessage(f"Switched to {tab_name} tab")

    def _on_select_pdf(self) -> None:
        """Handle PDF file selection with OCR processing."""
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Select PDF File", "", "PDF Files (*.pdf)"
            )
            if file_path:
                self._load_and_process_pdf(file_path)
        except Exception as e:
            self._show_error_message(f"Error selecting PDF file: {str(e)}")

    def _load_and_process_pdf(self, pdf_path: str) -> None:
        """Load PDF and start OCR processing."""
        try:
            # Load PDF in preview widget
            if self.pdf_preview.load_pdf(pdf_path):
                self.current_pdf_path = pdf_path
                self.status_bar.showMessage(f"Loaded PDF: {pdf_path}")
                self._show_success_message("PDF loaded successfully")

                # Start OCR processing
                self._start_ocr_processing(pdf_path)
            else:
                self._show_error_message("Failed to load PDF file")
        except Exception as e:
            self._show_error_message(f"Error loading PDF: {str(e)}")

    def _start_ocr_processing(self, pdf_path: str) -> None:
        """Start OCR processing in background thread."""
        # Stop any existing OCR thread
        if self.ocr_thread and self.ocr_thread.isRunning():
            self.ocr_thread.terminate()
            self.ocr_thread.wait()

        # Create and start new OCR thread
        self.ocr_thread = OCRProcessingThread(pdf_path, self.config)
        self.ocr_thread.processing_started.connect(self._on_ocr_started)
        self.ocr_thread.processing_finished.connect(self._on_ocr_finished)
        self.ocr_thread.processing_error.connect(self._on_ocr_error)

        self.ocr_thread.start()

    def _on_ocr_started(self) -> None:
        """Handle OCR processing started."""
        self.ocr_progress.setVisible(True)
        self.status_bar.showMessage("Processing PDF with OCR...")
        self.select_pdf_btn.setEnabled(False)

    def _on_ocr_finished(self, extracted_data: Dict[str, Any]) -> None:
        """Handle OCR processing finished successfully."""
        self.ocr_progress.setVisible(False)
        self.select_pdf_btn.setEnabled(True)

        # Store extracted data
        self.extracted_data = extracted_data

        # Debug: Print extracted data
        print(f"[DEBUG] Extracted data: {extracted_data}")
        print(f"[DEBUG] Company field: {extracted_data.get('company', 'NOT_FOUND')}")
        print(f"[DEBUG] Company field type: {type(extracted_data.get('company'))}")
        print(f"[DEBUG] All fields: {list(extracted_data.keys())}")

        # Update data panel
        self.data_panel.update_data(extracted_data)

        # Update file naming widget with extracted data
        if self.current_pdf_path:
            from pathlib import Path

            original_filename = Path(self.current_pdf_path).name
            self.file_naming_widget.update_data(extracted_data, original_filename)

        # Show success message
        company = extracted_data.get("company", "Unknown")
        total = extracted_data.get("total", "Unknown")

        # Improve company name display
        if company and company != "Unknown":
            # Capitalize company name for better display
            company_display = company.title()
        else:
            company_display = "Unknown Company"

        self.status_bar.showMessage(f"OCR completed: {company_display} - ${total}")
        self._show_success_message("OCR processing completed successfully")

    def _on_ocr_error(self, error_message: str) -> None:
        """Handle OCR processing error."""
        self.ocr_progress.setVisible(False)
        self.select_pdf_btn.setEnabled(True)
        self.status_bar.showMessage(f"OCR Error: {error_message}")
        self._show_error_message(f"OCR processing failed: {error_message}")

    def _show_error_message(self, message: str) -> None:
        """Show error message to user."""
        QMessageBox.critical(self, "Error", message)
        self.status_bar.showMessage(f"Error: {message}")

    def _show_success_message(self, message: str) -> None:
        """Show success message to user."""
        self.status_bar.showMessage(message)

    def _on_select_output_dir(self) -> None:
        """Handle output directory selection."""
        dir_path = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if dir_path:
            self.dir_edit.setText(dir_path)

    def _on_select_alias_file(self) -> None:
        """Handle business alias file selection."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Business Alias File", "", "JSON Files (*.json)"
        )
        if file_path:
            self.alias_edit.setText(file_path)

    def _on_save_settings(self) -> None:
        """Handle settings save."""
        # TODO: Implement actual settings saving
        self.status_bar.showMessage("Settings saved successfully")

    def _on_cancel_settings(self) -> None:
        """Handle settings cancel."""
        # TODO: Reset settings to previous values
        self.status_bar.showMessage("Settings changes cancelled")

    def _on_template_changed(self, template: str) -> None:
        """Handle file naming template changes."""
        # Update config with new template
        if "file_management" not in self.config:
            self.config["file_management"] = {}
        self.config["file_management"]["rename_format"] = template
        self.status_bar.showMessage("File naming template updated")

    def _show_about(self) -> None:
        """Show the about dialog."""
        QMessageBox.about(
            self,
            "About OCR Invoice Parser",
            "OCR Invoice Parser GUI\n\n"
            "A desktop application for extracting structured data from PDF invoices "
            "using OCR.\n\n"
            "Version: 1.0.0\n"
            "Development Phase: Sprint 0 - Foundation",
        )

    def closeEvent(self, event: Optional[QCloseEvent]) -> None:
        """Handle application close event."""
        # TODO: Add save prompts and cleanup logic in future sprints
        if event is not None:
            event.accept()


def main() -> None:
    """Main entry point for the OCR GUI application."""
    app = QApplication(sys.argv)
    app.setApplicationName("OCR Invoice Parser")
    app.setApplicationVersion("1.0.0")

    window = OCRMainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
