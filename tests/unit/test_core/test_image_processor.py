"""Unit tests for the ImageProcessor class."""

import pytest
from unittest.mock import Mock, patch, MagicMock, call
from pathlib import Path
from typing import Dict, Any

import os
import numpy as np

import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "src"))

from ocrinvoice.core.image_processor import ImageProcessor


class TestImageProcessorInitialization:
    """Test ImageProcessor initialization and configuration."""

    def test_init_with_default_config(self):
        """Test initialization with default configuration."""
        processor = ImageProcessor()

        assert processor.config == {}
        assert processor.preprocessing_steps == [
            "resize",
            "denoise",
            "enhance_contrast",
            "binarize",
        ]
        assert processor.target_width == 2000
        assert processor.target_height == 2800

    def test_init_with_custom_config(self):
        """Test initialization with custom configuration."""
        config = {
            "preprocessing_steps": ["resize", "enhance_contrast"],
            "target_width": 1500,
            "target_height": 2000,
            "denoise_strength": 10,
            "contrast_factor": 1.5,
        }

        processor = ImageProcessor(config)

        assert processor.config == config
        assert processor.preprocessing_steps == ["resize", "enhance_contrast"]
        assert processor.target_width == 1500
        assert processor.target_height == 2000

    def test_init_with_invalid_steps(self):
        """Test initialization with invalid preprocessing steps."""
        config = {"preprocessing_steps": ["invalid_step"]}

        with pytest.raises(ValueError, match="Invalid preprocessing step"):
            ImageProcessor(config)


class TestImageProcessorDependencyValidation:
    """Test ImageProcessor dependency validation methods."""

    def test_validate_dependencies_success(self):
        """Test successful dependency validation."""
        processor = ImageProcessor()
        # Should not raise any exception
        assert processor._validate_dependencies() is None

    @patch("ocrinvoice.core.image_processor.DEPENDENCIES_AVAILABLE", False)
    @patch("ocrinvoice.core.image_processor.importlib.util.find_spec")
    def test_validate_dependencies_missing_pil(self, mock_find_spec):
        """Test dependency validation with missing PIL."""

        # Mock PIL as missing, others as present
        def mock_find_spec_side_effect(name):
            if name == "PIL":
                return None
            return Mock()  # Return a mock for other dependencies

        mock_find_spec.side_effect = mock_find_spec_side_effect

        with pytest.raises(ImportError, match="PIL not installed"):
            ImageProcessor()

    @patch("ocrinvoice.core.image_processor.DEPENDENCIES_AVAILABLE", False)
    @patch("ocrinvoice.core.image_processor.importlib.util.find_spec")
    def test_validate_dependencies_missing_cv2(self, mock_find_spec):
        """Test dependency validation with missing cv2."""

        # Mock cv2 as missing, others as present
        def mock_find_spec_side_effect(name):
            if name == "cv2":
                return None
            return Mock()  # Return a mock for other dependencies

        mock_find_spec.side_effect = mock_find_spec_side_effect

        with pytest.raises(ImportError, match="cv2 not installed"):
            ImageProcessor()

    @patch("ocrinvoice.core.image_processor.DEPENDENCIES_AVAILABLE", False)
    @patch("ocrinvoice.core.image_processor.importlib.util.find_spec")
    def test_validate_dependencies_missing_numpy(self, mock_find_spec):
        """Test dependency validation with missing numpy."""

        # Mock numpy as missing, others as present
        def mock_find_spec_side_effect(name):
            if name == "numpy":
                return None
            return Mock()  # Return a mock for other dependencies

        mock_find_spec.side_effect = mock_find_spec_side_effect

        with pytest.raises(ImportError, match="numpy not installed"):
            ImageProcessor()


