"""
Tests for OCR Main Window

Tests for the OCR GUI main window functionality.
"""

import pytest
from pytestqt.qtbot import QtBot

from ocrinvoice.gui.ocr_main_window import OCRMainWindow


@pytest.fixture
def main_window(qtbot: QtBot) -> OCRMainWindow:
    """Create a main window instance for testing."""
    window = OCRMainWindow()
    qtbot.addWidget(window)
    return window


class TestOCRMainWindow:
    """Test cases for the OCR Main Window."""

    def test_window_creation(self, main_window: OCRMainWindow) -> None:
        """Test that the main window can be created successfully."""
        assert main_window is not None
        assert main_window.windowTitle() == "OCR Invoice Parser"

    def test_window_size(self, main_window: OCRMainWindow) -> None:
        """Test that the window has the correct minimum size."""
        assert main_window.minimumSize().width() >= 1000
        assert main_window.minimumSize().height() >= 700

    def test_tab_widget_exists(self, main_window: OCRMainWindow) -> None:
        """Test that the tab widget is created and accessible."""
        assert main_window.tab_widget is not None
        assert main_window.tab_widget.count() == 2

    def test_tab_names(self, main_window: OCRMainWindow) -> None:
        """Test that the correct tabs are created."""
        tab_names = [
            main_window.tab_widget.tabText(i)
            for i in range(main_window.tab_widget.count())
        ]
        assert "Single PDF" in tab_names
        assert "Settings" in tab_names

    def test_status_bar_exists(self, main_window: OCRMainWindow) -> None:
        """Test that the status bar is created and shows initial message."""
        assert main_window.status_bar is not None
        assert main_window.status_bar.currentMessage() == "Ready"

    def test_tab_switching(self, main_window: OCRMainWindow, qtbot: QtBot) -> None:
        """Test that switching tabs updates the status bar."""
        # Switch to the second tab
        main_window.tab_widget.setCurrentIndex(1)
        qtbot.wait(100)  # Small delay to allow signal processing

        # Check that status bar message was updated
        assert "Settings" in main_window.status_bar.currentMessage()

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

    def test_about_dialog(self, main_window: OCRMainWindow, qtbot: QtBot) -> None:
        """Test that the about dialog can be triggered."""
        # Find the About action in the Help menu
        help_menu = main_window.menuBar().actions()[-1]  # Help menu is last
        help_menu.trigger()

        # Find and trigger the About action
        about_action = None
        for action in help_menu.menu().actions():
            if "About" in action.text():
                about_action = action
                break

        assert about_action is not None

        # Trigger the about action (this will show a dialog)
        about_action.trigger()
        qtbot.wait(100)  # Small delay to allow dialog to appear

    def test_window_close(self, main_window: OCRMainWindow, qtbot: QtBot) -> None:
        """Test that the window can be closed properly."""
        # This test ensures the close event is handled without errors
        main_window.close()
        qtbot.wait(100)  # Small delay to allow close processing
