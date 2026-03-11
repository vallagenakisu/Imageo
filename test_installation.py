"""
Installation Test Script
Verifies that all required dependencies are properly installed
"""

import sys

print("=" * 60)
print("Photo Editor - Installation Test")
print("=" * 60)
print()

# Test Python version
print("1. Testing Python version...")
python_version = sys.version_info
print(f"   Python {python_version.major}.{python_version.minor}.{python_version.micro}")

if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
    print("   ❌ ERROR: Python 3.8 or higher is required!")
    sys.exit(1)
else:
    print("   ✓ Python version is compatible")
print()

# Test PyQt5
print("2. Testing PyQt5...")
try:
    from PyQt5 import QtWidgets, QtCore, QtGui
    print(f"   ✓ PyQt5 is installed")
except ImportError as e:
    print(f"   ❌ ERROR: PyQt5 not found!")
    print(f"   Install with: pip install PyQt5")
    sys.exit(1)
print()

# Test OpenCV
print("3. Testing OpenCV...")
try:
    import cv2
    print(f"   ✓ OpenCV version: {cv2.__version__}")
except ImportError:
    print(f"   ❌ ERROR: OpenCV not found!")
    print(f"   Install with: pip install opencv-python")
    sys.exit(1)
print()

# Test NumPy
print("4. Testing NumPy...")
try:
    import numpy as np
    print(f"   ✓ NumPy version: {np.__version__}")
except ImportError:
    print(f"   ❌ ERROR: NumPy not found!")
    print(f"   Install with: pip install numpy")
    sys.exit(1)
print()

# Test Pillow
print("5. Testing Pillow...")
try:
    from PIL import Image
    import PIL
    print(f"   ✓ Pillow version: {PIL.__version__}")
except ImportError:
    print(f"   ❌ ERROR: Pillow not found!")
    print(f"   Install with: pip install Pillow")
    sys.exit(1)
print()

# Test image_processor module
print("6. Testing image_processor module...")
try:
    from image_processor import ImageProcessor
    processor = ImageProcessor()
    print(f"   ✓ ImageProcessor module loaded successfully")
except ImportError as e:
    print(f"   ❌ ERROR: Cannot import image_processor module!")
    print(f"   Error: {e}")
    sys.exit(1)
print()

# Test basic OpenCV functionality
print("7. Testing OpenCV basic functionality...")
try:
    test_img = np.zeros((100, 100, 3), dtype=np.uint8)
    blurred = cv2.GaussianBlur(test_img, (5, 5), 0)
    print(f"   ✓ OpenCV operations working correctly")
except Exception as e:
    print(f"   ❌ ERROR: OpenCV operations failed!")
    print(f"   Error: {e}")
    sys.exit(1)
print()

# Test ImageProcessor operations
print("8. Testing ImageProcessor operations...")
try:
    test_img = np.ones((100, 100, 3), dtype=np.uint8) * 128
    processor = ImageProcessor()
    
    # Test a few operations
    result1 = processor.gaussian_blur(test_img, 5)
    result2 = processor.enhance_contrast(test_img)
    result3 = processor.rotate_image(test_img, 45)
    
    print(f"   ✓ All ImageProcessor operations working correctly")
except Exception as e:
    print(f"   ❌ ERROR: ImageProcessor operations failed!")
    print(f"   Error: {e}")
    sys.exit(1)
print()

# Summary
print("=" * 60)
print("✓ ALL TESTS PASSED!")
print("=" * 60)
print()
print("Your installation is complete and working correctly.")
print("You can now run the application with: python main.py")
print()
print("To create an executable, run: python build.ps1")
print()
