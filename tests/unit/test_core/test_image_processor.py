"""Unit tests for the ImageProcessor class."""

import pytest
from unittest.mock import Mock, patch, MagicMock, call
from pathlib import Path
from typing import Dict, Any
import tempfile
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
        with patch(
            "ocrinvoice.core.image_processor.importlib.util.find_spec"
        ) as mock_find_spec:
            mock_find_spec.return_value = Mock()

            processor = ImageProcessor()
            # Should not raise any exception
            assert processor._validate_dependencies() is None

    @patch("ocrinvoice.core.image_processor.importlib.util.find_spec")
    def test_validate_dependencies_missing_pil(self, mock_find_spec):
        """Test dependency validation with missing PIL."""

        def side_effect(name):
            if name == "PIL":
                return None
            return Mock()

        mock_find_spec.side_effect = side_effect

        with pytest.raises(ImportError, match="PIL not installed"):
            ImageProcessor()

    @patch("ocrinvoice.core.image_processor.importlib.util.find_spec")
    def test_validate_dependencies_missing_cv2(self, mock_find_spec):
        """Test dependency validation with missing cv2."""

        def side_effect(name):
            if name == "cv2":
                return None
            return Mock()

        mock_find_spec.side_effect = side_effect

        with pytest.raises(ImportError, match="cv2 not installed"):
            ImageProcessor()

    @patch("ocrinvoice.core.image_processor.importlib.util.find_spec")
    def test_validate_dependencies_missing_numpy(self, mock_find_spec):
        """Test dependency validation with missing numpy."""

        def side_effect(name):
            if name == "numpy":
                return None
            return Mock()

        mock_find_spec.side_effect = side_effect

        with pytest.raises(ImportError, match="numpy not installed"):
            ImageProcessor()


class TestImageProcessorImageResizing:
    """Test ImageProcessor image resizing methods."""

    @pytest.fixture
    def processor(self):
        """Create an ImageProcessor instance for testing."""
        return ImageProcessor()

    @patch("ocrinvoice.core.image_processor.PIL.Image")
    def test_resize_image_success(self, mock_pil, processor):
        """Test successful image resizing."""
        mock_image = Mock()
        mock_resized = Mock()
        mock_image.resize.return_value = mock_resized
        mock_image.size = (1000, 1400)

        result = processor._resize_image(mock_image)

        assert result == mock_resized
        mock_image.resize.assert_called_once_with((2000, 2800), mock_pil.Image.LANCZOS)

    @patch("ocrinvoice.core.image_processor.PIL.Image")
    def test_resize_image_already_correct_size(self, mock_pil, processor):
        """Test image resizing when image is already correct size."""
        mock_image = Mock()
        mock_image.size = (2000, 2800)

        result = processor._resize_image(mock_image)

        assert result == mock_image
        mock_image.resize.assert_not_called()

    @patch("ocrinvoice.core.image_processor.PIL.Image")
    def test_resize_image_with_custom_size(self, mock_pil, processor):
        """Test image resizing with custom target size."""
        processor.target_width = 1500
        processor.target_height = 2000

        mock_image = Mock()
        mock_resized = Mock()
        mock_image.resize.return_value = mock_resized
        mock_image.size = (1000, 1400)

        result = processor._resize_image(mock_image)

        assert result == mock_resized
        mock_image.resize.assert_called_once_with((1500, 2000), mock_pil.Image.LANCZOS)

    @patch("ocrinvoice.core.image_processor.PIL.Image")
    def test_resize_image_failure(self, mock_pil, processor):
        """Test image resizing failure."""
        mock_image = Mock()
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
        with patch(
            "ocrinvoice.core.image_processor.PIL.Image.fromarray"
        ) as mock_fromarray:
            mock_fromarray.return_value = mock_pil_image

            result = processor._denoise_image(mock_image)

            assert result == mock_pil_image
            mock_cv2.fastNlMeansDenoising.assert_called_once_with(
                mock_array, None, 10, 7, 21
            )

    @patch("ocrinvoice.core.image_processor.cv2")
    @patch("ocrinvoice.core.image_processor.np.array")
    def test_denoise_image_with_custom_strength(
        self, mock_np_array, mock_cv2, processor
    ):
        """Test image denoising with custom strength."""
        processor.config = {"denoise_strength": 15}

        mock_image = Mock()
        mock_array = np.array([[1, 2], [3, 4]])
        mock_np_array.return_value = mock_array

        mock_denoised = np.array([[2, 3], [4, 5]])
        mock_cv2.fastNlMeansDenoising.return_value = mock_denoised

        mock_pil_image = Mock()
        with patch(
            "ocrinvoice.core.image_processor.PIL.Image.fromarray"
        ) as mock_fromarray:
            mock_fromarray.return_value = mock_pil_image

            result = processor._denoise_image(mock_image)

            assert result == mock_pil_image
            mock_cv2.fastNlMeansDenoising.assert_called_once_with(
                mock_array, None, 15, 7, 21
            )

    @patch("ocrinvoice.core.image_processor.cv2")
    @patch("ocrinvoice.core.image_processor.np.array")
    def test_denoise_image_failure(self, mock_np_array, mock_cv2, processor):
        """Test image denoising failure."""
        mock_image = Mock()
        mock_array = np.array([[1, 2], [3, 4]])
        mock_np_array.return_value = mock_array

        mock_cv2.fastNlMeansDenoising.side_effect = Exception("Denoising failed")

        with pytest.raises(Exception, match="Denoising failed"):
            processor._denoise_image(mock_image)


