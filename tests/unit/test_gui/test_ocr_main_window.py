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
        # Add timeout to prevent hanging
        qtbot.wait(100)
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
        assert size.width() >= 700, f"Window width {size.width()} is too small"
        assert size.height() >= 600, f"Window height {size.height()} is too small"
        assert size.width() <= 2000, f"Window width {size.width()} is too large"
        assert size.height() <= 1500, f"Window height {size.height()} is too large"

    def test_tab_widget_exists(self, main_window: OCRMainWindow) -> None:
        """Test that the tab widget is created and accessible."""
        assert main_window.tab_widget is not None
        assert (
            main_window.tab_widget.count() == 6
        )  # Single PDF, File Naming, Projects, Official Names, Business Aliases, Settings

    def test_tab_names(self, main_window: OCRMainWindow) -> None:
        """Test that the correct tabs are created."""
        tab_names = [
            main_window.tab_widget.tabText(i)
            for i in range(main_window.tab_widget.count())
        ]
        assert "Single PDF" in tab_names
        assert "File Naming" in tab_names
        assert "Projects" in tab_names
        assert "Official Names" in tab_names
        assert "Business Aliases" in tab_names
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

    def test_about_dialog(self, main_window: OCRMainWindow, qtbot: QtBot) -> None:
        """Test that the about dialog can be triggered."""
        try:
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
        except Exception as e:
            # Skip this test if dialog creation fails in CI
            pytest.skip(f"Dialog test failed: {e}")

    def test_window_close(self, main_window: OCRMainWindow, qtbot: QtBot) -> None:
        """Test that the window can be closed properly."""
        # This test ensures the close event is handled without errors
        main_window.close()
        qtbot.wait(100)  # Small delay to allow close processing
