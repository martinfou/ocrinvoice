"""
Main Window for OCR Invoice Parser GUI

The primary application window for the OCR Invoice Parser GUI application.
This is the foundation for Sprint 0 of the OCR GUI development plan.
"""

import sys
from typing import Optional

from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QTabWidget,
    QLabel,
    QStatusBar,
    QMessageBox,
    QApplication,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QKeySequence, QCloseEvent


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
        """Create the single PDF processing tab (placeholder for Sprint 1)."""
        single_pdf_widget = QWidget()
        layout = QVBoxLayout(single_pdf_widget)

        # Placeholder content
        placeholder_label = QLabel("Single PDF Processing")
        placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder_label.setStyleSheet("font-size: 18px; color: #666; margin: 20px;")
        layout.addWidget(placeholder_label)

        info_label = QLabel(
            "This tab will contain PDF selection, preview, and OCR processing "
            "functionality."
        )
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_label.setStyleSheet("color: #888; margin: 10px;")
        layout.addWidget(info_label)

        self.tab_widget.addTab(single_pdf_widget, "Single PDF")

    def _create_settings_tab(self) -> None:
        """Create the settings tab (placeholder for Sprint 1)."""
        settings_widget = QWidget()
        layout = QVBoxLayout(settings_widget)

        # Placeholder content
        placeholder_label = QLabel("Settings")
        placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder_label.setStyleSheet("font-size: 18px; color: #666; margin: 20px;")
        layout.addWidget(placeholder_label)

        info_label = QLabel(
            "This tab will contain application settings "
            "and configuration "
            "options."
        )
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_label.setStyleSheet("color: #888; margin: 10px;")
        layout.addWidget(info_label)

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

    def _show_about(self) -> None:
        """Show the about dialog."""
        QMessageBox.about(
            self,
            "About OCR Invoice Parser",
            "OCR Invoice Parser GUI\n\n"
            "A desktop application for extracting structured data from PDF invoices using OCR.\n\n"
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
