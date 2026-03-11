# Photo Editor Desktop Application

A powerful and user-friendly desktop photo editing application built with Python, PyQt5, and OpenCV.

## Features

### Image Processing Operations
1. **Gaussian Blur** - Smooth images while preserving edges
2. **Average Blur** - Reduce noise by averaging neighboring pixels
3. **Edge Detection** - Canny and Sobel edge detection algorithms
4. **Contrast Enhancement** - Stretch intensity levels for better visibility
5. **Image Rotation** - Rotate images at any custom angle
6. **Image Sharpening** - Enhance details and edges
7. **Interactive Cropping** - Select and crop specific regions
8. **Saturation Control** - Adjust color vibrancy and tone
9. **Foreground-Background Separation** - Isolate subjects using segmentation
10. **Brightness Adjustment** - Control image brightness levels
11. **Grayscale Conversion** - Convert images to grayscale
12. **Image Flip** - Flip images horizontally or vertically

### Additional Features
- **Undo/Redo** - Full edit history management
- **Real-time Preview** - See changes instantly
- **File Support** - Load and save JPG, PNG, BMP formats
- **Quality Control** - Adjustable save quality
- **Status Information** - Display image dimensions and current operation

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup Instructions

1. Clone or download this repository
2. Navigate to the project directory:
   ```bash
   cd "Image Project"
   ```

3. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Running the Application

```bash
python main.py
```

### Basic Workflow

1. **Load an Image**: Click "Open Image" button or use File menu
2. **Apply Effects**: Use toolbar buttons or menu options to apply various effects
3. **Adjust Parameters**: Use sliders to fine-tune effects in real-time
4. **Undo/Redo**: Use toolbar buttons or Ctrl+Z/Ctrl+Y shortcuts
5. **Save Result**: Click "Save Image" to export your edited image

### Keyboard Shortcuts

- `Ctrl+O` - Open Image
- `Ctrl+S` - Save Image
- `Ctrl+Z` - Undo
- `Ctrl+Y` - Redo
- `Ctrl+Q` - Quit Application

## Building Executable

To create a standalone .exe file for Windows:

```bash
pyinstaller --name="PhotoEditor" --windowed --onefile --icon=icon.ico main.py
```

The executable will be created in the `dist` folder.

## Project Structure

```
Image Project/
├── main.py                 # Main application entry point
├── image_processor.py      # Image processing operations backend
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Architecture

- **Frontend**: PyQt5 GUI with modern interface
- **Backend**: OpenCV for image manipulation
- **Integration**: Event-driven architecture connecting GUI to processing functions
- **History Management**: Stack-based undo/redo system

## Technical Details

### Technologies Used
- **PyQt5**: GUI framework
- **OpenCV**: Image processing operations
- **NumPy**: Numerical operations on arrays
- **Pillow**: Additional image format support

### Performance
- Optimized for real-time preview
- Efficient memory management
- Supports high-resolution images

## Development

### Code Structure
- Modular design with clear separation of concerns
- Well-documented functions
- Type hints for better code clarity
- Error handling for robust operation

## License

This project is created for educational purposes.

## Author

Created as part of Image Processing Lab coursework.

## Support

For issues or questions, please refer to the source code documentation.

## Screen Recordings

Watch the application in action through the following screen recordings:

### Blur

<video src="Screen%20Recoding/Blur.mp4" controls width="700"></video>

### Canny Edge Detection

<video src="Screen%20Recoding/Canny%20Edge%20Detection.mp4" controls width="700"></video>

### Convolution

<video src="Screen%20Recoding/Convolution.mp4" controls width="700"></video>

### Histogram Matching

<video src="Screen%20Recoding/Histogram%20Matching.mp4" controls width="700"></video>

### K-Mean Cluster

<video src="Screen%20Recoding/K-Mean%20Cluster.mp4" controls width="700"></video>

### Laplacian Edge

<video src="Screen%20Recoding/Laplacian%20Edge.mp4" controls width="700"></video>

### Rotate Image

<video src="Screen%20Recoding/Rotate%20Image.mp4" controls width="700"></video>
