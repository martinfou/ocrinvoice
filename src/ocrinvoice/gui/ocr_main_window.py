"""
OCR Main Window

Main application window for the OCR Invoice Parser GUI.
"""

import sys
from typing import Optional
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QVBoxLayout, QWidget,
    QPushButton, QFileDialog, QMessageBox, QLabel, QHBoxLayout,
    QSplitter, QFrame, QComboBox, QLineEdit, QStatusBar, QCloseEvent
)
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QAction, QKeySequence

from .widgets.pdf_preview import PDFPreviewWidget
from .widgets.data_panel import DataPanelWidget


class OCRMainWindow(QMainWindow):
    """
    Main application window for the OCR Invoice Parser GUI.

    Provides the foundation for the OCR GUI application with:
    - Basic navigation framework using tabs
    - Status bar for user feedback
    - Menu system for application actions
    - Integration points for future OCR functionality
    """

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        # Window setup
        self.setWindowTitle("OCR Invoice Parser")
        self.setMinimumSize(1000, 700)
        self.resize(1200, 800)

        # Initialize UI components
        self._setup_ui()
        self._setup_menu_bar()
        self._setup_status_bar()
        self._setup_connections()

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

        # Create placeholder tabs for Sprint 0
        self._create_single_pdf_tab()
        self._create_settings_tab()

    def _create_single_pdf_tab(self) -> None:
        """Create the single PDF processing tab (Sprint 1)."""
        single_pdf_widget = QWidget()
        layout = QVBoxLayout(single_pdf_widget)

        # Create file selection area
        file_layout = QHBoxLayout()
        self.select_pdf_btn = QPushButton("Select PDF")
        self.select_pdf_btn.clicked.connect(self._on_select_pdf)
        file_layout.addWidget(self.select_pdf_btn)
        
        # Add drag and drop area
        self.drop_area = QLabel("Drag and drop PDF files here")
        self.drop_area.setStyleSheet(
            "border: 2px dashed #ccc; padding: 20px; background: #f9f9f9;"
        )
        self.drop_area.setAlignment(Qt.AlignmentFlag.AlignCenter)
        file_layout.addWidget(self.drop_area)

        # Main content area: PDF preview and data panel side by side
        content_layout = QHBoxLayout()
        # PDF preview placeholder
        self.pdf_preview = PDFPreviewWidget()
        content_layout.addWidget(self.pdf_preview, 2)
        # Data panel placeholder
        self.data_panel = DataPanelWidget()
        content_layout.addWidget(self.data_panel, 1)
        layout.addLayout(content_layout)

        self.tab_widget.addTab(single_pdf_widget, "Single PDF")

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
        """Handle PDF file selection with error handling."""
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Select PDF File", "", "PDF Files (*.pdf)"
            )
            if file_path:
                # Load PDF in preview widget
                if self.pdf_preview.load_pdf(file_path):
                    self.status_bar.showMessage(f"Loaded PDF: {file_path}")
                    self._show_success_message("PDF loaded successfully")
                else:
                    self._show_error_message("Failed to load PDF file")
        except Exception as e:
            self._show_error_message(f"Error selecting PDF file: {str(e)}")

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
