"""
Image Processing Backend Module
Contains all image processing operations using OpenCV and NumPy
"""

import cv2
import numpy as np
from typing import Tuple, Optional, Dict
from scipy.ndimage import convolve


class ImageProcessor:
    """
    Class containing all image processing operations
    """
    
    @staticmethod
    def convolve2d(image: np.ndarray, kernel: np.ndarray) -> np.ndarray:
        """
        Optimized 2D convolution using scipy (much faster than manual loops)
        
        Args:
            image: Input image array (single channel)
            kernel: Convolution kernel
            
        Returns:
            Convolved image array
        """
        # Use scipy's optimized convolution (10-50x faster than manual loops)
        result = convolve(image.astype(np.float64), kernel, mode='constant', cval=0.0)
        return result
    
    @staticmethod
    def create_gaussian_kernel(kernel_size: int, sigma: Optional[float] = None) -> np.ndarray:
        """
        Create a Gaussian kernel manually
        
        Args:
            kernel_size: Size of the kernel (must be odd)
            sigma: Standard deviation. If None, computed as (kernel_size-1)/6
            
        Returns:
            Gaussian kernel
        """
        if kernel_size % 2 == 0:
            kernel_size += 1
        
        if sigma is None:
            sigma = (kernel_size - 1) / 6
        
        # Create coordinate arrays
        ax = np.arange(-kernel_size // 2 + 1., kernel_size // 2 + 1.)
        xx, yy = np.meshgrid(ax, ax)
        
        # Compute Gaussian kernel
        kernel = np.exp(-0.5 * (np.square(xx) + np.square(yy)) / np.square(sigma))
        
        # Normalize
        return kernel / np.sum(kernel)
    
    @staticmethod
    def gaussian_blur(image: np.ndarray, kernel_size: int = 5, sigma: Optional[float] = None) -> np.ndarray:
        """
        Apply Gaussian blur manually using convolution
        
        Args:
            image: Input image array
            kernel_size: Size of the Gaussian kernel (must be odd)
            sigma: Standard deviation for Gaussian kernel
            
        Returns:
            Blurred image array
        """
        if kernel_size % 2 == 0:
            kernel_size += 1
        
        # Create Gaussian kernel
        kernel = ImageProcessor.create_gaussian_kernel(kernel_size, sigma)
        
        # Apply convolution to each channel
        if len(image.shape) == 3:
            result = np.zeros_like(image, dtype=np.uint8)
            for c in range(image.shape[2]):
                blurred = ImageProcessor.convolve2d(image[:, :, c].astype(np.float64), kernel)
                result[:, :, c] = np.clip(blurred, 0, 255).astype(np.uint8)
            return result
        else:
            blurred = ImageProcessor.convolve2d(image.astype(np.float64), kernel)
            return np.clip(blurred, 0, 255).astype(np.uint8)
    
    @staticmethod
    def average_blur(image: np.ndarray, kernel_size: int = 5) -> np.ndarray:
        """
        Apply average blur manually using convolution
        
        Args:
            image: Input image array
            kernel_size: Size of the averaging kernel
            
        Returns:
            Blurred image array
        """
        # Create averaging kernel
        kernel = np.ones((kernel_size, kernel_size), dtype=np.float64) / (kernel_size * kernel_size)
        
        # Apply convolution to each channel
        if len(image.shape) == 3:
            result = np.zeros_like(image, dtype=np.uint8)
            for c in range(image.shape[2]):
                blurred = ImageProcessor.convolve2d(image[:, :, c].astype(np.float64), kernel)
                result[:, :, c] = np.clip(blurred, 0, 255).astype(np.uint8)
            return result
        else:
            blurred = ImageProcessor.convolve2d(image.astype(np.float64), kernel)
            return np.clip(blurred, 0, 255).astype(np.uint8)
    
    @staticmethod
    def median_blur(image: np.ndarray, kernel_size: int = 5) -> np.ndarray:
        """
        Apply median blur using optimized cv2 function (manual version is too slow)
        
        Args:
            image: Input image array
            kernel_size: Size of the median kernel (must be odd)
            
        Returns:
            Blurred image array
        """
        if kernel_size % 2 == 0:
            kernel_size += 1
        
        # Use cv2's highly optimized median filter (100x faster than manual)
        return cv2.medianBlur(image, kernel_size)
    
    @staticmethod
    def canny_edge_detection_manual(image: np.ndarray, low_threshold: int = 50, 
                                    high_threshold: int = 150) -> Tuple[np.ndarray, Dict]:
        """
        Apply Canny edge detection algorithm manually with intermediate steps
        
        Args:
            image: Input image array
            low_threshold: Lower threshold for edge detection
            high_threshold: Upper threshold for edge detection
            
        Returns:
            Final edge image and dictionary containing intermediate images
        """
        # Step 1: Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        # Step 2: Apply Gaussian blur to reduce noise (using optimized version)
        blurred = ImageProcessor.gaussian_blur(gray, kernel_size=5)
        if len(blurred.shape) == 3:
            blurred = cv2.cvtColor(blurred, cv2.COLOR_BGR2GRAY)
        
        # Step 3: Calculate gradients using Sobel operators (optimized with cv2)
        gradient_x = cv2.Sobel(blurred, cv2.CV_64F, 1, 0, ksize=3)
        gradient_y = cv2.Sobel(blurred, cv2.CV_64F, 0, 1, ksize=3)
        
        # Calculate gradient magnitude and direction
        gradient_magnitude = np.sqrt(gradient_x**2 + gradient_y**2)
        gradient_direction = np.arctan2(gradient_y, gradient_x)
        
        # Normalize gradient magnitude for display
        gradient_magnitude_normalized = ((gradient_magnitude / gradient_magnitude.max()) * 255).astype(np.uint8)
        
        # Step 4: Non-maximum suppression
        nms = np.zeros_like(gradient_magnitude)
        angle = gradient_direction * 180.0 / np.pi
        angle[angle < 0] += 180
        
        # Vectorized non-maximum suppression for speed
        height, width = gradient_magnitude.shape
        for i in range(1, height - 1):
            for j in range(1, width - 1):
                q = 255
                r = 255
                
                # Angle 0
                if (0 <= angle[i, j] < 22.5) or (157.5 <= angle[i, j] <= 180):
                    q = gradient_magnitude[i, j + 1]
                    r = gradient_magnitude[i, j - 1]
                # Angle 45
                elif 22.5 <= angle[i, j] < 67.5:
                    q = gradient_magnitude[i + 1, j - 1]
                    r = gradient_magnitude[i - 1, j + 1]
                # Angle 90
                elif 67.5 <= angle[i, j] < 112.5:
                    q = gradient_magnitude[i + 1, j]
                    r = gradient_magnitude[i - 1, j]
                # Angle 135
                elif 112.5 <= angle[i, j] < 157.5:
                    q = gradient_magnitude[i - 1, j - 1]
                    r = gradient_magnitude[i + 1, j + 1]
                
                if gradient_magnitude[i, j] >= q and gradient_magnitude[i, j] >= r:
                    nms[i, j] = gradient_magnitude[i, j]
                else:
                    nms[i, j] = 0
        
        nms_normalized = ((nms / nms.max()) * 255).astype(np.uint8) if nms.max() > 0 else nms.astype(np.uint8)
        
        # Step 5: Double thresholding (vectorized for speed)
        strong_edges = (nms >= high_threshold).astype(np.uint8) * 255
        weak_edges = ((nms >= low_threshold) & (nms < high_threshold)).astype(np.uint8) * 128
        double_threshold = strong_edges + weak_edges
        
        # Step 6: Edge tracking by hysteresis (optimized)
        final_edges = strong_edges.copy()
        
        # Use a more efficient approach with connectivity
        for i in range(1, height - 1):
            for j in range(1, width - 1):
                if weak_edges[i, j] == 128:
                    # Check if any neighboring pixel is a strong edge
                    if np.any(strong_edges[i-1:i+2, j-1:j+2] == 255):
                        final_edges[i, j] = 255
                        strong_edges[i, j] = 255  # Update for propagation
        
        # Store intermediate results
        intermediates = {
            '1_grayscale': cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR),
            '2_blurred': cv2.cvtColor(blurred, cv2.COLOR_GRAY2BGR),
            '3_gradient_magnitude': cv2.cvtColor(gradient_magnitude_normalized, cv2.COLOR_GRAY2BGR),
            '4_non_maximum_suppression': cv2.cvtColor(nms_normalized, cv2.COLOR_GRAY2BGR),
            '5_double_threshold': cv2.cvtColor(double_threshold, cv2.COLOR_GRAY2BGR),
            '6_final_edges': cv2.cvtColor(final_edges, cv2.COLOR_GRAY2BGR)
        }
        
        return cv2.cvtColor(final_edges, cv2.COLOR_GRAY2BGR), intermediates
    
    @staticmethod
    def log_function(x, y, sigma):
        """
        Laplacian of Gaussian function
        LoG(x,y) = -(1/(πσ⁴)) * (1 - (x²+y²)/(2σ²)) * e^(-(x²+y²)/(2σ²))
        """
        r_squared = x**2 + y**2
        return -(1 / (np.pi * sigma**4)) * (1 - r_squared / (2 * sigma**2)) * np.exp(-r_squared / (2 * sigma**2))
    
    @staticmethod
    def generate_log_kernel(sigma):
        """
        Generate Laplacian of Gaussian kernel with given sigma
        Kernel size is automatically calculated as 9*sigma (rounded to odd)
        """
        size = 9 * sigma 
        size = int(np.ceil(size))
        
        # Ensure odd size
        if size & 1 == 0:
            size = size + 1
        
        kernel = np.zeros((size, size))
        center = size // 2
        
        for i in range(size):
            for j in range(size):
                x, y = i - center, j - center
                kernel[i, j] = ImageProcessor.log_function(x, y, sigma)
        
        return kernel
    
    @staticmethod
    def manual_variance(data):
        """
        Calculate variance manually without numpy's var function
        Var(X) = (1/n) * Σ(x - mean)²
        """
        flat_data = data.flatten()
        n = len(flat_data)
        
        mean = np.sum(flat_data) / n
        variance = np.sum((flat_data - mean) ** 2) / n
        
        return variance
    
    @staticmethod
    def calculate_local_variance(image, window_size=5):
        """
        Calculate local variance for each pixel using a sliding window
        Returns variance map of same size as input image
        """
        h, w = image.shape
        pad = window_size // 2
        variance_map = np.zeros((h, w), dtype=np.float32)
        
        # Pad image for border handling
        padded_img = cv2.copyMakeBorder(image, pad, pad, pad, pad, cv2.BORDER_REFLECT)
        
        # Calculate variance for each pixel's neighborhood
        for i in range(h):
            for j in range(w):
                window = padded_img[i:i+window_size, j:j+window_size].astype(np.float32)
                local_variance = ImageProcessor.manual_variance(window)
                variance_map[i, j] = local_variance
        
        return variance_map
    
    @staticmethod
    def zero_crossings_with_variance(log_image, variance_map, variance_threshold=100, min_strength=10):
        """
        Detect zero crossings in LoG response with variance-based filtering
        
        Args:
            log_image: LoG filtered image (float32)
            variance_map: Local variance map
            variance_threshold: Minimum variance to accept edge
            min_strength: Minimum zero-crossing strength
            
        Returns:
            edge_map: Binary edge map (uint8)
            strength_map: Zero-crossing strength map (float32)
        """
        h, w = log_image.shape
        edge_map = np.zeros((h, w), dtype=np.uint8)
        strength_map = np.zeros((h, w), dtype=np.float32)
        
        for i in range(1, h-1):
            for j in range(1, w-1):
                # Get 4-neighborhood (horizontal and vertical)
                n1 = log_image[i-1, j]  # top
                n2 = log_image[i+1, j]  # bottom
                n3 = log_image[i, j-1]  # left
                n4 = log_image[i, j+1]  # right
                root = log_image[i, j]  # center
                
                # Check for zero crossing (sign change)
                if (n1 * n2 < 0) or (n3 * n4 < 0):
                    # Calculate zero-crossing strength
                    strength = (np.abs(root - n1) + np.abs(root - n2) + 
                               np.abs(root - n3) + np.abs(root - n4))
                    strength_map[i, j] = strength
                    
                    # Get local variance
                    local_variance = variance_map[i, j]
                    
                    # Apply thresholds
                    if local_variance > variance_threshold and strength > min_strength:
                        edge_map[i, j] = 255
        
        return edge_map, strength_map
    
    @staticmethod
    def laplacian_edge_detection_manual(image: np.ndarray, threshold: int = 50, 
                                       kernel_size: int = 3, blur_kernel: int = 5) -> tuple:
        """
        Apply robust Laplacian-based edge detection using LoG with zero-crossing
        and adaptive thresholding based on local variance.
        
        Algorithm follows: Image → LoG operator → Zero crossing detection → 
        Variance threshold → Edge points
        
        Args:
            image: Input image array (BGR format)
            threshold: Variance threshold value (0-255, maps to actual variance threshold)
            kernel_size: Not used (kept for compatibility), sigma is used instead
            blur_kernel: Sigma value for LoG kernel (1-15)
            
        Returns:
            Tuple of (final_edges_BGR, intermediates_dict)
        """
        # Step 1: Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        # Step 2: Generate LoG kernel with sigma
        # Map blur_kernel (1-15) to reasonable sigma range (0.5-3.0)
        sigma = blur_kernel / 5.0  # 1→0.2, 5→1.0, 15→3.0
        sigma = max(0.5, min(sigma, 3.0))  # Clamp to reasonable range
        
        log_kernel = ImageProcessor.generate_log_kernel(sigma)
        
        # Step 3: Apply LoG filter
        log_image = cv2.filter2D(gray, ddepth=cv2.CV_32F, kernel=log_kernel).astype(np.float32)
        
        # Step 4: Calculate local variance
        variance_map = ImageProcessor.calculate_local_variance(gray, window_size=5)
        
        # Step 5: Detect zero crossings with variance thresholding
        # Map threshold parameter (0-255) to variance threshold
        # Default (50) → 100, range: 0 → 10, 255 → 500
        variance_threshold = 10 + (threshold / 255.0) * 490
        min_strength = 10  # Minimum zero-crossing strength
        
        edge_map, strength_map = ImageProcessor.zero_crossings_with_variance(
            log_image, variance_map, variance_threshold, min_strength
        )
        
        # Step 6: Optional post-processing (minimal to preserve algorithm purity)
        # Just remove isolated single pixels
        kernel = np.ones((3, 3), np.uint8)
        edge_map_cleaned = cv2.morphologyEx(edge_map, cv2.MORPH_OPEN, kernel, iterations=1)
        
        # Normalize images for visualization
        log_vis = cv2.normalize(log_image, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
        strength_vis = cv2.normalize(strength_map, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
        variance_vis = cv2.normalize(variance_map, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
        
        # Create variance threshold mask for visualization
        variance_mask = np.zeros_like(gray)
        variance_mask[variance_map > variance_threshold] = 255
        
        # Create zero crossings visualization (before variance filtering)
        zero_crossings_vis = np.zeros_like(gray)
        zero_crossings_vis[strength_map > 0] = 255
        
        # Create intermediates dictionary
        intermediates = {
            '1_grayscale': cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR),
            '2_log_kernel_applied': cv2.cvtColor(log_vis, cv2.COLOR_GRAY2BGR),
            '3_local_variance_map': cv2.applyColorMap(variance_vis, cv2.COLORMAP_JET),
            '4_zero_crossing_strength': cv2.cvtColor(strength_vis, cv2.COLOR_GRAY2BGR),
            '5_zero_crossings_detected': cv2.cvtColor(zero_crossings_vis, cv2.COLOR_GRAY2BGR),
            '6_variance_filtered': cv2.cvtColor(edge_map, cv2.COLOR_GRAY2BGR),
            '7_final_edges': cv2.cvtColor(edge_map_cleaned, cv2.COLOR_GRAY2BGR)
        }
        
        return cv2.cvtColor(edge_map_cleaned, cv2.COLOR_GRAY2BGR), intermediates
    
    @staticmethod
    def canny_edge_detection(image: np.ndarray, threshold1: int = 100, 
                            threshold2: int = 200) -> np.ndarray:
        """
        Apply Canny edge detection algorithm (wrapper for compatibility)
        
        Args:
            image: Input image array
            threshold1: Lower threshold for edge detection
            threshold2: Upper threshold for edge detection
            
        Returns:
            Edge-detected image array (grayscale)
        """
        result, _ = ImageProcessor.canny_edge_detection_manual(image, threshold1, threshold2)
        return result
    
    @staticmethod
    def sobel_edge_detection(image: np.ndarray) -> np.ndarray:
        """
        Apply Sobel edge detection algorithm
        
        Args:
            image: Input image array
            
        Returns:
            Edge-detected image array
        """
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
            
        # Calculate gradients
        sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        
        # Combine gradients
        sobel = np.sqrt(sobelx**2 + sobely**2)
        sobel = np.uint8(sobel / np.max(sobel) * 255)
        
        # Convert back to BGR for display
        return cv2.cvtColor(sobel, cv2.COLOR_GRAY2BGR)
    
    @staticmethod
    def enhance_contrast(image: np.ndarray) -> np.ndarray:
        """
        Enhance contrast by stretching intensity levels
        
        Args:
            image: Input image array
            
        Returns:
            Contrast-enhanced image array
        """
        # Convert to LAB color space
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        
        # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        l = clahe.apply(l)
        
        # Merge channels and convert back to BGR
        lab = cv2.merge([l, a, b])
        return cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
    
    @staticmethod
    def rotate_image(image: np.ndarray, angle: float) -> np.ndarray:
        """
        Rotate image by a custom angle
        
        Args:
            image: Input image array
            angle: Rotation angle in degrees (positive = counter-clockwise)
            
        Returns:
            Rotated image array
        """
        height, width = image.shape[:2]
        center = (width // 2, height // 2)
        
        # Get rotation matrix
        rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        
        # Calculate new bounding dimensions
        cos = np.abs(rotation_matrix[0, 0])
        sin = np.abs(rotation_matrix[0, 1])
        
        new_width = int((height * sin) + (width * cos))
        new_height = int((height * cos) + (width * sin))
        
        # Adjust rotation matrix for new dimensions
        rotation_matrix[0, 2] += (new_width / 2) - center[0]
        rotation_matrix[1, 2] += (new_height / 2) - center[1]
        
        # Perform rotation
        rotated = cv2.warpAffine(image, rotation_matrix, (new_width, new_height),
                                 borderMode=cv2.BORDER_CONSTANT, 
                                 borderValue=(255, 255, 255))
        return rotated
    
    @staticmethod
    def sharpen_image(image: np.ndarray, strength: float = 1.0) -> np.ndarray:
        """
        Sharpen image to enhance details and edges
        
        Args:
            image: Input image array
            strength: Sharpening strength (0.0 to 2.0)
            
        Returns:
            Sharpened image array
        """
        # Create sharpening kernel
        kernel = np.array([[-1, -1, -1],
                          [-1,  9, -1],
                          [-1, -1, -1]]) * strength
        
        # Normalize kernel
        kernel[1, 1] = 9 - 8 * strength
        
        # Apply kernel
        sharpened = cv2.filter2D(image, -1, kernel)
        return np.clip(sharpened, 0, 255).astype(np.uint8)
    
    @staticmethod
    def adjust_brightness(image: np.ndarray, value: int) -> np.ndarray:
        """
        Adjust image brightness
        
        Args:
            image: Input image array
            value: Brightness adjustment (-100 to +100)
            
        Returns:
            Brightness-adjusted image array
        """
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(hsv)
        
        # Adjust value channel
        v = np.clip(v.astype(np.int16) + value, 0, 255).astype(np.uint8)
        
        hsv = cv2.merge([h, s, v])
        return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    
    @staticmethod
    def adjust_saturation(image: np.ndarray, value: float) -> np.ndarray:
        """
        Adjust color saturation
        
        Args:
            image: Input image array
            value: Saturation multiplier (0.0 to 2.0, 1.0 = no change)
            
        Returns:
            Saturation-adjusted image array
        """
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV).astype(np.float32)
        h, s, v = cv2.split(hsv)
        
        # Adjust saturation channel
        s = np.clip(s * value, 0, 255)
        
        hsv = cv2.merge([h, s, v]).astype(np.uint8)
        return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    
    @staticmethod
    def convert_to_grayscale(image: np.ndarray) -> np.ndarray:
        """
        Convert image to grayscale
        
        Args:
            image: Input image array
            
        Returns:
            Grayscale image array (still in BGR format for consistency)
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        return cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
    
    @staticmethod
    def flip_image(image: np.ndarray, direction: str = 'horizontal') -> np.ndarray:
        """
        Flip image horizontally or vertically
        
        Args:
            image: Input image array
            direction: 'horizontal', 'vertical', or 'both'
            
        Returns:
            Flipped image array
        """
        if direction == 'horizontal':
            return cv2.flip(image, 1)
        elif direction == 'vertical':
            return cv2.flip(image, 0)
        elif direction == 'both':
            return cv2.flip(image, -1)
        else:
            return image.copy()
    
    @staticmethod
    def crop_image(image: np.ndarray, x: int, y: int, 
                   width: int, height: int) -> np.ndarray:
        """
        Crop image to specified region
        
        Args:
            image: Input image array
            x: Starting x coordinate
            y: Starting y coordinate
            width: Crop width
            height: Crop height
            
        Returns:
            Cropped image array
        """
        h, w = image.shape[:2]
        
        # Ensure coordinates are within bounds
        x = max(0, min(x, w - 1))
        y = max(0, min(y, h - 1))
        width = max(1, min(width, w - x))
        height = max(1, min(height, h - y))
        
        return image[y:y+height, x:x+width].copy()
    
    @staticmethod
    def foreground_background_separation(image: np.ndarray, 
                                        rect: Optional[Tuple[int, int, int, int]] = None,
                                        iterations: int = 5) -> np.ndarray:
        """
        Separate foreground from background using GrabCut algorithm
        
        Args:
            image: Input image array
            rect: Rectangle (x, y, width, height) around foreground. If None, uses center region
            iterations: Number of iterations for algorithm
            
        Returns:
            Image with background removed (white background)
        """
        # Create mask
        mask = np.zeros(image.shape[:2], np.uint8)
        
        # Define background and foreground models
        bgd_model = np.zeros((1, 65), np.float64)
        fgd_model = np.zeros((1, 65), np.float64)
        
        # Define rectangle around the foreground
        if rect is None:
            # Default: assuming center region
            h, w = image.shape[:2]
            rect = (int(w * 0.1), int(h * 0.1), 
                    int(w * 0.8), int(h * 0.8))
        
        # Apply GrabCut
        cv2.grabCut(image, mask, rect, bgd_model, fgd_model, 
                   iterations, cv2.GC_INIT_WITH_RECT)
        
        # Create mask where background is 0, foreground is 1
        mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype('uint8')
        
        # Apply mask to image
        result = image * mask2[:, :, np.newaxis]
        
        # Create white background
        background = np.ones_like(image) * 255
        background = background * (1 - mask2[:, :, np.newaxis])
        
        return result + background
    
    @staticmethod
    def foreground_background_separation_with_mask(image: np.ndarray, 
                                                   rect: Tuple[int, int, int, int],
                                                   iterations: int = 5) -> Tuple[np.ndarray, np.ndarray]:
        """
        Separate foreground from background using GrabCut algorithm and return both result and mask
        
        Args:
            image: Input image array
            rect: Rectangle (x, y, width, height) around foreground
            iterations: Number of iterations for algorithm
            
        Returns:
            Tuple of (segmented image with white background, binary mask)
        """
        # Create mask
        mask = np.zeros(image.shape[:2], np.uint8)
        
        # Define background and foreground models
        bgd_model = np.zeros((1, 65), np.float64)
        fgd_model = np.zeros((1, 65), np.float64)
        
        # Apply GrabCut
        cv2.grabCut(image, mask, rect, bgd_model, fgd_model, 
                   iterations, cv2.GC_INIT_WITH_RECT)
        
        # Create mask where background is 0, foreground is 1
        mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype('uint8')
        
        # Apply mask to image
        result = image * mask2[:, :, np.newaxis]
        
        # Create white background
        background = np.ones_like(image) * 255
        background = background * (1 - mask2[:, :, np.newaxis])
        
        segmented = result + background
        
        return segmented, mask2
    
    @staticmethod
    def apply_sepia(image: np.ndarray) -> np.ndarray:
        """
        Apply sepia tone effect
        
        Args:
            image: Input image array
            
        Returns:
            Sepia-toned image array
        """
        # Sepia transformation matrix
        sepia_filter = np.array([[0.272, 0.534, 0.131],
                                [0.349, 0.686, 0.168],
                                [0.393, 0.769, 0.189]])
        
        sepia_img = cv2.transform(image, sepia_filter)
        return np.clip(sepia_img, 0, 255).astype(np.uint8)
    
    @staticmethod
    def emboss_effect(image: np.ndarray) -> np.ndarray:
        """
        Apply emboss effect
        
        Args:
            image: Input image array
            
        Returns:
            Embossed image array
        """
        kernel = np.array([[-2, -1, 0],
                          [-1,  1, 1],
                          [ 0,  1, 2]])
        
        embossed = cv2.filter2D(image, -1, kernel)
        # Add gray to make it visible
        embossed = cv2.add(embossed, np.full(embossed.shape, 128, dtype=np.uint8))
        return embossed
    
    @staticmethod
    def cartoonify(image: np.ndarray) -> np.ndarray:
        """
        Apply cartoon effect to image
        
        Args:
            image: Input image array
            
        Returns:
            Cartoonified image array
        """
        # Apply bilateral filter to smooth colors
        color = cv2.bilateralFilter(image, 9, 300, 300)
        
        # Convert to grayscale and apply median blur
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.medianBlur(gray, 7)
        
        # Detect edges
        edges = cv2.adaptiveThreshold(gray, 255, 
                                     cv2.ADAPTIVE_THRESH_MEAN_C,
                                     cv2.THRESH_BINARY, 9, 9)
        
        # Combine color and edges
        edges = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
        cartoon = cv2.bitwise_and(color, edges)
        
        return cartoon
    
    @staticmethod
    def resize_image(image: np.ndarray, width: int, height: int, 
                    maintain_aspect: bool = True) -> np.ndarray:
        """
        Resize image to specified dimensions
        
        Args:
            image: Input image array
            width: Target width
            height: Target height
            maintain_aspect: Whether to maintain aspect ratio
            
        Returns:
            Resized image array
        """
        if maintain_aspect:
            h, w = image.shape[:2]
            aspect = w / h
            
            if width / height > aspect:
                width = int(height * aspect)
            else:
                height = int(width / aspect)
        
        return cv2.resize(image, (width, height), interpolation=cv2.INTER_LANCZOS4)
    
    @staticmethod
    def apply_custom_kernel(image: np.ndarray, kernel: np.ndarray) -> np.ndarray:
        """
        Apply custom convolution kernel to image
        
        Args:
            image: Input image array
            kernel: Custom convolution kernel
            
        Returns:
            Convolved image array
        """
        # Apply convolution to each channel
        if len(image.shape) == 3:
            result = np.zeros_like(image, dtype=np.uint8)
            for c in range(image.shape[2]):
                convolved = ImageProcessor.convolve2d(image[:, :, c].astype(np.float64), kernel)
                result[:, :, c] = np.clip(convolved, 0, 255).astype(np.uint8)
            return result
        else:
            convolved = ImageProcessor.convolve2d(image.astype(np.float64), kernel)
            return np.clip(convolved, 0, 255).astype(np.uint8)
    
    @staticmethod
    def kmeans_segmentation(image: np.ndarray, k: int = 3, max_iterations: int = 100) -> np.ndarray:
        """
        Perform K-means clustering using optimized cv2.kmeans (much faster than manual)
        
        Args:
            image: Input image array
            k: Number of clusters
            max_iterations: Maximum number of iterations
            
        Returns:
            Segmented image array
        """
        # Reshape image to 2D array of pixels
        original_shape = image.shape
        if len(image.shape) == 3:
            pixel_values = image.reshape((-1, 3))
        else:
            pixel_values = image.reshape((-1, 1))
        
        # Convert to float32
        pixel_values = np.float32(pixel_values)
        
        # Define criteria and apply kmeans (cv2 is optimized)
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, max_iterations, 0.2)
        _, labels, centers = cv2.kmeans(pixel_values, k, None, criteria, 10, 
                                        cv2.KMEANS_RANDOM_CENTERS)
        
        # Convert back to uint8
        centers = np.uint8(centers)
        segmented = centers[labels.flatten()]
        
        # Reshape back to original image shape
        segmented_image = segmented.reshape(original_shape)
        
        return segmented_image
