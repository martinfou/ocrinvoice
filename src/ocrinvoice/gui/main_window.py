"""
Main Window for Business Mappings GUI Manager

The primary application window containing the mapping table,
toolbar, menu bar, and status bar.
"""

import sys
from typing import Optional, Dict, Any

from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QToolBar,
    QStatusBar,
    QMessageBox,
    QApplication,
)
from PyQt6.QtCore import QSize
from PyQt6.QtGui import QAction, QKeySequence, QCloseEvent

from .mapping_table import MappingTable
from .mapping_form import MappingForm
from ocrinvoice.business.business_mapping_manager import BusinessMappingManager


class MainWindow(QMainWindow):
    """
    Main application window for the Business Mappings GUI Manager.

    Provides a complete interface for managing business mappings with
    table view, toolbar actions, menu system, and status bar.
    """

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        # Initialize business logic
        self.mapping_manager = BusinessMappingManager()

        # Window setup
        self.setWindowTitle("Business Mappings Manager")
        self.setMinimumSize(800, 600)
        self.resize(1024, 768)

        # Initialize UI components
        self._setup_ui()
        self._setup_menu_bar()
        self._setup_toolbar()
        self._setup_status_bar()
        self._setup_connections()

        # Load initial data
        self._load_mappings()

    def _setup_ui(self) -> None:
        """Set up the main user interface components."""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(8)

        # Create mapping table
        self.mapping_table = MappingTable()
        main_layout.addWidget(self.mapping_table)

        # Create mapping form (initially hidden)
        self.mapping_form = MappingForm()
        self.mapping_form.hide()
        main_layout.addWidget(self.mapping_form)

    def _setup_menu_bar(self) -> None:
        """Set up the menu bar with all menu items."""
        menubar = self.menuBar()
        file_menu = menubar.addMenu("&File")

        # New mapping action
        new_action = QAction("&New Mapping", self)
        new_action.setShortcut(QKeySequence.StandardKey.New)
        new_action.setStatusTip("Add a new business mapping")
        new_action.triggered.connect(self._add_mapping)
        file_menu.addAction(new_action)

        file_menu.addSeparator()

        # Import action
        import_action = QAction("&Import...", self)
        import_action.setShortcut(QKeySequence.StandardKey.Open)
        import_action.setStatusTip("Import mappings from file")
        import_action.triggered.connect(self._import_mappings)
        file_menu.addAction(import_action)

        # Export action
        export_action = QAction("&Export...", self)
        export_action.setShortcut(QKeySequence("Ctrl+Shift+E"))
        export_action.setStatusTip("Export mappings to file")
        export_action.triggered.connect(self._export_mappings)
        file_menu.addAction(export_action)

        file_menu.addSeparator()

        # Exit action
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.setStatusTip("Exit the application")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Edit menu
        edit_menu = menubar.addMenu("&Edit")

        # Edit mapping action
        edit_action = QAction("&Edit Mapping", self)
        edit_action.setShortcut(QKeySequence.StandardKey.Copy)
        edit_action.setStatusTip("Edit selected mapping")
        edit_action.triggered.connect(self._edit_mapping)
        edit_menu.addAction(edit_action)

        # Delete mapping action
        delete_action = QAction("&Delete Mapping", self)
        delete_action.setShortcut(QKeySequence.StandardKey.Delete)
        delete_action.setStatusTip("Delete selected mapping")
        delete_action.triggered.connect(self._delete_mapping)
        edit_menu.addAction(delete_action)

        edit_menu.addSeparator()

        # Select all action
        select_all_action = QAction("Select &All", self)
        select_all_action.setShortcut(QKeySequence.StandardKey.SelectAll)
        select_all_action.setStatusTip("Select all mappings")
        select_all_action.triggered.connect(self.mapping_table.selectAll)
        edit_menu.addAction(select_all_action)

        # Tools menu
        tools_menu = menubar.addMenu("&Tools")

        # Statistics action
        stats_action = QAction("&Statistics", self)
        stats_action.setStatusTip("View mapping statistics")
        stats_action.triggered.connect(self._show_statistics)
        tools_menu.addAction(stats_action)

        # Help menu
        help_menu = menubar.addMenu("&Help")

        # About action
        about_action = QAction("&About", self)
        about_action.setStatusTip("About Business Mappings Manager")
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def _setup_toolbar(self) -> None:
        """Set up the toolbar with action buttons."""
        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(toolbar)

        # Add mapping button
        add_action = QAction("➕ Add", self)
        add_action.setStatusTip("Add a new business mapping")
        add_action.triggered.connect(self._add_mapping)
        toolbar.addAction(add_action)

        # Edit mapping button
        edit_action = QAction("✏️ Edit", self)
        edit_action.setStatusTip("Edit selected mapping")
        edit_action.triggered.connect(self._edit_mapping)
        toolbar.addAction(edit_action)

        # Delete mapping button
        delete_action = QAction("🗑️ Delete", self)
        delete_action.setStatusTip("Delete selected mapping")
        delete_action.triggered.connect(self._delete_mapping)
        toolbar.addAction(delete_action)

        toolbar.addSeparator()

        # Import button
        import_action = QAction("📥 Import", self)
        import_action.setStatusTip("Import mappings from file")
        import_action.triggered.connect(self._import_mappings)
        toolbar.addAction(import_action)

        # Export button
        export_action = QAction("📤 Export", self)
        export_action.setStatusTip("Export mappings to file")
        export_action.triggered.connect(self._export_mappings)
        toolbar.addAction(export_action)

        toolbar.addSeparator()

        # Refresh button
        refresh_action = QAction("🔄 Refresh", self)
        refresh_action.setStatusTip("Refresh mapping data")
        refresh_action.triggered.connect(self._load_mappings)
        toolbar.addAction(refresh_action)

        # Statistics button
        stats_action = QAction("📊 Statistics", self)
        stats_action.setStatusTip("View mapping statistics")
        stats_action.triggered.connect(self._show_statistics)
        toolbar.addAction(stats_action)

    def _setup_status_bar(self) -> None:
        """Set up the status bar with information display."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # Initial status message
        self.status_bar.showMessage("Ready")

    def _setup_connections(self) -> None:
        """Set up signal/slot connections between components."""
        # Connect mapping table signals
        self.mapping_table.mapping_selected.connect(self._on_mapping_selected)
        self.mapping_table.mapping_double_clicked.connect(self._edit_mapping)

        # Connect mapping form signals
        self.mapping_form.mapping_saved.connect(self._on_mapping_saved)
        self.mapping_form.mapping_cancelled.connect(self._on_mapping_cancelled)

    def _load_mappings(self) -> None:
        """Load mappings from the business mapping manager."""
        try:
            # Get mappings from manager
            exact_matches = self.mapping_manager.config.get("exact_matches", {})
            partial_matches = self.mapping_manager.config.get("partial_matches", {})

            # Load into table
            self.mapping_table.load_mappings(exact_matches, partial_matches)

            # Update status
            total_count = len(exact_matches) + len(partial_matches)
            self.status_bar.showMessage(f"{total_count} mappings loaded")

        except Exception as e:
            QMessageBox.critical(
                self, "Error Loading Mappings", f"Failed to load mappings: {str(e)}"
            )
            self.status_bar.showMessage("Error loading mappings")

    def _add_mapping(self) -> None:
        """Show the add mapping form."""
        self.mapping_form.show_add_mode()
        self.mapping_form.show()
        self.mapping_table.hide()

    def _edit_mapping(self) -> None:
        """Edit the selected mapping."""
        selected_mapping = self.mapping_table.get_selected_mapping()
        if selected_mapping:
            self.mapping_form.show_edit_mode(selected_mapping)
            self.mapping_form.show()
            self.mapping_table.hide()
        else:
            QMessageBox.information(
                self, "No Selection", "Please select a mapping to edit."
            )

    def _delete_mapping(self) -> None:
        """Delete the selected mapping."""
        selected_mapping = self.mapping_table.get_selected_mapping()
        if not selected_mapping:
            QMessageBox.information(
                self, "No Selection", "Please select a mapping to delete."
            )
            return

        # Confirm deletion
        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete the mapping '{selected_mapping['mapping']}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                # Delete from manager
                match_type = selected_mapping.get("match_type", "exact_matches")
                del self.mapping_manager.config[match_type][selected_mapping["mapping"]]
                self.mapping_manager._save_config()

                # Reload table
                self._load_mappings()

                self.status_bar.showMessage(
                    f"Deleted mapping: {selected_mapping['mapping']}"
                )

            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error Deleting Mapping",
                    f"Failed to delete mapping: {str(e)}",
                )

    def _import_mappings(self) -> None:
        """Import mappings from file."""
        # TODO: Implement import dialog
        QMessageBox.information(
            self,
            "Import Mappings",
            "Import functionality will be implemented in Phase 2.",
        )

    def _export_mappings(self) -> None:
        """Export mappings to file."""
        # TODO: Implement export dialog
        QMessageBox.information(
            self,
            "Export Mappings",
            "Export functionality will be implemented in Phase 2.",
        )

    def _show_statistics(self) -> None:
        """Show mapping statistics."""
        try:
            stats = self.mapping_manager.get_stats()

            stats_text = f"""
