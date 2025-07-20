"""
Tests for OCR Main Window

Tests for the OCR GUI main window functionality.
"""

import os
import pytest
from pytestqt.qtbot import QtBot

# Skip GUI tests in CI environments (including Windows CI)
if os.environ.get("CI"):
    pytest.skip("GUI tests disabled in CI environment", allow_module_level=True)

from ocrinvoice.gui.ocr_main_window import OCRMainWindow


@pytest.fixture  # type: ignore[misc]
def main_window(qtbot: QtBot) -> OCRMainWindow:
    """Create a main window instance for testing."""
    try:
        window = OCRMainWindow()
        qtbot.addWidget(window)
        # Show the window to trigger the QTimer.singleShot resize
        window.show()
        # Add timeout to prevent hanging and allow QTimer to execute
        qtbot.wait(200)
        return window
    except Exception as e:
        pytest.skip(f"GUI initialization failed: {e}")


@pytest.mark.gui
class TestOCRMainWindow:
    """Test cases for the OCR Main Window."""

    def test_window_creation(self, main_window: OCRMainWindow) -> None:
        """Test that the main window can be created successfully."""
        assert main_window is not None
        assert main_window.windowTitle() == "OCR Invoice Parser"

    def test_window_size(self, main_window: OCRMainWindow) -> None:
        """Test that the window has a reasonable size."""
        # The window should have a reasonable size for the content
        # Allow for system adjustments while ensuring minimum usability
        size = main_window.size()
        assert size.width() >= 800, f"Window width {size.width()} is too small"
        assert size.height() >= 600, f"Window height {size.height()} is too small"
        assert size.width() <= 2000, f"Window width {size.width()} is too large"
        assert size.height() <= 1500, f"Window height {size.height()} is too large"

    def test_tab_widget_exists(self, main_window: OCRMainWindow) -> None:
        """Test that the tab widget is created and accessible."""
        assert main_window.tab_widget is not None
        assert (
            main_window.tab_widget.count() == 6
        )  # Single PDF, File Naming, Projects, Business, Category, Settings

    def test_tab_names(self, main_window: OCRMainWindow) -> None:
        """Test that the correct tabs are created."""
        tab_names = [
            main_window.tab_widget.tabText(i)
            for i in range(main_window.tab_widget.count())
        ]
        assert "Single PDF" in tab_names
        assert "File Naming" in tab_names
        assert "Projects" in tab_names
        assert "Business" in tab_names
        assert "Categories" in tab_names
        assert "Settings" in tab_names

    def test_status_bar_exists(self, main_window: OCRMainWindow) -> None:
        """Test that the status bar is created and shows initial message."""
        assert main_window.status_bar is not None
        # The status bar should show either "Ready" or a backup message
        current_message = main_window.status_bar.currentMessage()
        assert "Ready" in current_message or "backup" in current_message.lower()

    def test_tab_switching(self, main_window: OCRMainWindow, qtbot: QtBot) -> None:
        """Test that switching tabs updates the status bar."""
        # Switch to the File Naming tab (index 1)
        main_window.tab_widget.setCurrentIndex(1)
        qtbot.wait(100)  # Small delay to allow signal processing

        # Check that status bar message was updated
        assert "File Naming" in main_window.status_bar.currentMessage()

    def test_menu_bar_exists(self, main_window: OCRMainWindow) -> None:
        """Test that the menu bar is created with expected menus."""
        menubar = main_window.menuBar()
        assert menubar is not None

        # Check that File and Help menus exist
        menu_titles = [
            menubar.actions()[i].text() for i in range(len(menubar.actions()))
        ]
        assert any("File" in title for title in menu_titles)
        assert any("Help" in title for title in menu_titles)

    def test_window_close(self, main_window: OCRMainWindow, qtbot: QtBot) -> None:
        """Test that the window can be closed properly."""
        # This test ensures the close event is handled without errors
        main_window.close()
        qtbot.wait(100)  # Small delay to allow close processing

    def test_edit_business_field_in_single_pdf_table(
        self, main_window: OCRMainWindow, qtbot: QtBot
    ) -> None:
        """Test editing the business field in the single PDF table, including adding a new business."""
        # Switch to Single PDF tab
        tab_names = [
            main_window.tab_widget.tabText(i)
            for i in range(main_window.tab_widget.count())
        ]
        single_pdf_index = tab_names.index("Single PDF")
        main_window.tab_widget.setCurrentIndex(single_pdf_index)
        qtbot.wait(100)

        # Simulate loading extracted data with a known business
        extracted_data = {
            "company": "Hydro Quebec",
            "total": 123.45,
            "date": "2024-07-16",
            "invoice_number": "INV-001",
            "parser_type": "invoice",
            "is_valid": True,
            "confidence": 0.95,
        }
        main_window.data_panel.update_data(extracted_data)
        qtbot.wait(100)

        # Find the business field cell (row 0, column 1)
        table = main_window.data_panel.data_table
        business_item = table.item(0, 1)
        assert business_item is not None

        # Double-click to edit (should show combo box)
        table.editItem(business_item)
        qtbot.wait(100)

        # Simulate selecting an existing business
        business_delegate = main_window.data_panel.business_delegate
        editor = business_delegate.createEditor(table, None, table.model().index(0, 1))
        editor.setCurrentText("Hydro Quebec")
        business_delegate.setModelData(editor, table.model(), table.model().index(0, 1))
        qtbot.wait(100)
        assert table.item(0, 1).text() == "Hydro Quebec"

        # Simulate adding a new business
        new_business = "New Test Business"
        editor.setCurrentText(new_business)
        # Simulate user confirming addition
        business_delegate._check_add_new(
            editor
        )  # Normally triggered by editingFinished
        business_delegate.setModelData(editor, table.model(), table.model().index(0, 1))
        qtbot.wait(100)
        assert table.item(0, 1).text() == new_business