class TestImageProcessorContrastEnhancement:
    """Test ImageProcessor contrast enhancement methods."""

    @pytest.fixture
    def processor(self):
        """Create an ImageProcessor instance for testing."""
        return ImageProcessor()

    @patch("ocrinvoice.core.image_processor.cv2")
    @patch("ocrinvoice.core.image_processor.np.array")
    def test_enhance_contrast_success(self, mock_np_array, mock_cv2, processor):
        """Test successful contrast enhancement."""
        mock_image = Mock()
        mock_array = np.array([[1, 2], [3, 4]])
        mock_np_array.return_value = mock_array

        mock_enhanced = np.array([[2, 4], [6, 8]])
        mock_cv2.convertScaleAbs.return_value = mock_enhanced

        mock_pil_image = Mock()
        with patch(
            "ocrinvoice.core.image_processor.PIL.Image.fromarray"
        ) as mock_fromarray:
            mock_fromarray.return_value = mock_pil_image

            result = processor._enhance_contrast(mock_image)

            assert result == mock_pil_image
            mock_cv2.convertScaleAbs.assert_called_once_with(
                mock_array, alpha=1.2, beta=0
            )

    @patch("ocrinvoice.core.image_processor.cv2")
    @patch("ocrinvoice.core.image_processor.np.array")
    def test_enhance_contrast_with_custom_factor(
        self, mock_np_array, mock_cv2, processor
    ):
        """Test contrast enhancement with custom factor."""
        processor.config = {"contrast_factor": 1.5}

        mock_image = Mock()
        mock_array = np.array([[1, 2], [3, 4]])
        mock_np_array.return_value = mock_array

        mock_enhanced = np.array([[2, 4], [6, 8]])
        mock_cv2.convertScaleAbs.return_value = mock_enhanced

        mock_pil_image = Mock()
        with patch(
            "ocrinvoice.core.image_processor.PIL.Image.fromarray"
        ) as mock_fromarray:
            mock_fromarray.return_value = mock_pil_image

            result = processor._enhance_contrast(mock_image)

            assert result == mock_pil_image
            mock_cv2.convertScaleAbs.assert_called_once_with(
                mock_array, alpha=1.5, beta=0
            )

    @patch("ocrinvoice.core.image_processor.cv2")
    @patch("ocrinvoice.core.image_processor.np.array")
    def test_enhance_contrast_failure(self, mock_np_array, mock_cv2, processor):
        """Test contrast enhancement failure."""
        mock_image = Mock()
        mock_array = np.array([[1, 2], [3, 4]])
        mock_np_array.return_value = mock_array

        mock_cv2.convertScaleAbs.side_effect = Exception("Enhancement failed")

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
        mock_array = np.array([[100, 150], [200, 250]])
        mock_np_array.return_value = mock_array

        mock_binary = np.array([[0, 0], [255, 255]])
        mock_cv2.threshold.return_value = (127.0, mock_binary)

        mock_pil_image = Mock()
        with patch(
            "ocrinvoice.core.image_processor.PIL.Image.fromarray"
        ) as mock_fromarray:
            mock_fromarray.return_value = mock_pil_image

            result = processor._binarize_image(mock_image)

            assert result == mock_pil_image
            mock_cv2.threshold.assert_called_once_with(
                mock_array, 0, 255, mock_cv2.THRESH_BINARY + mock_cv2.THRESH_OTSU
            )

    @patch("ocrinvoice.core.image_processor.cv2")
    @patch("ocrinvoice.core.image_processor.np.array")
    def test_binarize_image_with_custom_threshold(
        self, mock_np_array, mock_cv2, processor
    ):
        """Test image binarization with custom threshold."""
        processor.config = {"binarization_threshold": 128}

        mock_image = Mock()
        mock_array = np.array([[100, 150], [200, 250]])
        mock_np_array.return_value = mock_array

        mock_binary = np.array([[0, 0], [255, 255]])
        mock_cv2.threshold.return_value = (128.0, mock_binary)

        mock_pil_image = Mock()
        with patch(
            "ocrinvoice.core.image_processor.PIL.Image.fromarray"
        ) as mock_fromarray:
            mock_fromarray.return_value = mock_pil_image

            result = processor._binarize_image(mock_image)

            assert result == mock_pil_image
            mock_cv2.threshold.assert_called_once_with(
                mock_array, 128, 255, mock_cv2.THRESH_BINARY
            )

    @patch("ocrinvoice.core.image_processor.cv2")
    @patch("ocrinvoice.core.image_processor.np.array")
    def test_binarize_image_failure(self, mock_np_array, mock_cv2, processor):
        """Test image binarization failure."""
        mock_image = Mock()
        mock_array = np.array([[100, 150], [200, 250]])
        mock_np_array.return_value = mock_array

        mock_cv2.threshold.side_effect = Exception("Binarization failed")

        with pytest.raises(Exception, match="Binarization failed"):
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
        mock_resized = Mock()
        mock_denoised = Mock()
        mock_enhanced = Mock()
        mock_binarized = Mock()

        with patch.object(processor, "_resize_image") as mock_resize:
            mock_resize.return_value = mock_resized

            with patch.object(processor, "_denoise_image") as mock_denoise:
                mock_denoise.return_value = mock_denoised

                with patch.object(processor, "_enhance_contrast") as mock_enhance:
                    mock_enhance.return_value = mock_enhanced

                    with patch.object(processor, "_binarize_image") as mock_binarize:
                        mock_binarize.return_value = mock_binarized

                        result = processor.preprocess_for_ocr(mock_image)

                        assert result == mock_binarized
                        mock_resize.assert_called_once_with(mock_image)
                        mock_denoise.assert_called_once_with(mock_resized)
                        mock_enhance.assert_called_once_with(mock_denoised)
                        mock_binarize.assert_called_once_with(mock_enhanced)

    def test_preprocess_for_ocr_with_custom_steps(self, processor):
        """Test OCR preprocessing with custom steps."""
        processor.preprocessing_steps = ["resize", "enhance_contrast"]
        mock_image = Mock()
        mock_resized = Mock()
        mock_enhanced = Mock()

        with patch.object(processor, "_resize_image") as mock_resize:
            mock_resize.return_value = mock_resized

            with patch.object(processor, "_enhance_contrast") as mock_enhance:
                mock_enhance.return_value = mock_enhanced

                result = processor.preprocess_for_ocr(mock_image)

                assert result == mock_enhanced
                mock_resize.assert_called_once_with(mock_image)
                mock_enhance.assert_called_once_with(mock_resized)

    def test_preprocess_for_ocr_step_failure(self, processor):
        """Test OCR preprocessing when a step fails."""
        mock_image = Mock()

        with patch.object(processor, "_resize_image") as mock_resize:
            mock_resize.side_effect = Exception("Resize failed")

            with pytest.raises(Exception, match="Resize failed"):
                processor.preprocess_for_ocr(mock_image)

    def test_preprocess_for_ocr_empty_steps(self, processor):
        """Test OCR preprocessing with empty steps list."""
        processor.preprocessing_steps = []
        mock_image = Mock()

        result = processor.preprocess_for_ocr(mock_image)

        assert result == mock_image

    def test_preprocess_for_ocr_invalid_step(self, processor):
        """Test OCR preprocessing with invalid step."""
        processor.preprocessing_steps = ["invalid_step"]
        mock_image = Mock()

        with pytest.raises(ValueError, match="Unknown preprocessing step"):
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

        result = processor._validate_image(mock_image)

        assert result == mock_image

    def test_validate_image_invalid_mode(self, processor):
        """Test image validation with invalid mode."""
        mock_image = Mock()
        mock_image.mode = "CMYK"

        with pytest.raises(ValueError, match="Unsupported image mode"):
            processor._validate_image(mock_image)

    def test_validate_image_none(self, processor):
        """Test image validation with None image."""
        with pytest.raises(ValueError, match="Image cannot be None"):
            processor._validate_image(None)

    def test_get_image_info(self, processor):
        """Test getting image information."""
        mock_image = Mock()
        mock_image.size = (1000, 1400)
        mock_image.mode = "RGB"

        info = processor._get_image_info(mock_image)

        assert info["width"] == 1000
        assert info["height"] == 1400
        assert info["mode"] == "RGB"
        assert info["aspect_ratio"] == pytest.approx(0.714, 0.001)


