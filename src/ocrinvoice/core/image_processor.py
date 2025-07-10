"""Image preprocessing utilities for OCR."""

import logging
import importlib.util
from pathlib import Path
from typing import Dict, Any, List, Optional, Union

# Conditional imports for optional dependencies
try:
    import cv2
    import numpy as np
    from PIL import Image, ImageEnhance, ImageFilter

    DEPENDENCIES_AVAILABLE = True
except ImportError as e:
    DEPENDENCIES_AVAILABLE = False
    logging.warning(
        f"Some image processing dependencies are missing: {e}. "
        "Image preprocessing will be limited."
    )


class ImageProcessor:
    """Utility for preprocessing images to improve OCR accuracy.

    This class provides various image preprocessing techniques
    that can enhance OCR results by improving image quality
    and reducing noise.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize the image processor.

        Args:
            config: Configuration dictionary for image processing settings
        """
        self.config: Dict[str, Any] = config or {}
        self.logger: logging.Logger = logging.getLogger(self.__class__.__name__)

        # Validate dependencies
        self._validate_dependencies()

        # Configuration
        self.min_width: int = self.config.get("min_width", 800)
        self.target_width: int = self.config.get("target_width", 2000)
        self.target_height: int = self.config.get("target_height", 2800)
        self.enhance_contrast: bool = self.config.get("enhance_contrast", True)
        self.enhance_sharpness: bool = self.config.get("enhance_sharpness", True)
        self.apply_noise_reduction: bool = self.config.get(
            "apply_noise_reduction", True
        )
        self.apply_binarization: bool = self.config.get("apply_binarization", True)
        self.debug: bool = self.config.get("debug", False)

        # Preprocessing steps in order
        self.preprocessing_steps: List[str] = self.config.get(
            "preprocessing_steps", ["resize", "denoise", "enhance_contrast", "binarize"]
        )

        # Validate configuration
        self._validate_preprocessing_steps()

    def _validate_dependencies(self) -> None:
        """Validate that required dependencies are available."""
        # Check PIL
        if importlib.util.find_spec("PIL") is None:
            raise ImportError("PIL not installed")

        # Check cv2
        if importlib.util.find_spec("cv2") is None:
            raise ImportError("cv2 not installed")

        # Check numpy
        if importlib.util.find_spec("numpy") is None:
            raise ImportError("numpy not installed")

    def preprocess_image(self, image: Union[str, Path, Image.Image]) -> Image.Image:
        """Apply comprehensive preprocessing to an image.

        Args:
            image: Path to image file or PIL Image object

        Returns:
            Preprocessed PIL Image

        Raises:
            FileNotFoundError: If image file doesn't exist
        """
        if isinstance(image, (str, Path)):
            image_path = Path(image)
            if not image_path.exists():
                raise FileNotFoundError(f"Image file not found: {image_path}")

            # Load image
            image = Image.open(image_path)

        # Apply preprocessing pipeline
        processed = image

        # 1. Resize if too small
        processed = self._resize_image(processed)

        # 2. Convert to grayscale
        processed = self._convert_to_grayscale(processed)

        # 3. Enhance contrast
        if self.enhance_contrast:
            processed = self._enhance_contrast(processed)

        # 4. Enhance sharpness
        if self.enhance_sharpness:
            processed = self._enhance_sharpness(processed)

        # 5. Apply noise reduction
        if self.apply_noise_reduction:
            processed = self._reduce_noise(processed)

        # 6. Apply thresholding
        processed = self._apply_thresholding(processed)

        # 7. Apply morphological operations
        processed = self._apply_morphology(processed)

        return processed

    def _resize_image(self, image: Image.Image) -> Image.Image:
        """Resize image if it's too small for good OCR.

        Args:
            image: PIL Image to resize

        Returns:
            Resized PIL Image
        """
        width, height = image.size

        if width < self.min_width:
            # Calculate scale factor
            scale_factor = self.min_width / width
            new_width = int(width * scale_factor)
            new_height = int(height * scale_factor)

            # Resize using high-quality interpolation
            resized = image.resize((new_width, new_height), Image.Resampling.LANCZOS)

            if self.debug:
                self.logger.debug(
                    f"Resized image from {width}x{height} to {new_width}x{new_height}"
                )

            return resized

        return image

    def _convert_to_grayscale(self, image: Image.Image) -> Image.Image:
        """Convert image to grayscale.

        Args:
            image: PIL Image to convert

        Returns:
            Grayscale PIL Image
        """
        if image.mode != "L":
            return image.convert("L")
        return image

    def _enhance_contrast(self, image: Image.Image) -> Image.Image:
        """Enhance image contrast.

        Args:
            image: PIL Image to enhance

        Returns:
            Enhanced PIL Image
        """
        enhancer = ImageEnhance.Contrast(image)
        enhanced = enhancer.enhance(1.5)  # Increase contrast by 50%
        return enhanced

    def _enhance_sharpness(self, image: Image.Image) -> Image.Image:
        """Enhance image sharpness.

        Args:
            image: PIL Image to enhance

        Returns:
            Enhanced PIL Image
        """
        enhancer = ImageEnhance.Sharpness(image)
        enhanced = enhancer.enhance(1.3)  # Increase sharpness by 30%
        return enhanced

    def _reduce_noise(self, image: Image.Image) -> Image.Image:
        """Reduce noise in the image.

        Args:
            image: PIL Image to process

        Returns:
            Denoised PIL Image
        """
        # Convert to numpy array for OpenCV processing
        img_array = np.array(image)

        # Apply Gaussian blur to reduce noise
        denoised = cv2.GaussianBlur(img_array, (1, 1), 0)

        # Convert back to PIL Image
        return Image.fromarray(denoised)

    def _apply_thresholding(self, image: Image.Image) -> Image.Image:
        """Apply adaptive thresholding to create binary image.

        Args:
            image: PIL Image to process

        Returns:
            Thresholded PIL Image
        """
        # Convert to numpy array
        img_array = np.array(image)

        # Apply Otsu's thresholding
        _, thresh = cv2.threshold(
            img_array, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )

        # Convert back to PIL Image
        return Image.fromarray(thresh)

    def _apply_morphology(self, image: Image.Image) -> Image.Image:
        """Apply morphological operations to clean up the image.

        Args:
            image: PIL Image to process

        Returns:
            Processed PIL Image
        """
        # Convert to numpy array
        img_array = np.array(image)

        # Create kernel for morphological operations
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))

        # Apply closing operation to fill small holes
        closed = cv2.morphologyEx(img_array, cv2.MORPH_CLOSE, kernel)

        # Apply opening operation to remove small noise
        opened = cv2.morphologyEx(closed, cv2.MORPH_OPEN, kernel)

        # Convert back to PIL Image
        return Image.fromarray(opened)

    def _denoise_image(self, image: Image.Image, strength: float = 1.0) -> Image.Image:
        """Denoise image using various techniques.

        Args:
            image: PIL Image to denoise
            strength: Denoising strength (0.0 to 2.0)

        Returns:
            Denoised PIL Image
        """
        try:
            # Convert to numpy array for OpenCV processing
            img_array = np.array(image)

            # Apply bilateral filter for edge-preserving denoising
            denoised = cv2.bilateralFilter(img_array, 9, 75, 75)

            # Apply additional Gaussian blur if strength > 1.0
            if strength > 1.0:
                kernel_size = int(3 + (strength - 1.0) * 2)
                if kernel_size % 2 == 0:
                    kernel_size += 1
                denoised = cv2.GaussianBlur(denoised, (kernel_size, kernel_size), 0)

            # Convert back to PIL Image
            return Image.fromarray(denoised)

        except Exception as e:
            self.logger.error(f"Denoising failed: {e}")
            raise Exception(f"Denoising failed: {e}")

    def _binarize_image(
        self, image: Image.Image, threshold: Optional[int] = None
    ) -> Image.Image:
        """Convert image to binary (black and white).

        Args:
            image: PIL Image to binarize
            threshold: Threshold value (0-255), None for automatic

        Returns:
            Binary PIL Image
        """
        try:
            # Convert to grayscale if not already
            if image.mode != "L":
                image = image.convert("L")

            # Convert to numpy array
            img_array = np.array(image)

            if threshold is None:
                # Use Otsu's method for automatic threshold
                threshold, binary = cv2.threshold(
                    img_array, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
                )
            else:
                # Use manual threshold
                _, binary = cv2.threshold(img_array, threshold, 255, cv2.THRESH_BINARY)

            # Convert back to PIL Image
            return Image.fromarray(binary)

        except Exception as e:
            self.logger.error(f"Binarization failed: {e}")
            raise Exception(f"Binarization failed: {e}")

    def _validate_image(
        self, image: Union[str, Path, Image.Image], mode: str = "any"
    ) -> bool:
        """Validate that an image is valid and meets requirements.

        Args:
            image: Image to validate (path or PIL Image)
            mode: Validation mode ('any', 'rgb', 'grayscale')

        Returns:
            True if image is valid, False otherwise
        """
        try:
            if isinstance(image, (str, Path)):
                image_path = Path(image)
                if not image_path.exists():
                    return False

                # Try to open the image
                with Image.open(image_path) as img:
                    img.verify()

                # Check mode if specified
                if mode != "any":
                    with Image.open(image_path) as img:
                        if mode == "rgb" and img.mode not in ["RGB", "RGBA"]:
                            return False
                        elif mode == "grayscale" and img.mode != "L":
                            return False
            else:
                # PIL Image object
                if not isinstance(image, Image.Image):
                    return False

                # Check mode if specified
                if mode == "rgb" and image.mode not in ["RGB", "RGBA"]:
                    return False
                elif mode == "grayscale" and image.mode != "L":
                    return False

            return True

        except Exception as e:
            self.logger.debug(f"Image validation failed: {e}")
            return False

    def preprocess_for_ocr(
        self,
        image: Union[str, Path, Image.Image],
        method: str = "standard",
        max_retries: int = 3,
    ) -> Image.Image:
        """Preprocess image specifically for OCR.

        Args:
            image: Image to preprocess (path or PIL Image)
            method: Preprocessing method ('standard', 'aggressive', 'conservative')
            max_retries: Maximum number of retry attempts

        Returns:
            Preprocessed PIL Image

        Raises:
            FileNotFoundError: If image file doesn't exist
            Exception: If preprocessing fails
        """
        for attempt in range(max_retries):
            try:
                if method == "standard":
                    return self.preprocess_image(image)
                elif method == "aggressive":
                    return self._preprocess_aggressive(image)
                elif method == "conservative":
                    return self._preprocess_conservative(image)
                else:
                    raise ValueError(f"Unknown preprocessing method: {method}")

            except Exception as e:
                self.logger.error(f"Preprocessing failed on attempt {attempt + 1}: {e}")
                if attempt == max_retries - 1:
                    raise Exception(f"Always fails: {e}")

        # This should never be reached
        raise Exception("Preprocessing failed after all retries")

    def _preprocess_aggressive(self, image: Image.Image) -> Image.Image:
        """Apply aggressive preprocessing for difficult images.

        Args:
            image: PIL Image to process

        Returns:
            Aggressively processed PIL Image
        """
        # Convert to numpy array
        img_array = np.array(image)

        # Convert to grayscale if needed
        if len(img_array.shape) == 3:
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        else:
            gray = img_array

        # Apply more aggressive noise reduction
        denoised = cv2.medianBlur(gray, 3)

        # Apply adaptive thresholding
        thresh = cv2.adaptiveThreshold(
            denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )

        # Apply more aggressive morphological operations
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        processed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        processed = cv2.morphologyEx(processed, cv2.MORPH_OPEN, kernel)

        return Image.fromarray(processed)

    def _preprocess_conservative(self, image: Image.Image) -> Image.Image:
        """Apply conservative preprocessing to preserve details.

        Args:
            image: PIL Image to process

        Returns:
            Conservatively processed PIL Image
        """
        # Convert to grayscale
        if image.mode != "L":
            image = image.convert("L")

        # Apply minimal contrast enhancement
        enhancer = ImageEnhance.Contrast(image)
        enhanced = enhancer.enhance(1.2)

        # Apply minimal sharpening
        enhancer = ImageEnhance.Sharpness(enhanced)
        sharpened = enhancer.enhance(1.1)

        return sharpened

    def get_image_info(self, image: Union[str, Path, Image.Image]) -> Dict[str, Any]:
        """Get information about an image.

        Args:
            image: Path to image file or PIL Image object

        Returns:
            Dictionary with image information

        Raises:
            FileNotFoundError: If image file doesn't exist
        """
        if isinstance(image, (str, Path)):
            image_path = Path(image)
            if not image_path.exists():
                raise FileNotFoundError(f"Image file not found: {image_path}")

            image = Image.open(image_path)
            file_size = image_path.stat().st_size
        else:
            file_size = None

        info = {
            "size": image.size,
            "mode": image.mode,
            "format": image.format,
            "file_size": file_size,
            "is_grayscale": image.mode == "L",
            "aspect_ratio": image.size[0] / image.size[1] if image.size[1] > 0 else 0,
        }

        return info

    def batch_preprocess(
        self, images: List[Union[str, Path, Image.Image]], method: str = "standard"
    ) -> List[Image.Image]:
        """Preprocess multiple images.

        Args:
            images: List of image paths or PIL Images
            method: Preprocessing method

        Returns:
            List of preprocessed PIL Images
        """
        processed_images = []

        for i, image in enumerate(images):
            try:
                processed = self.preprocess_for_ocr(image, method)
                processed_images.append(processed)

                if self.debug:
                    self.logger.debug(f"Processed image {i + 1}/{len(images)}")

            except Exception as e:
                self.logger.error(f"Error processing image {i + 1}: {e}")
                # Add original image as fallback
                if isinstance(image, Image.Image):
                    processed_images.append(image)
                else:
                    # Try to load the image
                    try:
                        img = Image.open(image)
                        processed_images.append(img)
                    except:
                        # Create a blank image as last resort
                        blank = Image.new("L", (100, 100), 255)
                        processed_images.append(blank)

        return processed_images

    def _validate_preprocessing_steps(self) -> None:
        """Validate preprocessing steps configuration."""
        valid_steps = [
            "resize",
            "denoise",
            "enhance_contrast",
            "binarize",
            "grayscale",
            "sharpness",
        ]

        for step in self.preprocessing_steps:
            if step not in valid_steps:
                raise ValueError(
                    f"Invalid preprocessing step: {step}. Valid steps are: {valid_steps}"
                )
