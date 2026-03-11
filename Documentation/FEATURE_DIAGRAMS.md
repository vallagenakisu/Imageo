# Feature Implementation Diagram

## Manual Blur Implementation Flow

```
┌─────────────────────────────────────────────────────────────┐
│                     User Interface                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  Gaussian    │  │   Average    │  │    Median    │     │
│  │    Blur      │  │     Blur     │  │     Blur     │     │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘     │
└─────────┼──────────────────┼──────────────────┼────────────┘
          │                  │                  │
          ▼                  ▼                  ▼
    ┌──────────────────────────────────────────────┐
    │         Blur Dialog (with sliders)           │
    │  ┌────────────────────────────────────────┐  │
    │  │  Kernel Size Slider: [1 --- 5 --- 25] │  │
    │  │  Sigma Slider (Gaussian only): [Auto] │  │
    │  └────────────────────────────────────────┘  │
    └──────────────────┬───────────────────────────┘
                       │
                       ▼
    ┌──────────────────────────────────────────────┐
    │         Create Kernel                        │
    │  • Gaussian: Mathematical formula            │
    │  • Average: Uniform weights                  │
    │  • Median: Sorting operation                 │
    └──────────────────┬───────────────────────────┘
                       │
                       ▼
    ┌──────────────────────────────────────────────┐
    │         Manual Convolution                   │
    │  For each pixel (i,j):                       │
    │    1. Extract neighborhood                   │
    │    2. Element-wise multiply with kernel      │
    │    3. Sum all products                       │
    │    4. Store result                           │
    └──────────────────┬───────────────────────────┘
                       │
                       ▼
    ┌──────────────────────────────────────────────┐
    │         Clip & Convert to uint8              │
    └──────────────────┬───────────────────────────┘
                       │
                       ▼
               ┌─────────────┐
               │   Result    │
               └─────────────┘
```

---

## Manual Canny Edge Detection Flow

```
┌────────────────────────────────────────────────────────────┐
│                    Input Image                             │
└────────────────────────┬───────────────────────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────────────────────┐
│  STEP 1: Grayscale Conversion                              │
│  • BGR → Gray using cv2.cvtColor()                         │
└────────────────────────┬───────────────────────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────────────────────┐
│  STEP 2: Gaussian Blur (Noise Reduction)                   │
│  • Manual Gaussian kernel (5x5)                            │
│  • Convolution to smooth image                             │
└────────────────────────┬───────────────────────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────────────────────┐
│  STEP 3: Gradient Calculation (Sobel)                      │
│  • Sobel X: [-1 0 1; -2 0 2; -1 0 1]                      │
│  • Sobel Y: [-1 -2 -1; 0 0 0; 1 2 1]                      │
│  • Magnitude: √(Gx² + Gy²)                                 │
│  • Direction: arctan2(Gy, Gx)                              │
└────────────────────────┬───────────────────────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────────────────────┐
│  STEP 4: Non-Maximum Suppression                           │
│  • For each pixel:                                         │
│    - Check gradient direction (0°, 45°, 90°, 135°)        │
│    - Compare with neighbors along gradient                 │
│    - Keep only local maxima                                │
│    - Suppress others                                       │
└────────────────────────┬───────────────────────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────────────────────┐
│  STEP 5: Double Thresholding                               │
│  • Strong edges: magnitude ≥ high_threshold                │
│  • Weak edges: low_threshold ≤ magnitude < high_threshold │
│  • Non-edges: magnitude < low_threshold                    │
└────────────────────────┬───────────────────────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────────────────────┐
│  STEP 6: Edge Tracking by Hysteresis                       │
│  • Keep all strong edges                                   │
│  • For each weak edge:                                     │
│    - If connected to strong edge → keep                    │
│    - Otherwise → discard                                   │
└────────────────────────┬───────────────────────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────────────────────┐
│                    Final Edge Image                         │
└────────────────────────┬───────────────────────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────────────────────┐
│           Display All Intermediate Steps                    │
│  • Scrollable dialog with all 6 images                     │
└────────────────────────────────────────────────────────────┘
```

---

## Custom Kernel Convolution Flow

```
┌────────────────────────────────────────────────────────────┐
│                Custom Kernel Dialog                         │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Preset Selector:  [Edge Detection ▼]               │  │
│  │                                                      │  │
│  │  Kernel Input:                                       │  │
│  │  -1,-1,-1;-1,8,-1;-1,-1,-1                          │  │
│  │                                                      │  │
│  │  [OK]  [Cancel]                                      │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────┬───────────────────────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────────────────────┐
│              Parse Kernel String                            │
│  • Split by semicolon (rows)                               │
│  • Split each row by comma (values)                        │
│  • Convert to numpy array                                  │
│  • Validate dimensions                                     │
└────────────────────────┬───────────────────────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────────────────────┐
│         Apply Convolution (apply_custom_kernel)             │
│  • For each channel (if color image)                       │
│  • Call convolve2d() with custom kernel                    │
└────────────────────────┬───────────────────────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────────────────────┐
│                  Display Result                             │
└────────────────────────────────────────────────────────────┘


Preset Kernels Available:

┌─────────────────┬─────────────────┬─────────────────┐
│ Edge Detection  │    Sharpen      │     Emboss      │
├─────────────────┼─────────────────┼─────────────────┤
│ -1  -1  -1      │  0  -1   0      │ -2  -1   0      │
│ -1   8  -1      │ -1   5  -1      │ -1   1   1      │
│ -1  -1  -1      │  0  -1   0      │  0   1   2      │
└─────────────────┴─────────────────┴─────────────────┘

┌─────────────────┬─────────────────┬─────────────────┐
│ Horizontal Edge │  Vertical Edge  │    Box Blur     │
├─────────────────┼─────────────────┼─────────────────┤
│ -1  -1  -1      │ -1   0   1      │  1   1   1      │
│  0   0   0      │ -1   0   1      │  1   1   1      │
│  1   1   1      │ -1   0   1      │  1   1   1      │
└─────────────────┴─────────────────┴─────────────────┘
```

