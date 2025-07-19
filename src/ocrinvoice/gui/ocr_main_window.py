"""
OCR Main Window

Main application window for the OCR Invoice Parser GUI.
"""

import sys
import os
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
    QSplashScreen,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QAction, QKeySequence, QCloseEvent, QPixmap, QFont

from ocrinvoice.gui.widgets.pdf_preview import PDFPreviewWidget
from ocrinvoice.gui.widgets.data_panel import DataPanelWidget
from ocrinvoice.gui.widgets.file_naming import FileNamingWidget

# Import OCR parsing functionality
from ocrinvoice.parsers.invoice_parser import InvoiceParser
from ocrinvoice.config import get_config
from ocrinvoice.utils.pdf_metadata_manager import PDFMetadataManager


class OCRProcessingThread(QThread):
    """Background thread for OCR processing to avoid blocking the GUI."""

    # Signals to communicate with the main thread
    processing_started = pyqtSignal()
    processing_finished = pyqtSignal(dict)  # Emits extracted data
    processing_error = pyqtSignal(str)  # Emits error message
    processing_progress = pyqtSignal(int)  # Emits progress percentage

    def __init__(self, pdf_path: str, config: Dict[str, Any]):
        super().__init__()
        self.pdf_path = pdf_path
        self.config = config
        self._is_cancelled = False

    def cancel(self) -> None:
        """Cancel the processing operation."""
        self._is_cancelled = True

    def run(self) -> None:
        """Run OCR processing in background thread."""
        try:
            self.processing_started.emit()
            self.processing_progress.emit(10)

            # Check if cancelled
            if self._is_cancelled:
                return

            # Initialize parser with config
            parser = InvoiceParser(self.config)
            self.processing_progress.emit(30)

            # Check if cancelled
            if self._is_cancelled:
                return

            # Parse the PDF
            result = parser.parse(self.pdf_path)
            self.processing_progress.emit(90)

            # Check if cancelled
            if self._is_cancelled:
                return

            # Clean up any large objects to free memory
            if "raw_text" in result and len(result["raw_text"]) > 10000:
                # Keep only first 1000 chars for debugging if needed
                result["raw_text"] = result["raw_text"][:1000] + "... (truncated)"

            self.processing_progress.emit(100)
            self.processing_finished.emit(result)

        except Exception as e:
            if not self._is_cancelled:
                self.processing_error.emit(str(e))
        finally:
            # Clean up
            self._is_cancelled = False


