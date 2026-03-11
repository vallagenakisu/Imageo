# Photo Editor Desktop Application - Setup Guide

## Quick Start

### 1. Install Dependencies

Open PowerShell in the project directory and run:

```powershell
pip install -r requirements.txt
```

### 2. Run the Application

```powershell
python main.py
```

## Building Executable (.exe) for Windows

### Using PyInstaller

1. Install PyInstaller (if not already installed):
```powershell
pip install pyinstaller
```

2. Create the executable:
```powershell
pyinstaller --name="PhotoEditor" --windowed --onefile main.py
```

3. Find your executable in the `dist` folder.

### Advanced Build Options

For a more customized build with icon and better optimization:

```powershell
pyinstaller --name="PhotoEditor" `
            --windowed `
            --onefile `
            --add-data "README.md;." `
            --hidden-import=cv2 `
            --hidden-import=numpy `
            --hidden-import=PyQt5 `
            main.py
```

## Troubleshooting

### Common Issues

**Issue: "No module named cv2"**
- Solution: `pip install opencv-python`

**Issue: "No module named PyQt5"**
- Solution: `pip install PyQt5`

**Issue: Application won't start**
- Check Python version (requires 3.8+)
- Verify all dependencies are installed: `pip list`

**Issue: Slow performance with large images**
- Try resizing images before editing
- Close other applications to free up memory

### Performance Tips

1. **For large images**: Consider resizing before applying effects
2. **Memory usage**: Close and reopen the app if working with many large files
3. **Undo history**: Limited to 20 operations to manage memory

## System Requirements

- **OS**: Windows 7/8/10/11, Linux, macOS
- **Python**: 3.8 or higher
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 500MB free space

## Feature List with Shortcuts

### File Operations
- Open Image: `Ctrl+O`
- Save Image: `Ctrl+S`
- Save As: `Ctrl+Shift+S`
- Exit: `Ctrl+Q`

### Edit Operations
- Undo: `Ctrl+Z`
- Redo: `Ctrl+Y`

### Image Processing Operations

#### Blur Effects (3 types)
1. **Gaussian Blur** - Smooth edges
2. **Average Blur** - Noise reduction
3. **Median Blur** - Salt-and-pepper noise removal

#### Edge Detection (2 algorithms)
4. **Canny Edge Detection** - Optimal edge detection
5. **Sobel Edge Detection** - Gradient-based edges

#### Enhancement (2 operations)
6. **Contrast Enhancement** - CLAHE algorithm
7. **Sharpen Image** - Detail enhancement

#### Transform (4 operations)
8. **Rotate Image** - Any angle rotation
9. **Crop Image** - Interactive selection
10. **Flip Horizontal** - Mirror image
11. **Flip Vertical** - Vertical mirror

#### Adjustments (2 controls with sliders)
12. **Brightness** - Real-time adjustment (-100 to +100)
13. **Saturation** - Color vibrancy (0% to 200%)

#### Effects (5 artistic effects)
14. **Grayscale** - Black and white conversion
15. **Sepia Tone** - Vintage photo effect
16. **Emboss Effect** - 3D relief effect
17. **Cartoon Effect** - Cartoon-style rendering
18. **Foreground-Background Separation** - Subject isolation

**Total: 18 Image Processing Operations** (exceeds the requirement of 10)

## Testing the Application

### Test with Sample Images

1. Prepare test images in different formats (JPG, PNG, BMP)
2. Test with various resolutions (low, medium, high)
3. Try each operation individually
4. Test undo/redo functionality
5. Test save with different quality settings

### Performance Testing

```powershell
# Small image (< 1MB)
# Medium image (1-5MB)
# Large image (> 5MB)
# High resolution (4K+)
```

## Development Notes

### Project Structure
```
Image Project/
├── main.py                 # Main GUI application
├── image_processor.py      # Backend processing functions
├── requirements.txt        # Dependencies
├── README.md              # User documentation
├── SETUP.md               # This file
└── dist/                  # Built executables (after build)
```

### Code Architecture

- **Separation of Concerns**: UI (main.py) separate from processing (image_processor.py)
- **Modular Design**: Each operation is a separate function
- **Error Handling**: Robust error checking for file operations
- **Memory Management**: History limited to prevent memory issues
- **Type Hints**: Clear function signatures for maintainability

### Extending the Application

To add a new image processing operation:

1. Add the processing function to `image_processor.py`:
```python
@staticmethod
def new_operation(image: np.ndarray, param: int) -> np.ndarray:
    # Your processing code here
    return processed_image
```

2. Add a button in `main.py` control panel:
```python
new_btn = QPushButton("New Operation")
new_btn.clicked.connect(self.apply_new_operation)
layout.addWidget(new_btn)
```

3. Add the handler function:
```python
def apply_new_operation(self):
    if self.current_image is None:
        return
    self.add_to_history()
    self.current_image = self.processor.new_operation(self.current_image, param)
    self.display_image()
    self.status_bar.showMessage("Applied New Operation")
```

## License

This project is created for educational purposes as part of Image Processing Lab coursework.

## Support

For issues or questions:
1. Check this documentation
2. Review the code comments
3. Test with different images and settings

---

**Version**: 1.0  
**Last Updated**: October 2025  
**Author**: Image Processing Lab Project