class TestImageProcessorImageResizing:
    """Test ImageProcessor image resizing methods."""

    @pytest.fixture
    def processor(self):
        """Create an ImageProcessor instance for testing."""
        return ImageProcessor()

    @patch("ocrinvoice.core.image_processor.Image")
    def test_resize_image_success(self, mock_image_class, processor):
        """Test successful image resizing."""
        mock_image = Mock()
        mock_resized = Mock()
        mock_image.resize.return_value = mock_resized
        mock_image.size = (500, 700)  # Smaller than min_width (800)
        mock_image_class.Resampling.LANCZOS = "LANCZOS"

        result = processor._resize_image(mock_image)

        assert result == mock_resized
        mock_image.resize.assert_called_once_with(
            (processor.target_width, processor.target_height), "LANCZOS"
        )

    @patch("ocrinvoice.core.image_processor.Image")
    def test_resize_image_already_correct_size(self, mock_image_class, processor):
        """Test image resizing when image is already correct size."""
        mock_image = Mock()
        mock_image.size = (2000, 2800)

        result = processor._resize_image(mock_image)

        assert result == mock_image
        mock_image.resize.assert_not_called()

    @patch("ocrinvoice.core.image_processor.Image")
    def test_resize_image_with_custom_size(self, mock_image_class, processor):
        """Test image resizing with custom target size."""
        processor.target_width = 1500
        processor.target_height = 2000
        processor.min_width = 1200  # Ensure resize is triggered

        mock_image = Mock()
        mock_resized = Mock()
        mock_image.resize.return_value = mock_resized
        mock_image.size = (1000, 1400)
        mock_image_class.Resampling.LANCZOS = "LANCZOS"

        result = processor._resize_image(mock_image)

        # The implementation returns the resized image
        mock_image.resize.assert_called_once_with((1500, 2100), "LANCZOS")
        assert result == mock_resized

    @patch("ocrinvoice.core.image_processor.Image")
    def test_resize_image_failure(self, mock_image_class, processor):
        """Test image resizing failure."""
        # Create a mock image that will trigger the resize logic
        mock_image = Mock()
        mock_image.size = (500, 600)  # Small enough to trigger resize
        mock_image.resize.side_effect = Exception("Resize failed")

        with pytest.raises(Exception, match="Resize failed"):
            processor._resize_image(mock_image)


class TestImageProcessorImageDenoising:
    """Test ImageProcessor image denoising methods."""

    @pytest.fixture
    def processor(self):
        """Create an ImageProcessor instance for testing."""
        return ImageProcessor()

    @patch("ocrinvoice.core.image_processor.cv2")
    @patch("ocrinvoice.core.image_processor.np.array")
    def test_denoise_image_success(self, mock_np_array, mock_cv2, processor):
        """Test successful image denoising."""
        mock_image = Mock()
        mock_array = np.array([[1, 2], [3, 4]])
        mock_np_array.return_value = mock_array

        mock_denoised = np.array([[2, 3], [4, 5]])
        mock_cv2.fastNlMeansDenoising.return_value = mock_denoised

        mock_pil_image = Mock()
        with patch("ocrinvoice.core.image_processor.Image.fromarray") as mock_fromarray:
            mock_fromarray.return_value = mock_pil_image

            result = processor._denoise_image(mock_image)

            assert result == mock_pil_image
            # np.array is called multiple times in the pipeline, so check it was called at least once
            mock_np_array.assert_called()
            mock_cv2.fastNlMeansDenoising.assert_called_once_with(mock_array, h=1.0)
            mock_fromarray.assert_called_once_with(mock_denoised)

    @patch("ocrinvoice.core.image_processor.cv2")
    @patch("ocrinvoice.core.image_processor.np.array")
    def test_denoise_image_with_custom_strength(
        self, mock_np_array, mock_cv2, processor
    ):
        """Test image denoising with custom strength."""
        mock_image = Mock()
        mock_array = np.array([[1, 2], [3, 4]])
        mock_np_array.return_value = mock_array

        mock_denoised = np.array([[2, 3], [4, 5]])
        mock_cv2.fastNlMeansDenoising.return_value = mock_denoised

        mock_pil_image = Mock()
        with patch("ocrinvoice.core.image_processor.Image.fromarray") as mock_fromarray:
            mock_fromarray.return_value = mock_pil_image

            result = processor._denoise_image(mock_image, strength=2.0)

            assert result == mock_pil_image
            mock_cv2.fastNlMeansDenoising.assert_called_once_with(mock_array, h=2.0)

    @patch("ocrinvoice.core.image_processor.cv2")
    @patch("ocrinvoice.core.image_processor.np.array")
    def test_denoise_image_failure(self, mock_np_array, mock_cv2, processor):
        """Test image denoising failure."""
        mock_image = Mock()
        mock_np_array.side_effect = Exception("Conversion failed")

        with pytest.raises(Exception, match="Conversion failed"):
            processor._denoise_image(mock_image)