class TestImageProcessorErrorHandling:
    """Test ImageProcessor error handling and recovery."""

    @pytest.fixture
    def processor(self):
        """Create an ImageProcessor instance for testing."""
        return ImageProcessor()

    def test_handle_preprocessing_error_with_retry(self, processor):
        """Test preprocessing error handling with retry mechanism."""
        mock_image = Mock()

        with patch.object(processor, "_resize_image") as mock_resize:
            mock_resize.side_effect = [
                Exception("First failure"),
                Exception("Second failure"),
                mock_image,
            ]

            result = processor.preprocess_for_ocr(mock_image, max_retries=3)

            assert result == mock_image
            assert mock_resize.call_count == 3

    def test_handle_preprocessing_error_max_retries_exceeded(self, processor):
        """Test preprocessing error handling when max retries are exceeded."""
        mock_image = Mock()

        with patch.object(processor, "_resize_image") as mock_resize:
            mock_resize.side_effect = Exception("Always fails")

            with pytest.raises(Exception, match="Always fails"):
                processor.preprocess_for_ocr(mock_image, max_retries=2)

            assert mock_resize.call_count == 2


class TestImageProcessorPerformance:
    """Test ImageProcessor performance characteristics."""

    @pytest.fixture
    def processor(self):
        """Create an ImageProcessor instance for testing."""
        return ImageProcessor()

    def test_large_image_processing(self, processor):
        """Test processing of large images."""
        # Create a large mock image
        mock_image = Mock()
        mock_image.size = (4000, 5600)
        mock_image.mode = "RGB"

        with patch.object(processor, "_resize_image") as mock_resize:
            mock_resize.return_value = mock_image

            result = processor.preprocess_for_ocr(mock_image)

            assert result == mock_image
            mock_resize.assert_called_once_with(mock_image)

    def test_multiple_concurrent_processing(self, processor):
        """Test handling of multiple concurrent preprocessing requests."""
        import threading

        results = []
        errors = []

        def processing_worker():
            try:
                mock_image = Mock()
                mock_image.size = (1000, 1400)
                mock_image.mode = "RGB"

                with patch.object(processor, "_resize_image") as mock_resize:
                    mock_resize.return_value = mock_image
                    result = processor.preprocess_for_ocr(mock_image)
                    results.append(result)
            except Exception as e:
                errors.append(e)

        threads = []
        for i in range(5):
            thread = threading.Thread(target=processing_worker)
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        assert len(results) == 5
        assert len(errors) == 0