Statistics:
            • Total business canonical names: {stats['official_names']}
• Total exact matches: {stats['exact_matches']}
• Total partial matches: {stats['partial_matches']}
• Total fuzzy candidates: {stats['fuzzy_candidates']}
• Total unique businesses: {stats['total_businesses']}
            """.strip()

            QMessageBox.information(self, "Mapping Statistics", stats_text)

        except Exception as e:
            QMessageBox.critical(
                self, "Error Loading Statistics", f"Failed to load statistics: {str(e)}"
            )

    def _show_about(self) -> None:
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About Business Mappings Manager",
            """
Business Mappings Manager v1.3.17

A PyQt6 desktop application for managing business name mappings
used by the OCR invoice parser.

Part of the OCR Invoice Parser project.
            """.strip(),
        )

    def _on_mapping_selected(self, mapping_data: Dict[str, Any]) -> None:
        """Handle mapping selection in the table."""
        if mapping_data:
            self.status_bar.showMessage(
                f"Selected: {mapping_data['mapping']} → {mapping_data['official_name']}"
            )
        else:
            self.status_bar.showMessage("Ready")

    def _on_mapping_saved(self, mapping_data: Dict[str, Any]) -> None:
        """Handle mapping save from form."""
        try:
            # Save to manager
            mapping = mapping_data["mapping"]
            official_name = mapping_data["official_name"]
            match_type = mapping_data.get("match_type", "exact_matches")

            self.mapping_manager.add_mapping(mapping, official_name, match_type)

            # Hide form and show table
            self.mapping_form.hide()
            self.mapping_table.show()

            # Reload data
            self._load_mappings()

            self.status_bar.showMessage(f"Saved mapping: {mapping} → {official_name}")

        except Exception as e:
            QMessageBox.critical(
                self, "Error Saving Mapping", f"Failed to save mapping: {str(e)}"
            )

    def _on_mapping_cancelled(self) -> None:
        """Handle mapping form cancellation."""
        self.mapping_form.hide()
        self.mapping_table.show()
        self.status_bar.showMessage("Ready")

    def closeEvent(self, event: Optional[QCloseEvent]) -> None:
        """Handle application close event."""
        # TODO: Save window state and settings
        event.accept()


def main() -> None:
    """Main entry point for the GUI application."""
    app = QApplication(sys.argv)
    app.setApplicationName("Business Mappings Manager")
    app.setApplicationVersion("1.3.17")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