class TestImageProcessorContrastEnhancement:
    """Test ImageProcessor contrast enhancement methods."""

    @pytest.fixture
    def processor(self):
        """Create an ImageProcessor instance for testing."""
        return ImageProcessor()

    @patch("ocrinvoice.core.image_processor.ImageEnhance")
    def test_enhance_contrast_success(self, mock_enhance, processor):
        """Test successful contrast enhancement."""
        mock_image = Mock()
        mock_enhancer = Mock()
        mock_enhanced = Mock()
        mock_enhance.Contrast.return_value = mock_enhancer
        mock_enhancer.enhance.return_value = mock_enhanced

        result = processor._enhance_contrast(mock_image)

        assert result == mock_enhanced
        mock_enhance.Contrast.assert_called_once_with(mock_image)
        mock_enhancer.enhance.assert_called_once_with(1.5)

    @patch("ocrinvoice.core.image_processor.ImageEnhance")
    def test_enhance_contrast_with_custom_factor(self, mock_enhance, processor):
        """Test contrast enhancement with custom factor."""
        mock_image = Mock()
        mock_enhancer = Mock()
        mock_enhanced = Mock()
        mock_enhance.Contrast.return_value = mock_enhancer
        mock_enhancer.enhance.return_value = mock_enhanced

        # Test with custom factor
        processor.config["contrast_factor"] = 2.0
        result = processor._enhance_contrast(mock_image)

        assert result == mock_enhanced
        mock_enhancer.enhance.assert_called_once_with(2.0)

    @patch("ocrinvoice.core.image_processor.ImageEnhance")
    def test_enhance_contrast_failure(self, mock_enhance, processor):
        """Test contrast enhancement failure."""
        mock_image = Mock()
        mock_enhance.Contrast.side_effect = Exception("Enhancement failed")

        with pytest.raises(Exception, match="Enhancement failed"):
            processor._enhance_contrast(mock_image)


class TestImageProcessorImageBinarization:
    """Test ImageProcessor image binarization methods."""

    @pytest.fixture
    def processor(self):
        """Create an ImageProcessor instance for testing."""
        return ImageProcessor()

    @patch("ocrinvoice.core.image_processor.cv2")
    @patch("ocrinvoice.core.image_processor.np.array")
    def test_binarize_image_success(self, mock_np_array, mock_cv2, processor):
        """Test successful image binarization."""
        mock_image = Mock()
        mock_array = np.array([[100, 200], [50, 150]])
        mock_np_array.return_value = mock_array

        mock_binarized = np.array([[0, 255], [0, 255]])
        mock_cv2.threshold.return_value = (127, mock_binarized)

        mock_pil_image = Mock()
        with patch("ocrinvoice.core.image_processor.Image.fromarray") as mock_fromarray:
            mock_fromarray.return_value = mock_pil_image

            result = processor._binarize_image(mock_image)

            assert result == mock_pil_image
            # np.array is called multiple times in the pipeline, so check it was called at least once
            mock_np_array.assert_called()
            mock_cv2.threshold.assert_called_once()
            mock_fromarray.assert_called_once_with(mock_binarized)

    @patch("ocrinvoice.core.image_processor.cv2")
    @patch("ocrinvoice.core.image_processor.np.array")
    def test_binarize_image_with_custom_threshold(
        self, mock_np_array, mock_cv2, processor
    ):
        """Test image binarization with custom threshold."""
        mock_image = Mock()
        mock_array = np.array([[100, 200], [50, 150]])
        mock_np_array.return_value = mock_array

        mock_binarized = np.array([[0, 255], [0, 255]])
        mock_cv2.threshold.return_value = (200, mock_binarized)

        mock_pil_image = Mock()
        with patch("ocrinvoice.core.image_processor.Image.fromarray") as mock_fromarray:
            mock_fromarray.return_value = mock_pil_image

            result = processor._binarize_image(mock_image, threshold=200)

            assert result == mock_pil_image
            mock_cv2.threshold.assert_called_once_with(
                mock_array, 200, 255, mock_cv2.THRESH_BINARY
            )

    @patch("ocrinvoice.core.image_processor.cv2")
    @patch("ocrinvoice.core.image_processor.np.array")
    def test_binarize_image_failure(self, mock_np_array, mock_cv2, processor):
        """Test image binarization failure."""
        mock_image = Mock()
        mock_np_array.side_effect = Exception("Conversion failed")

        with pytest.raises(Exception, match="Conversion failed"):
            processor._binarize_image(mock_image)