class TestImageProcessorIntegration:
    """Integration tests for ImageProcessor."""

    @pytest.fixture
    def processor(self):
        """Create an ImageProcessor instance for testing."""
        return ImageProcessor()

    def test_full_preprocessing_workflow(self, processor):
        """Test complete preprocessing workflow."""
        mock_image = Mock()
        mock_image.size = (1000, 1400)
        mock_image.mode = "RGB"

        mock_resized = Mock()
        mock_denoised = Mock()
        mock_enhanced = Mock()
        mock_binarized = Mock()

        with patch.object(processor, "_resize_image") as mock_resize:
            mock_resize.return_value = mock_resized

            with patch.object(processor, "_denoise_image") as mock_denoise:
                mock_denoise.return_value = mock_denoised

                with patch.object(processor, "_enhance_contrast") as mock_enhance:
                    mock_enhance.return_value = mock_enhanced

                    with patch.object(processor, "_binarize_image") as mock_binarize:
                        mock_binarize.return_value = mock_binarized

                        result = processor.preprocess_for_ocr(mock_image)

                        assert result == mock_binarized
                        mock_resize.assert_called_once_with(mock_image)
                        mock_denoise.assert_called_once_with(mock_resized)
                        mock_enhance.assert_called_once_with(mock_denoised)
                        mock_binarize.assert_called_once_with(mock_enhanced)

    def test_preprocessing_with_validation(self, processor):
        """Test preprocessing workflow with image validation."""
        mock_image = Mock()
        mock_image.size = (1000, 1400)
        mock_image.mode = "RGB"

        with patch.object(processor, "_validate_image") as mock_validate:
            mock_validate.return_value = mock_image

            with patch.object(processor, "_resize_image") as mock_resize:
                mock_resize.return_value = mock_image

                result = processor.preprocess_for_ocr(mock_image)

                assert result == mock_image
                mock_validate.assert_called_once_with(mock_image)
                mock_resize.assert_called_once_with(mock_image)
