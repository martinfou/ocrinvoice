"""
Main Window for Business Aliases GUI Manager

The primary application window containing the alias table,
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
from PyQt6.QtGui import QAction, QKeySequence

from .alias_table import AliasTable
from .alias_form import AliasForm
from ..business.business_alias_manager import BusinessAliasManager


class MainWindow(QMainWindow):
    """
    Main application window for the Business Aliases GUI Manager.

    Provides a complete interface for managing business aliases with
    table view, toolbar actions, menu system, and status bar.
    """

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        # Initialize business logic
        self.alias_manager = BusinessAliasManager()

        # Window setup
        self.setWindowTitle("Business Aliases Manager")
        self.setMinimumSize(800, 600)
        self.resize(1024, 768)

        # Initialize UI components
        self._setup_ui()
        self._setup_menu_bar()
        self._setup_toolbar()
        self._setup_status_bar()
        self._setup_connections()

        # Load initial data
        self._load_aliases()

    def _setup_ui(self) -> None:
        """Set up the main user interface components."""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(8)

        # Create alias table
        self.alias_table = AliasTable()
        main_layout.addWidget(self.alias_table)

        # Create alias form (initially hidden)
        self.alias_form = AliasForm()
        self.alias_form.hide()
        main_layout.addWidget(self.alias_form)

    def _setup_menu_bar(self) -> None:
        """Set up the menu bar with all menu items."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")

        # New alias action
        new_action = QAction("&New Alias", self)
        new_action.setShortcut(QKeySequence.StandardKey.New)
        new_action.setStatusTip("Add a new business alias")
        new_action.triggered.connect(self._add_alias)
        file_menu.addAction(new_action)

        file_menu.addSeparator()

        # Import action
        import_action = QAction("&Import...", self)
        import_action.setShortcut(QKeySequence.StandardKey.Open)
        import_action.setStatusTip("Import aliases from file")
        import_action.triggered.connect(self._import_aliases)
        file_menu.addAction(import_action)

        # Export action
        export_action = QAction("&Export...", self)
        export_action.setShortcut(QKeySequence("Ctrl+Shift+E"))
        export_action.setStatusTip("Export aliases to file")
        export_action.triggered.connect(self._export_aliases)
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

        # Edit alias action
        edit_action = QAction("&Edit Alias", self)
        edit_action.setShortcut(QKeySequence.StandardKey.Copy)
        edit_action.setStatusTip("Edit selected alias")
        edit_action.triggered.connect(self._edit_alias)
        edit_menu.addAction(edit_action)

        # Delete alias action
        delete_action = QAction("&Delete Alias", self)
        delete_action.setShortcut(QKeySequence.StandardKey.Delete)
        delete_action.setStatusTip("Delete selected alias")
        delete_action.triggered.connect(self._delete_alias)
        edit_menu.addAction(delete_action)

        edit_menu.addSeparator()

        # Select all action
        select_all_action = QAction("Select &All", self)
        select_all_action.setShortcut(QKeySequence.StandardKey.SelectAll)
        select_all_action.setStatusTip("Select all aliases")
        select_all_action.triggered.connect(self.alias_table.selectAll)
        edit_menu.addAction(select_all_action)

        # Tools menu
        tools_menu = menubar.addMenu("&Tools")

        # Statistics action
        stats_action = QAction("&Statistics", self)
        stats_action.setStatusTip("View alias statistics")
        stats_action.triggered.connect(self._show_statistics)
        tools_menu.addAction(stats_action)

        # Help menu
        help_menu = menubar.addMenu("&Help")

        # About action
        about_action = QAction("&About", self)
        about_action.setStatusTip("About Business Aliases Manager")
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def _setup_toolbar(self) -> None:
        """Set up the toolbar with action buttons."""
        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(toolbar)

        # Add alias button
        add_action = QAction("➕ Add", self)
        add_action.setStatusTip("Add a new business alias")
        add_action.triggered.connect(self._add_alias)
        toolbar.addAction(add_action)

        # Edit alias button
        edit_action = QAction("✏️ Edit", self)
        edit_action.setStatusTip("Edit selected alias")
        edit_action.triggered.connect(self._edit_alias)
        toolbar.addAction(edit_action)

        # Delete alias button
        delete_action = QAction("🗑️ Delete", self)
        delete_action.setStatusTip("Delete selected alias")
        delete_action.triggered.connect(self._delete_alias)
        toolbar.addAction(delete_action)

        toolbar.addSeparator()

        # Import button
        import_action = QAction("📥 Import", self)
        import_action.setStatusTip("Import aliases from file")
        import_action.triggered.connect(self._import_aliases)
        toolbar.addAction(import_action)

        # Export button
        export_action = QAction("📤 Export", self)
        export_action.setStatusTip("Export aliases to file")
        export_action.triggered.connect(self._export_aliases)
        toolbar.addAction(export_action)

        toolbar.addSeparator()

        # Refresh button
        refresh_action = QAction("🔄 Refresh", self)
        refresh_action.setStatusTip("Refresh alias data")
        refresh_action.triggered.connect(self._load_aliases)
        toolbar.addAction(refresh_action)

        # Statistics button
        stats_action = QAction("📊 Statistics", self)
        stats_action.setStatusTip("View alias statistics")
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
        # Connect alias table signals
        self.alias_table.alias_selected.connect(self._on_alias_selected)
        self.alias_table.alias_double_clicked.connect(self._edit_alias)

        # Connect alias form signals
        self.alias_form.alias_saved.connect(self._on_alias_saved)
        self.alias_form.alias_cancelled.connect(self._on_alias_cancelled)

    def _load_aliases(self) -> None:
        """Load aliases from the business alias manager."""
        try:
            # Get aliases from manager
            exact_matches = self.alias_manager.config.get("exact_matches", {})
            partial_matches = self.alias_manager.config.get("partial_matches", {})

            # Load into table
            self.alias_table.load_aliases(exact_matches, partial_matches)

            # Update status
            total_count = len(exact_matches) + len(partial_matches)
            self.status_bar.showMessage(f"{total_count} aliases loaded")

        except Exception as e:
            QMessageBox.critical(
                self, "Error Loading Aliases", f"Failed to load aliases: {str(e)}"
            )
            self.status_bar.showMessage("Error loading aliases")

    def _add_alias(self) -> None:
        """Show the add alias form."""
        self.alias_form.show_add_mode()
        self.alias_form.show()
        self.alias_table.hide()

    def _edit_alias(self) -> None:
        """Edit the selected alias."""
        selected_alias = self.alias_table.get_selected_alias()
        if selected_alias:
            self.alias_form.show_edit_mode(selected_alias)
            self.alias_form.show()
            self.alias_table.hide()
        else:
            QMessageBox.information(
                self, "No Selection", "Please select an alias to edit."
            )

    def _delete_alias(self) -> None:
        """Delete the selected alias."""
        selected_alias = self.alias_table.get_selected_alias()
        if not selected_alias:
            QMessageBox.information(
                self, "No Selection", "Please select an alias to delete."
            )
            return

        # Confirm deletion
        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete the alias '{selected_alias['alias']}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                # Delete from manager
                match_type = selected_alias.get("match_type", "exact_matches")
                del self.alias_manager.config[match_type][selected_alias["alias"]]
                self.alias_manager._save_config()

                # Reload table
                self._load_aliases()

                self.status_bar.showMessage(f"Deleted alias: {selected_alias['alias']}")

            except Exception as e:
                QMessageBox.critical(
                    self, "Error Deleting Alias", f"Failed to delete alias: {str(e)}"
                )

    def _import_aliases(self) -> None:
        """Import aliases from file."""
        # TODO: Implement import dialog
        QMessageBox.information(
            self,
            "Import Aliases",
            "Import functionality will be implemented in Phase 2.",
        )

    def _export_aliases(self) -> None:
        """Export aliases to file."""
        # TODO: Implement export dialog
        QMessageBox.information(
            self,
            "Export Aliases",
            "Export functionality will be implemented in Phase 2.",
        )

    def _show_statistics(self) -> None:
        """Show alias statistics."""
        try:
            stats = self.alias_manager.get_stats()

            stats_text = f"""
Statistics:
• Total official names: {stats['official_names']}
• Total exact matches: {stats['exact_matches']}
• Total partial matches: {stats['partial_matches']}
• Total fuzzy candidates: {stats['fuzzy_candidates']}
• Total unique businesses: {stats['total_businesses']}
            """.strip()

            QMessageBox.information(self, "Alias Statistics", stats_text)

        except Exception as e:
            QMessageBox.critical(
                self, "Error Loading Statistics", f"Failed to load statistics: {str(e)}"
            )

    def _show_about(self) -> None:
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About Business Aliases Manager",
            """
Business Aliases Manager v1.0.0

A PyQt6 desktop application for managing business name aliases
used by the OCR invoice parser.

Part of the OCR Invoice Parser project.
            """.strip(),
        )

    def _on_alias_selected(self, alias_data: Dict[str, Any]) -> None:
        """Handle alias selection in the table."""
        if alias_data:
            self.status_bar.showMessage(
                f"Selected: {alias_data['alias']} → {alias_data['official_name']}"
            )
        else:
            self.status_bar.showMessage("Ready")

    def _on_alias_saved(self, alias_data: Dict[str, Any]) -> None:
        """Handle alias save from form."""
        try:
            # Save to manager
            alias = alias_data["alias"]
            official_name = alias_data["official_name"]
            match_type = alias_data.get("match_type", "exact_matches")

            self.alias_manager.add_alias(alias, official_name, match_type)

            # Hide form and show table
            self.alias_form.hide()
            self.alias_table.show()

            # Reload data
            self._load_aliases()

            self.status_bar.showMessage(f"Saved alias: {alias} → {official_name}")

        except Exception as e:
            QMessageBox.critical(
                self, "Error Saving Alias", f"Failed to save alias: {str(e)}"
            )

    def _on_alias_cancelled(self) -> None:
        """Handle alias form cancellation."""
        self.alias_form.hide()
        self.alias_table.show()
        self.status_bar.showMessage("Ready")

    def closeEvent(self, event) -> None:
        """Handle application close event."""
        # TODO: Save window state and settings
        event.accept()


def main() -> None:
    """Main entry point for the GUI application."""
    app = QApplication(sys.argv)
    app.setApplicationName("Business Aliases Manager")
    app.setApplicationVersion("1.0.0")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