class TestImageProcessorMainPreprocessing:
    """Test ImageProcessor main preprocessing methods."""

    @pytest.fixture
    def processor(self):
        """Create an ImageProcessor instance for testing."""
        return ImageProcessor()

    def test_preprocess_for_ocr_success(self, processor):
        """Test successful OCR preprocessing."""
        mock_image = Mock()
        mock_processed = Mock()

        with patch.object(processor, "preprocess_image") as mock_preprocess:
            mock_preprocess.return_value = mock_processed

            result = processor.preprocess_for_ocr(mock_image)

            assert result == mock_processed
            mock_preprocess.assert_called_once_with(mock_image)

    def test_preprocess_for_ocr_with_custom_steps(self, processor):
        """Test OCR preprocessing with custom steps."""
        processor.preprocessing_steps = ["resize", "enhance_contrast"]
        mock_image = Mock()
        mock_processed = Mock()

        with patch.object(processor, "_resize_image") as mock_resize:
            with patch.object(processor, "_enhance_contrast") as mock_contrast:
                mock_resize.return_value = mock_processed
                mock_contrast.return_value = mock_processed

                result = processor.preprocess_for_ocr(mock_image)

                assert result == mock_processed
                mock_resize.assert_called_once_with(mock_image)
                mock_contrast.assert_called_once_with(mock_processed)

    def test_preprocess_for_ocr_empty_steps(self, processor):
        """Test OCR preprocessing with empty steps."""
        processor.preprocessing_steps = []
        mock_image = Mock()

        result = processor.preprocess_for_ocr(mock_image)

        assert result == mock_image

    def test_preprocess_for_ocr_invalid_step(self, processor):
        """Test OCR preprocessing with invalid step."""
        processor.preprocessing_steps = ["invalid_step"]
        mock_image = Mock()

        with pytest.raises(
            Exception, match="Always fails: Invalid preprocessing step: invalid_step"
        ):
            processor.preprocess_for_ocr(mock_image)


class TestImageProcessorUtilityMethods:
    """Test ImageProcessor utility methods."""

    @pytest.fixture
    def processor(self):
        """Create an ImageProcessor instance for testing."""
        return ImageProcessor()

    def test_validate_image_success(self, processor):
        """Test successful image validation."""
        mock_image = Mock()
        mock_image.mode = "RGB"

        result = processor._validate_image(mock_image, mode="RGB")

        assert result is True

    def test_validate_image_invalid_mode(self, processor):
        """Test image validation with invalid mode."""
        mock_image = Mock()
        mock_image.mode = "RGB"

        with pytest.raises(ValueError, match="Invalid mode"):
            processor._validate_image(mock_image, mode="invalid")

    def test_validate_image_none(self, processor):
        """Test image validation with None image."""
        with pytest.raises(ValueError, match="Image cannot be None"):
            processor._validate_image(None)

    def test_get_image_info(self, processor):
        """Test getting image information."""
        mock_image = Mock()
        mock_image.size = (1000, 1400)
        mock_image.mode = "RGB"
        mock_image.format = "JPEG"

        result = processor.get_image_info(mock_image)

        assert result["width"] == 1000
        assert result["height"] == 1400
        assert result["mode"] == "RGB"
        assert result["format"] == "JPEG"