---

## K-Means Segmentation Flow

```
┌────────────────────────────────────────────────────────────┐
│              Input: Image & k (clusters)                    │
└────────────────────────┬───────────────────────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────────────────────┐
│           Reshape Image to 2D Array                         │
│  • (height × width × channels) → (n_pixels, channels)      │
└────────────────────────┬───────────────────────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────────────────────┐
│         Initialize k Random Centroids                       │
│  • Randomly select k pixels as initial centroids           │
└────────────────────────┬───────────────────────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────────────────────┐
│              ITERATION LOOP (max 100)                       │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  1. Assign Pixels to Nearest Centroid                │  │
│  │     • Calculate distance to each centroid            │  │
│  │     • dist = ||pixel - centroid||                    │  │
│  │     • Assign to closest centroid                     │  │
│  │                                                       │  │
│  │  2. Update Centroids                                 │  │
│  │     • For each cluster:                              │  │
│  │       new_centroid = mean(assigned_pixels)           │  │
│  │                                                       │  │
│  │  3. Check Convergence                                │  │
│  │     • If centroids didn't change → STOP              │  │
│  │     • Otherwise → continue iteration                 │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────┬───────────────────────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────────────────────┐
│         Create Segmented Image                              │
│  • Replace each pixel with its centroid color              │
│  • Reshape back to original dimensions                     │
└────────────────────────┬───────────────────────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────────────────────┐
│                Display Segmented Result                     │
└────────────────────────────────────────────────────────────┘


Visual Example (k=3):

Original Image:              Segmented Image:
┌──────────────┐            ┌──────────────┐
│ ░░▒▒▓▓██     │   ───→     │ ░░░░████     │
│ ░▒▒▓▓▓██     │            │ ░░░░████     │
│ ▒▒▓▓███      │            │ ▒▒▒▒████     │
│ ▓▓███        │            │ ████████     │
└──────────────┘            └──────────────┘
  Many colors                3 distinct colors
```

---

## Data Flow Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      main.py (UI Layer)                      │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  PhotoEditorApp (Main Window)                         │  │
│  │  • Menu bar & Toolbar                                 │  │
│  │  • Control Panel (buttons & sliders)                  │  │
│  │  • Image Display Area                                 │  │
│  │  • History Management (Undo/Redo)                     │  │
│  └─────────────────────┬─────────────────────────────────┘  │
│                        │                                     │
│  ┌─────────────────────┴─────────────────────────────────┐  │
│  │  Dialog Classes                                       │  │
│  │  • BlurDialog         (slider controls)               │  │
│  │  • CustomKernelDialog (kernel input)                  │  │
│  │  • CannyIntermediatesDialog (step viewer)             │  │
│  │  • CropDialog         (interactive crop)              │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────┬───────────────────────────────────┘
                          │ Calls methods
                          ▼
┌─────────────────────────────────────────────────────────────┐
│              image_processor.py (Processing Layer)           │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  ImageProcessor (Static Methods)                      │  │
│  │  ┌─────────────────────────────────────────────────┐  │  │
│  │  │  Core Functions:                                │  │  │
│  │  │  • convolve2d()                                 │  │  │
│  │  │  • create_gaussian_kernel()                     │  │  │
│  │  ├─────────────────────────────────────────────────┤  │  │
│  │  │  Blur Functions:                                │  │  │
│  │  │  • gaussian_blur()                              │  │  │
│  │  │  • average_blur()                               │  │  │
│  │  │  • median_blur()                                │  │  │
│  │  ├─────────────────────────────────────────────────┤  │  │
│  │  │  Edge Detection:                                │  │  │
│  │  │  • canny_edge_detection_manual()                │  │  │
│  │  │  • sobel_edge_detection()                       │  │  │
│  │  ├─────────────────────────────────────────────────┤  │  │
│  │  │  New Features:                                  │  │  │
│  │  │  • apply_custom_kernel()                        │  │  │
│  │  │  • kmeans_segmentation()                        │  │  │
│  │  └─────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────┬───────────────────────────────────┘
                          │ Uses
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                 External Libraries                           │
│  • NumPy:  Array operations, mathematical functions          │
│  • OpenCV: Color space conversion, basic I/O                 │
│  • PyQt5:  GUI components, event handling                    │
└─────────────────────────────────────────────────────────────┘
```