class OCRMainWindow(QMainWindow):
    """Main application window for the OCR Invoice Parser GUI."""

    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)

        print("🔧 Loading configuration...")
        # Load configuration
        self.config = get_config()

        print("🤖 Initializing OCR parser...")
        # Initialize OCR parser
        self.ocr_parser = InvoiceParser(self.config)

        # OCR processing thread
        self.ocr_thread: Optional[OCRProcessingThread] = None

        # Current PDF path
        self.current_pdf_path: Optional[str] = None

        # Extracted data
        self.extracted_data: Optional[Dict[str, Any]] = None

        # Initialize business mapping manager for backups
        self.business_mapping_manager = None
        try:
            from ocrinvoice.business.business_mapping_manager import BusinessMappingManager

            self.business_mapping_manager = BusinessMappingManager()
            print("✅ Business mapping manager initialized")
        except Exception as e:
            print(f"⚠️ Could not initialize business mapping manager: {e}")

        # Initialize project manager
        self.project_manager = None
        try:
            from ocrinvoice.business.project_manager import ProjectManager

            self.project_manager = ProjectManager()
            print("✅ Project manager initialized")
        except Exception as e:
            print(f"⚠️ Could not initialize project manager: {e}")

        # Initialize PDF metadata manager
        self.pdf_metadata_manager = None
        try:
            self.pdf_metadata_manager = PDFMetadataManager()
            print("✅ PDF metadata manager initialized")
        except Exception as e:
            print(f"⚠️ Could not initialize PDF metadata manager: {e}")

        print("🎨 Setting up user interface...")
        # Set up the UI
        self._setup_ui()
        self._setup_menu_bar()
        self._setup_status_bar()
        self._setup_connections()

        # Set window properties
        self.setWindowTitle("OCR Invoice Parser")
        self.resize(1800, 800)
        self.move(100, 100)
        self.setMinimumSize(1200, 600)  # Ensure window doesn't get too small

        # Create startup backup
        self._create_startup_backup()

        print("✅ Main window initialization complete")

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
        self._create_project_tab()
        self._create_official_names_tab()
        self._create_business_aliases_tab()
        self._create_settings_tab()

    def _create_single_pdf_tab(self) -> None:
        """Create the Single PDF processing tab."""
        single_pdf_widget = QWidget()
        layout = QVBoxLayout(single_pdf_widget)

        # Create file selection area
        file_layout = QVBoxLayout()

        # Select PDF button
        self.select_pdf_btn = QPushButton("📁 Select PDF File")
        self.select_pdf_btn.setToolTip("Choose a PDF invoice to process")
        self.select_pdf_btn.clicked.connect(self._on_select_pdf)
        file_layout.addWidget(self.select_pdf_btn)

        # Add drag and drop area
        self.drop_area = QLabel(
            "📄 Drag and drop PDF files here\nor click 'Select PDF File' above"
        )
        self.drop_area.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.drop_area.setFixedHeight(80)
        self.drop_area.setWordWrap(True)
        file_layout.addWidget(self.drop_area)

        layout.addLayout(file_layout)

        # Add OCR progress bar
        self.ocr_progress = QProgressBar()
        self.ocr_progress.setVisible(False)
        self.ocr_progress.setRange(0, 100)  # Percentage-based progress
        self.ocr_progress.setFormat("🔄 Processing PDF with OCR... %p%")
        layout.addWidget(self.ocr_progress)

        # Main content area: PDF preview and data panel side by side
        content_splitter = QSplitter(Qt.Orientation.Horizontal)

        # PDF Preview (left side)
        self.pdf_preview = PDFPreviewWidget()
        content_splitter.addWidget(self.pdf_preview)

        # Data Panel (right side)
        business_names = []
        if self.business_mapping_manager:
            business_names = self.business_mapping_manager.get_all_business_names()
        self.data_panel = DataPanelWidget(business_names=business_names)
        self.data_panel.rename_requested.connect(self._on_rename_from_data_panel)
        # Connect data changes to file naming updates
        self.data_panel.data_changed.connect(self._on_data_changed)
        # Connect project selection changes
        self.data_panel.project_changed.connect(self._on_project_changed)
        # Connect document type selection changes
        self.data_panel.document_type_changed.connect(self._on_document_type_changed)
        content_splitter.addWidget(self.data_panel)

        # Set initial splitter sizes (60% PDF, 40% data)
        content_splitter.setSizes([900, 600])

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
        
        # Connect filename changes to status bar updates
        self.file_naming_widget.filename_changed.connect(self._update_filename_status_label)

        self.tab_widget.addTab(self.file_naming_widget, "File Naming")

    def _create_settings_tab(self) -> None:
        """Create the settings tab with basic configuration options."""
        settings_widget = QWidget()
        layout = QVBoxLayout(settings_widget)

        # Settings title
        title_label = QLabel("OCR Invoice Parser Settings")
        layout.addWidget(title_label)

        # OCR Settings Section
        ocr_group = QFrame()
        ocr_group.setFrameShape(QFrame.Shape.StyledPanel)
        ocr_layout = QVBoxLayout(ocr_group)

        ocr_title = QLabel("OCR Settings")
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

    def _create_business_aliases_tab(self) -> None:
        """Create the Business Aliases tab."""
        try:
            from .business_alias_tab import BusinessAliasTab

            business_aliases_widget = BusinessAliasTab()

            # Connect alias update signal to refresh OCR data if needed
            business_aliases_widget.alias_updated.connect(self._on_aliases_updated)

            # Add to tab widget
            self.tab_widget.addTab(business_aliases_widget, "Business Aliases")

        except ImportError:
            # Fallback if business alias components are not available
            fallback_widget = QWidget()
            layout = QVBoxLayout(fallback_widget)

            fallback_title = QLabel("Business Aliases")
            title_font = QFont()
            title_font.setBold(True)
            title_font.setPointSize(16)
            fallback_title.setFont(title_font)
            fallback_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(fallback_title)

            fallback_content = QLabel("Business alias management is not available.")
            fallback_content.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(fallback_content)

            self.tab_widget.addTab(fallback_widget, "Business Aliases")

    def _create_official_names_tab(self) -> None:
        """Create the Official Names tab."""
        try:
            from .official_names_tab import OfficialNamesTab

            official_names_widget = OfficialNamesTab()

            # Connect official names update signal to refresh OCR data if needed
            official_names_widget.official_names_updated.connect(
                self._on_official_names_updated
            )

            # Add to tab widget
            self.tab_widget.addTab(official_names_widget, "Official Names")

        except ImportError:
            # Fallback if official names components are not available
            fallback_widget = QWidget()
            layout = QVBoxLayout(fallback_widget)

            fallback_title = QLabel("Official Names")
            title_font = QFont()
            title_font.setBold(True)
            title_font.setPointSize(16)
            fallback_title.setFont(title_font)
            fallback_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(fallback_title)

            fallback_content = QLabel("Official names management is not available.")
            fallback_content.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(fallback_content)

            self.tab_widget.addTab(fallback_widget, "Official Names")

    def _on_aliases_updated(self) -> None:
        """Handle business aliases updates."""
        # Refresh OCR parser with updated aliases if needed
        if hasattr(self, "ocr_parser"):
            # Reinitialize parser to pick up new aliases
            self.ocr_parser = InvoiceParser(self.config)
        self.status_bar.showMessage("Business aliases updated - OCR parser refreshed")

    def _on_official_names_updated(self) -> None:
        """Handle official names updates."""
        # Refresh OCR parser with updated official names if needed
        if hasattr(self, "ocr_parser"):
            # Reinitialize parser to pick up new official names
            self.ocr_parser = InvoiceParser(self.config)
        self.status_bar.showMessage("Official names updated - OCR parser refreshed")

    def _create_project_tab(self) -> None:
        """Create the Projects tab."""
        try:
            from .project_tab import ProjectTab

            project_widget = ProjectTab()

            # Connect project update signal to refresh file naming if needed
            project_widget.project_updated.connect(self._on_projects_updated)

            # Add to tab widget
            self.tab_widget.addTab(project_widget, "Projects")

        except ImportError:
            # Fallback if project components are not available
            fallback_widget = QWidget()
            layout = QVBoxLayout(fallback_widget)

            fallback_title = QLabel("Projects")
            title_font = QFont()
            title_font.setBold(True)
            title_font.setPointSize(16)
            fallback_title.setFont(title_font)
            fallback_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(fallback_title)

            fallback_content = QLabel("Project management is not available.")
            fallback_content.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(fallback_content)

            self.tab_widget.addTab(fallback_widget, "Projects")

    def _on_projects_updated(self) -> None:
        """Handle projects updates."""
        # Refresh the project dropdown in the data panel
        self._update_project_dropdown()

        self.status_bar.showMessage("Projects updated")

    def _setup_menu_bar(self) -> None:
        """Set up the menu bar with enhanced menu items and keyboard shortcuts."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")

        # Open PDF action
        open_action = QAction("&Open PDF...", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.setStatusTip("Open a PDF file for OCR processing")
        open_action.triggered.connect(self._on_select_pdf)
        file_menu.addAction(open_action)

        file_menu.addSeparator()

        # Export action
        export_action = QAction("&Export Data...", self)
        export_action.setShortcut(QKeySequence("Ctrl+E"))
        export_action.setStatusTip("Export extracted data to file")
        export_action.triggered.connect(self._on_export_data)
        file_menu.addAction(export_action)

        file_menu.addSeparator()

        # Exit action
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.setStatusTip("Exit the application")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # View menu
        view_menu = menubar.addMenu("&View")

        # Tab navigation actions
        single_pdf_action = QAction("&Single PDF", self)
        single_pdf_action.setShortcut(QKeySequence("Ctrl+1"))
        single_pdf_action.setStatusTip("Switch to Single PDF processing tab")
        single_pdf_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(0))
        view_menu.addAction(single_pdf_action)

        file_naming_action = QAction("&File Naming", self)
        file_naming_action.setShortcut(QKeySequence("Ctrl+2"))
        file_naming_action.setStatusTip("Switch to File Naming configuration tab")
        file_naming_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(1))
        view_menu.addAction(file_naming_action)

        settings_action = QAction("&Settings", self)
        settings_action.setShortcut(QKeySequence("Ctrl+3"))
        settings_action.setStatusTip("Switch to Settings tab")
        settings_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(2))
        view_menu.addAction(settings_action)

        business_aliases_action = QAction("&Business Aliases", self)
        business_aliases_action.setShortcut(QKeySequence("Ctrl+4"))
        business_aliases_action.setStatusTip(
            "Switch to Business Aliases management tab"
        )
        business_aliases_action.triggered.connect(
            lambda: self.tab_widget.setCurrentIndex(3)
        )
        view_menu.addAction(business_aliases_action)

        official_names_action = QAction("&Official Names", self)
        official_names_action.setShortcut(QKeySequence("Ctrl+5"))
        official_names_action.setStatusTip("Switch to Official Names management tab")
        official_names_action.triggered.connect(
            lambda: self.tab_widget.setCurrentIndex(4)
        )
        view_menu.addAction(official_names_action)

        projects_action = QAction("&Projects", self)
        projects_action.setShortcut(QKeySequence("Ctrl+6"))
        projects_action.setStatusTip("Switch to Projects management tab")
        projects_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(5))
        view_menu.addAction(projects_action)

        # Help menu
        help_menu = menubar.addMenu("&Help")

        # Keyboard shortcuts help
        shortcuts_action = QAction("&Keyboard Shortcuts", self)
        shortcuts_action.setShortcut(QKeySequence("F1"))
        shortcuts_action.setStatusTip("Show keyboard shortcuts help")
        shortcuts_action.triggered.connect(self._show_keyboard_shortcuts)
        help_menu.addAction(shortcuts_action)

        help_menu.addSeparator()

        # About action
        about_action = QAction("&About", self)
        about_action.setStatusTip("About OCR Invoice Parser")
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def _setup_status_bar(self) -> None:
        """Set up the status bar for user feedback."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready - Select a PDF file to begin")
        # Add persistent new filename label
        self.filename_status_label = QLabel()
        self.status_bar.addPermanentWidget(self.filename_status_label)
        self._update_filename_status_label("")

    def _update_filename_status_label(self, new_filename: str) -> None:
        """Update the persistent filename label in the status bar."""
        if new_filename:
            self.filename_status_label.setText(f"New filename: {new_filename}")
        else:
            self.filename_status_label.setText("")

    def _setup_connections(self) -> None:
        """Set up signal connections."""
        self.tab_widget.currentChanged.connect(self._on_tab_changed)

        # Initialize project dropdown
        self._update_project_dropdown()

    def _on_tab_changed(self, index: int) -> None:
        """Handle tab changes."""
        tab_name = self.tab_widget.tabText(index)
        if tab_name == "Single PDF":
            self.status_bar.showMessage(
                "📄 Single PDF Processing - Select a PDF file to extract data"
            )
        elif tab_name == "File Naming":
            self.status_bar.showMessage(
                "📝 File Naming - Configure templates and preview filenames"
            )
        elif tab_name == "Settings":
            self.status_bar.showMessage(
                "⚙️ Settings - Configure application preferences"
            )
        elif tab_name == "Business Aliases":
            self.status_bar.showMessage(
                "🏢 Business Aliases - Manage company name mappings for improved OCR accuracy"
            )
        elif tab_name == "Official Names":
            self.status_bar.showMessage(
                "📋 Official Names - Manage canonical business names that aliases resolve to"
            )
        else:
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
        """Load PDF and check for metadata first, then start OCR processing if needed."""
        try:
            # Load PDF in preview widget
            if self.pdf_preview.load_pdf(pdf_path):
                self.current_pdf_path = pdf_path
                self.status_bar.showMessage(f"Loaded PDF: {pdf_path}")
                self._show_success_message("PDF loaded successfully")

                # Check for saved metadata first
                if self.pdf_metadata_manager and self.pdf_metadata_manager.has_saved_data(pdf_path):
                    self.status_bar.showMessage("📋 Loading saved data from PDF metadata...")
                    saved_data = self.pdf_metadata_manager.load_data_from_pdf(pdf_path)
                    if saved_data:
                        print(f"📋 [PDF METADATA LOADED] File: {pdf_path}")
                        print(f"📋 [PDF METADATA LOADED] Data: {saved_data}")
                        print(f"📋 [PDF METADATA LOADED] Fields: {list(saved_data.keys())}")
                        # Use saved data instead of running OCR
                        self._on_ocr_finished(saved_data)
                        self.status_bar.showMessage("✅ Loaded data from PDF metadata")
                        return

                # No saved data found, start OCR processing
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
        self.ocr_thread.processing_progress.connect(self._on_ocr_progress)

        self.ocr_thread.start()

    def _on_ocr_started(self) -> None:
        """Handle OCR processing started."""
        self.ocr_progress.setVisible(True)
        self.status_bar.showMessage("🔄 Processing PDF with OCR - Please wait...")
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

        # Restore project and document type selections from metadata
        selected_project = extracted_data.get("selected_project", "")
        selected_document_type = extracted_data.get("selected_document_type", "")
        
        # Set project selection if found in metadata
        if selected_project:
            self.data_panel.set_selected_project(selected_project)
            if self.file_naming_widget:
                self.file_naming_widget.set_project(selected_project)
            print(f"✅ Restored project selection: {selected_project}")
        
        # Set document type selection if found in metadata
        if selected_document_type:
            self.data_panel.set_selected_document_type(selected_document_type)
            print(f"✅ Restored document type selection: {selected_document_type}")

        # Update file naming widget with extracted data
        if self.current_pdf_path:
            from pathlib import Path

            original_filename = Path(self.current_pdf_path).name
            self.file_naming_widget.update_data(
                extracted_data, original_filename, self.current_pdf_path
            )
            # Update persistent filename label after data update
            new_filename = self.file_naming_widget.new_filename_label.text()
            self._update_filename_status_label(new_filename)

        # Save extracted data to PDF metadata
        if self.pdf_metadata_manager and self.current_pdf_path:
            try:
                print(f"💾 [PDF METADATA SAVING] File: {self.current_pdf_path}")
                print(f"💾 [PDF METADATA SAVING] Data: {extracted_data}")
                print(f"💾 [PDF METADATA SAVING] Fields: {list(extracted_data.keys())}")
                
                success = self.pdf_metadata_manager.save_data_to_pdf(
                    self.current_pdf_path, extracted_data
                )
                if success:
                    print("✅ Successfully saved OCR data to PDF metadata")
                else:
                    print("⚠️ Failed to save OCR data to PDF metadata")
            except Exception as e:
                print(f"⚠️ Error saving OCR metadata: {e}")

        # Show success message with confidence indicator
        company = extracted_data.get("company", "Unknown")
        total = extracted_data.get("total", "Unknown")
        confidence = extracted_data.get("confidence", 0)

        # Improve company name display
        if company and company != "Unknown":
            # Capitalize company name for better display
            company_display = company.title()
        else:
            company_display = "Unknown Company"

        # Format total amount
        if total and total != "Unknown":
            if isinstance(total, (int, float)):
                total_display = f"${total:.2f}"
            else:
                total_display = str(total)
        else:
            total_display = "Unknown"

        # Show status with confidence indicator
        if confidence and confidence > 0.7:
            status_msg = (
                f"✅ OCR completed successfully! {company_display} - "
                f"{total_display} (Confidence: {confidence:.1%})"
            )
        else:
            status_msg = (
                f"⚠️ OCR completed with low confidence. {company_display} - "
                f"{total_display} (Confidence: {confidence:.1%})"
            )

        self.status_bar.showMessage(status_msg)
        self._show_success_message("OCR processing completed successfully")

    def _on_ocr_error(self, error_message: str) -> None:
        """Handle OCR processing error."""
        self.ocr_progress.setVisible(False)
        self.select_pdf_btn.setEnabled(True)

        # Provide more specific error messages
        if "tesseract" in error_message.lower():
            user_message = (
                "OCR Engine Error: Tesseract is not installed or not found in PATH. "
                "Please install Tesseract OCR."
            )
        elif "pdf" in error_message.lower() and "corrupt" in error_message.lower():
            user_message = (
                "PDF Error: The selected file appears to be corrupted or "
                "not a valid PDF."
            )
        elif "permission" in error_message.lower():
            user_message = (
                "Permission Error: Cannot access the selected file. "
                "Please check file permissions."
            )
        elif "memory" in error_message.lower():
            user_message = (
                "Memory Error: The PDF is too large to process. "
                "Try with a smaller file."
            )
        else:
            user_message = f"OCR Processing Error: {error_message}"

        self.status_bar.showMessage(f"❌ {user_message}")
        self._show_error_message(user_message)

        # Clear any partial data
        self.extracted_data = None
        self.data_panel.clear_data()

    def _on_ocr_progress(self, progress: int) -> None:
        """Handle OCR processing progress updates."""
        self.ocr_progress.setValue(progress)

    def _show_error_message(self, message: str) -> None:
        """Show error message to user with improved formatting."""
        error_dialog = QMessageBox(self)
        error_dialog.setIcon(QMessageBox.Icon.Critical)
        error_dialog.setWindowTitle("OCR Processing Error")
        error_dialog.setText("An error occurred during OCR processing:")
        error_dialog.setInformativeText(message)
        error_dialog.setStandardButtons(QMessageBox.StandardButton.Ok)
        error_dialog.setDefaultButton(QMessageBox.StandardButton.Ok)

        # Add helpful suggestions based on error type
        if "tesseract" in message.lower():
            error_dialog.setDetailedText(
                "To fix this issue:\n"
                "1. Download and install Tesseract OCR from: "
                "https://github.com/tesseract-ocr/tesseract\n"
                "2. Add Tesseract to your system PATH\n"
                "3. Restart the application"
            )
        elif "pdf" in message.lower():
            error_dialog.setDetailedText(
                "To fix this issue:\n"
                "1. Verify the file is a valid PDF\n"
                "2. Try opening the file in a PDF viewer\n"
                "3. If the file is corrupted, try to obtain a new copy"
            )

        error_dialog.exec()
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
        # Update persistent filename label
        new_filename = self.file_naming_widget.new_filename_label.text()
        self._update_filename_status_label(new_filename)
        self.status_bar.showMessage("File naming template updated")

    def _on_export_data(self) -> None:
        """Handle data export from menu."""
        if not self.extracted_data:
            QMessageBox.information(
                self, "No Data", "No data to export. Please process a PDF first."
            )
            return

        # TODO: Implement actual export functionality
        self.status_bar.showMessage("Export functionality coming in future sprints")

    def _on_data_changed(self, updated_data: Dict[str, Any]) -> None:
        """Handle data changes from the data panel."""
        # Update the stored extracted data
        self.extracted_data = updated_data

        # Update file naming widget with new data
        if self.current_pdf_path:
            from pathlib import Path

            original_filename = Path(self.current_pdf_path).name
            self.file_naming_widget.update_data(
                updated_data, original_filename, self.current_pdf_path
            )
            # Update persistent filename label after data update
            new_filename = self.file_naming_widget.new_filename_label.text()
            self._update_filename_status_label(new_filename)

        # Save updated data to PDF metadata
        if self.pdf_metadata_manager and self.current_pdf_path:
            try:
                success = self.pdf_metadata_manager.save_data_to_pdf(
                    self.current_pdf_path, updated_data
                )
                if success:
                    self.status_bar.showMessage("✅ Data updated and saved to PDF metadata")
                else:
                    self.status_bar.showMessage("⚠️ Data updated but failed to save to PDF metadata")
            except Exception as e:
                print(f"⚠️ Error saving metadata: {e}")
                self.status_bar.showMessage("⚠️ Data updated but failed to save to PDF metadata")
        else:
            # Show status message indicating data was updated
            self.status_bar.showMessage("✅ Data updated - file name preview refreshed")

    def _on_project_changed(self, project_name: str) -> None:
        """Handle project selection changes from the data panel."""
        # Update the file naming widget with the selected project
        if self.file_naming_widget:
            self.file_naming_widget.set_project(project_name)
        
        # Update the status bar
        self.status_bar.showMessage(f"Project selected: {project_name}")

    def _on_document_type_changed(self, document_type: str) -> None:
        """Handle document type selection changes from the data panel."""
        # Update the file naming widget's preview to reflect the new document type
        if self.file_naming_widget:
            self.file_naming_widget._update_preview()
        
        # Update the status bar
        self.status_bar.showMessage(f"Document type selected: {document_type}")

    def _update_project_dropdown(self) -> None:
        """Update the project dropdown with available projects."""
        if self.project_manager and self.data_panel:
            try:
                projects = self.project_manager.get_project_names()
                self.data_panel.update_projects(projects)
            except Exception as e:
                print(f"⚠️ Could not load projects: {e}")

    def _on_rename_from_data_panel(self) -> None:
        """Handle rename request from data panel."""
        if not self.extracted_data or not self.current_pdf_path:
            QMessageBox.warning(
                self, "Error", "No file or data available for renaming."
            )
            return

        # Trigger the rename in the file naming widget without switching tabs
        if hasattr(self.file_naming_widget, "_rename_file"):
            self.file_naming_widget._rename_file()

    def _show_keyboard_shortcuts(self) -> None:
        """Show keyboard shortcuts help dialog."""
        shortcuts_text = """
Keyboard Shortcuts:

File Operations:
  Ctrl+O          Open PDF file
  Ctrl+E          Export data
  Ctrl+Q          Quit application

Navigation:
  Ctrl+1          Switch to Single PDF tab
  Ctrl+2          Switch to File Naming tab
  Ctrl+3          Switch to Settings tab
  Ctrl+4          Switch to Business Aliases tab
  Ctrl+5          Switch to Official Names tab
  Ctrl+6          Switch to Projects tab

Help:
  F1              Show this help dialog

PDF Preview (when focused):
  Ctrl++          Zoom in
  Ctrl+-          Zoom out
  Ctrl+0          Reset zoom to 100%
  Ctrl+Wheel      Zoom with mouse wheel
        """

        QMessageBox.information(self, "Keyboard Shortcuts", shortcuts_text)

    def _create_startup_backup(self) -> None:
        """Create a backup on application startup."""
        if self.business_mapping_manager:
            try:
                backup_path = self.business_mapping_manager.create_startup_backup()
                if backup_path:
                    self.status_bar.showMessage(
                        f"Startup backup created: {os.path.basename(backup_path)}", 3000
                    )
            except Exception as e:
                print(f"⚠️ Startup backup failed: {e}")

    def _create_shutdown_backup(self) -> None:
        """Create a backup on application shutdown."""
        if self.business_mapping_manager:
            try:
                backup_path = self.business_mapping_manager.create_shutdown_backup()
                if backup_path:
                    print(
                        f"✅ Shutdown backup created: {os.path.basename(backup_path)}"
                    )
            except Exception as e:
                print(f"⚠️ Shutdown backup failed: {e}")

    def _show_about(self) -> None:
        """Show the about dialog."""
        QMessageBox.about(
            self,
            "About OCR Invoice Parser",
            "OCR Invoice Parser GUI\n\n"
            "A desktop application for extracting structured data from PDF invoices "
            "using OCR.\n\n"
            "Version: 1.3.16\n"
            "Development Phase: Sprint 4 - MVP Polish & Testing",
        )

    def closeEvent(self, event: Optional[QCloseEvent]) -> None:
        """Handle application close event."""
        # Create shutdown backup
        self._create_shutdown_backup()

        # Cancel any ongoing OCR processing
        if self.ocr_thread and self.ocr_thread.isRunning():
            self.ocr_thread.cancel()
            self.ocr_thread.wait()

        if event is not None:
            event.accept()


