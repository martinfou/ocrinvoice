"""
PDF Preview Widget

Displays PDF files in the GUI using pdf2image for rendering.
"""

import os
from typing import Optional
from PyQt6.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
    QScrollArea,
    QHBoxLayout,
    QPushButton,
    QSlider,
    QFrame,
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import (
    QPixmap,
    QImage,
    QKeySequence,
    QShortcut,
    QWheelEvent,
    QResizeEvent,
)
from pdf2image import convert_from_path


class PDFPreviewWidget(QWidget):
    """PDF Preview Widget with zoom and pan capabilities."""

    # Signal emitted when raw data button is clicked
    raw_data_requested = pyqtSignal()
    
    # Signal emitted when force OCR button is clicked
    force_ocr_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_pdf_path: Optional[str] = None
        self.original_pixmap: Optional[QPixmap] = None
        self.zoom_factor = 1.0
        self.min_zoom = 0.1
        self.max_zoom = 5.0
        self.zoom_step = 0.25
        self.fit_to_width_mode = False

        self._setup_ui()
        self._setup_shortcuts()

    def _setup_ui(self) -> None:
        """Set up the user interface."""
        # Create toolbar for zoom controls
        toolbar = QFrame()
        toolbar.setFrameStyle(QFrame.Shape.StyledPanel)
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(5, 5, 5, 5)

        # Zoom out button
        self.zoom_out_btn = QPushButton("−")
        self.zoom_out_btn.setToolTip("Zoom Out (Ctrl+-)")
        self.zoom_out_btn.setFixedSize(30, 30)
        self.zoom_out_btn.clicked.connect(self.zoom_out)

        # Zoom slider
        self.zoom_slider = QSlider(Qt.Orientation.Horizontal)
        self.zoom_slider.setMinimum(int(self.min_zoom * 100))
        self.zoom_slider.setMaximum(int(self.max_zoom * 100))
        self.zoom_slider.setValue(100)  # 100% = 1.0
        self.zoom_slider.setToolTip("Zoom Level")
        self.zoom_slider.valueChanged.connect(self._on_slider_changed)

        # Zoom in button
        self.zoom_in_btn = QPushButton("+")
        self.zoom_in_btn.setToolTip("Zoom In (Ctrl+=)")
        self.zoom_in_btn.setFixedSize(30, 30)
        self.zoom_in_btn.clicked.connect(self.zoom_in)

        # Reset zoom button
        self.reset_zoom_btn = QPushButton("100%")
        self.reset_zoom_btn.setToolTip("Reset to 100% (Ctrl+0)")
        self.reset_zoom_btn.clicked.connect(self.reset_zoom)

        # Fit to width button
        self.fit_width_btn = QPushButton("Fit Width")
        self.fit_width_btn.setToolTip("Fit to Width")
        self.fit_width_btn.setCheckable(True)
        self.fit_width_btn.clicked.connect(self.fit_to_width)

        # Raw data button
        self.raw_data_btn = QPushButton("📊 Raw Data")
        self.raw_data_btn.setToolTip("View complete raw data structure")
        self.raw_data_btn.clicked.connect(self._on_raw_data_clicked)

        # Force OCR button
        self.force_ocr_btn = QPushButton("🔄 Force OCR")
        self.force_ocr_btn.setToolTip("Force fresh OCR processing, ignoring saved metadata")
        self.force_ocr_btn.clicked.connect(self._on_force_ocr_clicked)
        self.force_ocr_btn.setEnabled(False)  # Disabled until PDF is loaded

        # Add controls to toolbar
        toolbar_layout.addWidget(self.zoom_out_btn)
        toolbar_layout.addWidget(self.zoom_slider)
        toolbar_layout.addWidget(self.zoom_in_btn)
        toolbar_layout.addWidget(self.reset_zoom_btn)
        toolbar_layout.addWidget(self.fit_width_btn)
        toolbar_layout.addWidget(self.raw_data_btn)
        toolbar_layout.addWidget(self.force_ocr_btn)
        toolbar_layout.addStretch()

        # Create scroll area for zooming
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(
            False
        )  # Keep this False for proper scrolling
        self.scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        self.scroll_area.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )

        # Create label for displaying PDF image
        self.pdf_label = QLabel()
        self.pdf_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pdf_label.setMinimumSize(400, 600)
        self.pdf_label.setStyleSheet("background: white; border: 1px solid #ccc;")

        # Set placeholder text
        self.pdf_label.setText("PDF Preview Area\n\nSelect a PDF file to preview")
        self.pdf_label.setStyleSheet(
            "background: white; border: 1px solid #ccc; color: #666; font-size: 14px;"
        )

        # Add label to scroll area
        self.scroll_area.setWidget(self.pdf_label)

        # Main layout - minimize margins to maximize space
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(toolbar)
        layout.addWidget(self.scroll_area)

    def _setup_shortcuts(self) -> None:
        """Set up keyboard shortcuts for zoom operations."""
        # Zoom in: Ctrl+= or Ctrl++
        zoom_in_shortcut = QShortcut(QKeySequence("Ctrl+="), self)
        zoom_in_shortcut.activated.connect(self.zoom_in)

        # Zoom out: Ctrl+-
        zoom_out_shortcut = QShortcut(QKeySequence("Ctrl+-"), self)
        zoom_out_shortcut.activated.connect(self.zoom_out)

        # Reset zoom: Ctrl+0
        reset_zoom_shortcut = QShortcut(QKeySequence("Ctrl+0"), self)
        reset_zoom_shortcut.activated.connect(self.reset_zoom)

        # Mouse wheel zoom
        self.scroll_area.wheelEvent = self._wheel_event

    def resizeEvent(self, event: QResizeEvent) -> None:
        """Handle resize events to maintain fit-to-width mode."""
        super().resizeEvent(event)
        if self.fit_to_width_mode and self.original_pixmap:
            # Recalculate fit-to-width when window is resized
            self._update_fit_to_width()

    def showEvent(self, event) -> None:
        """Handle show events to ensure proper fit-to-width calculation."""
        super().showEvent(event)
        if self.fit_to_width_mode and self.original_pixmap:
            # Recalculate fit-to-width when widget is shown
            self._update_fit_to_width()

    def _wheel_event(self, event: QWheelEvent) -> None:
        """Handle mouse wheel events for zooming."""
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            # Zoom with Ctrl+Wheel
            delta = event.angleDelta().y()
            if delta > 0:
                self.zoom_in()
            else:
                self.zoom_out()
            event.accept()
        else:
            # Normal scrolling - delegate to scroll area
            super(QScrollArea, self.scroll_area).wheelEvent(event)

    def _on_slider_changed(self, value: int) -> None:
        """Handle zoom slider changes."""
        new_zoom = value / 100.0
        if new_zoom != self.zoom_factor:
            self.zoom_factor = new_zoom
            self.fit_to_width_mode = False
            self.fit_width_btn.setChecked(False)
            self._update_zoom()

    def zoom_in(self) -> None:
        """Zoom in by one step."""
        new_zoom = min(self.zoom_factor + self.zoom_step, self.max_zoom)
        self._set_zoom(new_zoom)

    def zoom_out(self) -> None:
        """Zoom out by one step."""
        new_zoom = max(self.zoom_factor - self.zoom_step, self.min_zoom)
        self._set_zoom(new_zoom)

    def reset_zoom(self) -> None:
        """Reset zoom to 100%."""
        self._set_zoom(1.0)

    def fit_to_width(self) -> None:
        """Toggle fit-to-width mode."""
        if self.fit_width_btn.isChecked():
            self.fit_to_width_mode = True
            # Use a timer to ensure the widget has fully rendered
            QTimer.singleShot(50, self._update_fit_to_width)
        else:
            self.fit_to_width_mode = False
            self._update_zoom()

    def _update_fit_to_width(self) -> None:
        """Update fit-to-width zoom level."""
        if not self.original_pixmap:
            return

        # Get the full available width of the scroll area viewport
        scroll_width = self.scroll_area.viewport().width()
        pdf_width = self.original_pixmap.width()

        if pdf_width > 0 and scroll_width > 0:
            # Calculate zoom to fit the full width
            new_zoom = scroll_width / pdf_width
            new_zoom = max(self.min_zoom, min(new_zoom, self.max_zoom))
            self.zoom_factor = new_zoom
            self.zoom_slider.setValue(int(self.zoom_factor * 100))
            self._update_zoom()

    def _set_zoom(self, zoom_factor: float) -> None:
        """Set zoom factor and update UI."""
        self.zoom_factor = max(self.min_zoom, min(zoom_factor, self.max_zoom))
        self.zoom_slider.setValue(int(self.zoom_factor * 100))
        self.fit_to_width_mode = False
        self.fit_width_btn.setChecked(False)
        self._update_zoom()

    def _update_zoom(self) -> None:
        """Update the displayed image with current zoom factor."""
        if not self.original_pixmap:
            return

        # Calculate new size
        original_size = self.original_pixmap.size()
        new_size = original_size * self.zoom_factor

        # Scale the pixmap
        scaled_pixmap = self.original_pixmap.scaled(
            new_size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )

        # Update the label with the scaled pixmap
        self.pdf_label.setPixmap(scaled_pixmap)

        # Set the label size to match the scaled pixmap size to enable proper scrolling
        self.pdf_label.setFixedSize(scaled_pixmap.size())

        # Update button states
        self.zoom_in_btn.setEnabled(self.zoom_factor < self.max_zoom)
        self.zoom_out_btn.setEnabled(self.zoom_factor > self.min_zoom)

        # Update reset button text
        self.reset_zoom_btn.setText(f"{int(self.zoom_factor * 100)}%")

    def load_pdf(self, pdf_path: str) -> bool:
        """Load and display a PDF file."""
        try:
            if not os.path.exists(pdf_path):
                self._show_error("PDF file not found")
                return False

            # Convert first page to image
            images = convert_from_path(pdf_path, first_page=1, last_page=1)
            if not images:
                self._show_error("Could not convert PDF to image")
                return False

            # Convert PIL image to QPixmap
            pil_image = images[0]
            qimage = QImage(
                pil_image.tobytes(),
                pil_image.width,
                pil_image.height,
                pil_image.width * 3,  # RGB
                QImage.Format.Format_RGB888,
            )

            # Store original pixmap and reset zoom
            self.original_pixmap = QPixmap.fromImage(qimage)
            self.current_pdf_path = pdf_path

            # Reset zoom and fit to width initially
            self.reset_zoom()
            self.fit_to_width_mode = True
            self.fit_width_btn.setChecked(True)
            # Use a timer to ensure the widget has fully rendered before calculating fit-to-width
            QTimer.singleShot(100, self._update_fit_to_width)

            # Enable Force OCR button
            self.force_ocr_btn.setEnabled(True)

            return True

        except Exception as e:
            self._show_error(f"Error loading PDF: {str(e)}")
            return False

    def _show_error(self, message: str) -> None:
        """Show error message in the preview area."""
        self.pdf_label.setText(f"Error: {message}")
        self.pdf_label.setStyleSheet(
            "background: #ffe6e6; border: 1px solid #ff9999; color: #cc0000; font-size: 12px;"
        )
        # Reset label size to minimum for error display
        self.pdf_label.setFixedSize(self.pdf_label.minimumSize())
        self.current_pdf_path = None
        self.original_pixmap = None

    def clear(self) -> None:
        """Clear the preview area."""
        self.pdf_label.setText("PDF Preview Area\n\nSelect a PDF file to preview")
        self.pdf_label.setStyleSheet(
            "background: white; border: 1px solid #ccc; color: #666; font-size: 14px;"
        )
        # Reset label size to minimum for placeholder display
        self.pdf_label.setFixedSize(self.pdf_label.minimumSize())
        self.current_pdf_path = None
        self.original_pixmap = None
        self.fit_to_width_mode = False
        self.fit_width_btn.setChecked(False)
        self.reset_zoom()
        
        # Disable Force OCR button
        self.force_ocr_btn.setEnabled(False)

    def _on_raw_data_clicked(self) -> None:
        """Handle raw data button click."""
        self.raw_data_requested.emit()

    def _on_force_ocr_clicked(self) -> None:
        """Handle force OCR button click."""
        self.force_ocr_requested.emit()