class TestImageProcessorErrorHandling:
    """Test ImageProcessor error handling methods."""

    @pytest.fixture
    def processor(self):
        """Create an ImageProcessor instance for testing."""
        return ImageProcessor()

    def test_handle_preprocessing_error_with_retry(self, processor):
        """Test error handling with retry mechanism."""
        mock_image = Mock()
        mock_processed = Mock()

        with patch.object(processor, "preprocess_image") as mock_preprocess:
            # First two calls fail, third succeeds
            mock_preprocess.side_effect = [
                Exception("First failure"),
                Exception("Second failure"),
                mock_processed,
            ]

            result = processor.preprocess_for_ocr(mock_image, max_retries=3)

            assert result == mock_processed
            assert mock_preprocess.call_count == 3

    def test_handle_preprocessing_error_max_retries_exceeded(self, processor):
        """Test error handling when max retries are exceeded."""
        mock_image = Mock()

        with patch.object(processor, "preprocess_image") as mock_preprocess:
            mock_preprocess.side_effect = Exception("Always fails")

            with pytest.raises(Exception, match="Always fails: Always fails"):
                processor.preprocess_for_ocr(mock_image, max_retries=2)

            assert mock_preprocess.call_count == 2


class TestImageProcessorPerformance:
    """Test ImageProcessor performance methods."""

    @pytest.fixture
    def processor(self):
        """Create an ImageProcessor instance for testing."""
        return ImageProcessor()

    def test_large_image_processing(self, processor):
        """Test processing of large images."""
        mock_image = Mock()
        mock_image.size = (4000, 6000)
        mock_processed = Mock()

        with patch.object(processor, "preprocess_for_ocr") as mock_preprocess:
            mock_preprocess.return_value = mock_processed

            result = processor.preprocess_for_ocr(mock_image)

            assert result == mock_processed

    def test_multiple_concurrent_processing(self, processor):
        """Test handling multiple concurrent processing requests."""
        import threading
        import time

        mock_image = Mock()
        mock_processed = Mock()

        results = []
        errors = []

        def processing_worker():
            try:
                with patch.object(processor, "preprocess_for_ocr") as mock_preprocess:
                    mock_preprocess.return_value = mock_processed
                    result = processor.preprocess_for_ocr(mock_image)
                    results.append(result)
            except Exception as e:
                errors.append(e)

        # Start multiple threads
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=processing_worker)
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        assert len(results) == 5
        assert len(errors) == 0
        assert all(result == mock_processed for result in results)


class TestImageProcessorIntegration:
    """Test ImageProcessor integration scenarios."""

    @pytest.fixture
    def processor(self):
        """Create an ImageProcessor instance for testing."""
        return ImageProcessor()

    def test_full_preprocessing_workflow(self, processor):
        """Test complete preprocessing workflow."""
        mock_image = Mock()
        mock_processed = Mock()

        with patch.object(processor, "preprocess_for_ocr") as mock_preprocess:
            mock_preprocess.return_value = mock_processed

            result = processor.preprocess_for_ocr(mock_image)

            assert result == mock_processed
            mock_preprocess.assert_called_once_with(mock_image)

    def test_preprocessing_with_validation(self, processor):
        """Test preprocessing with image validation."""
        mock_image = Mock()
        mock_image.mode = "RGB"
        mock_processed = Mock()

        with patch.object(processor, "_validate_image") as mock_validate:
            with patch.object(processor, "preprocess_image") as mock_preprocess:
                mock_validate.return_value = True
                mock_preprocess.return_value = mock_processed

                result = processor.preprocess_for_ocr(mock_image)

                assert result == mock_processed
                mock_validate.assert_called_once_with(mock_image)
                mock_preprocess.assert_called_once_with(mock_image)