def main() -> None:
    """Main entry point for the OCR GUI application."""
    import time
    from pathlib import Path

    # Startup logging
    print("🚀 Starting OCR Invoice Parser...")
    print(f"📁 Working directory: {Path.cwd()}")

    # Check if running in PyInstaller bundle
    if getattr(sys, "frozen", False):
        print("📦 Running from PyInstaller binary")
        print(f"📦 Bundle path: {getattr(sys, '_MEIPASS', 'Unknown')}")
    else:
        print("🔧 Running from source code")

    print("⚙️  Initializing application...")
    start_time = time.time()

    app = QApplication(sys.argv)
    app.setApplicationName("OCR Invoice Parser")
    app.setApplicationVersion("1.3.16")

    # Set Qt application settings to ensure window size is respected
    # app.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)
    # app.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)

    print("🎨 Creating main window...")

    # Create and show splash screen
    splash = QSplashScreen()
    splash.setPixmap(QPixmap(400, 200))
    splash.show()

    # Update splash screen with progress
    splash.showMessage(
        "Initializing OCR Invoice Parser...",
        Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignBottom,
    )
    app.processEvents()

    print("🔧 Loading configuration...")
    splash.showMessage(
        "Loading configuration...",
        Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignBottom,
    )
    app.processEvents()

    window = OCRMainWindow()

    print("🎨 Setting up user interface...")
    splash.showMessage(
        "Setting up user interface...",
        Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignBottom,
    )
    app.processEvents()

    window.show()

    def force_window_size():
        window.resize(900, 800)
        window.move(100, 100)

    QTimer.singleShot(0, force_window_size)

    splash.finish(window)

    startup_time = time.time() - start_time
    print(f"✅ Application started in {startup_time:.2f} seconds")
    print("🎯 Ready to process PDF invoices!")

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
