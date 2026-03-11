# Quick Reference - New Features

## 1. Manual Blur Functions

### How to Use:
- Click any blur button (Gaussian/Average/Median)
- Use the **intensity slider** to adjust kernel size (1-25)
- For Gaussian blur: Also adjust **sigma slider** for standard deviation
- Click OK to apply

### Behind the Scenes:
- Uses manual 2D convolution
- No cv2.blur(), cv2.GaussianBlur(), or cv2.medianBlur()
- Gaussian kernel generated from mathematical formula
- Each pixel computed individually using kernel weights

---

## 2. Manual Canny Edge Detection

### How to Use:
- Click "Canny Edge Detection (Manual)"
- Enter **low threshold** (e.g., 50)
- Enter **high threshold** (e.g., 150)
- View result and intermediate steps popup

### Intermediate Steps Shown:
1. **Grayscale** - Original converted to grayscale
2. **Gaussian Blur** - Noise reduction
3. **Gradient Magnitude** - Edge strength (Sobel)
4. **Non-Maximum Suppression** - Thin edges
5. **Double Threshold** - Strong/weak edge classification
6. **Final Edges** - After hysteresis tracking

### Tips:
- Lower threshold: More edges detected
- Higher threshold: Only strong edges
- Typical range: Low=50, High=150

---

## 3. Custom Kernel Convolution

### How to Use:
- Click "Apply Custom Kernel"
- Select preset OR enter custom values
- Format: `val1,val2,val3;val4,val5,val6;val7,val8,val9`
- Click OK to apply

### Preset Kernels:

**Edge Detection:**
```
-1  -1  -1
-1   8  -1
-1  -1  -1
```

**Sharpen:**
```
 0  -1   0
-1   5  -1
 0  -1   0
```

**Emboss:**
```
-2  -1   0
-1   1   1
 0   1   2
```

**Horizontal Edge:**
```
-1  -1  -1
 0   0   0
 1   1   1
```

**Vertical Edge:**
```
-1   0   1
-1   0   1
-1   0   1
```

**Box Blur:**
```
1  1  1
1  1  1
1  1  1
```

### Custom Kernel Examples:

**Identity (no change):**
```
0,0,0;0,1,0;0,0,0
```

**Strong Edge Detection:**
```
-1,-1,-1;-1,9,-1;-1,-1,-1
```

**Diagonal Edge:**
```
-1,0,1;0,0,0;1,0,-1
```

---

## 4. K-Means Segmentation

### How to Use:
- Click "K-Means Clustering"
- Enter number of clusters (2-10)
- Wait for processing
- View segmented result

### Understanding Results:
- **k=2**: Binary segmentation (foreground/background)
- **k=3-5**: Useful for color-based grouping
- **k=6-10**: More detailed segmentation

### Tips:
- Start with k=3 for general segmentation
- Larger k = more segments but slower processing
- Works best on images with distinct color regions

### Performance:
- Small image (< 500x500): Fast
- Medium image (500-1000): Moderate
- Large image (> 1000): Slow (may take 10-30 seconds)

---

## Keyboard Shortcuts

- **Ctrl+O**: Open Image
- **Ctrl+S**: Save Image
- **Ctrl+Shift+S**: Save As
- **Ctrl+Z**: Undo
- **Ctrl+Y**: Redo
- **Ctrl+Q**: Exit

---

## Workflow Examples

### Example 1: Edge Enhancement
1. Open image
2. Apply Gaussian blur (kernel=3) to reduce noise
3. Apply Canny edge detection
4. Review intermediate steps
5. Adjust thresholds if needed

### Example 2: Custom Filter
1. Open image
2. Click "Apply Custom Kernel"
3. Select "Sharpen" preset
4. Click OK
5. Compare with original using Undo

### Example 3: Color Segmentation
1. Open colorful image
2. Click "K-Means Clustering"
3. Try k=3, k=5, k=7
4. Use Undo to compare results
5. Choose best segmentation

### Example 4: Blur Comparison
1. Open image
2. Apply Gaussian blur (save image)
3. Undo, apply Average blur (save as different file)
4. Undo, apply Median blur (save as different file)
5. Compare all three results

---

## Troubleshooting

### Blur is too slow:
- Reduce kernel size
- Use smaller image
- Average blur is fastest, Median is slowest

### Canny edges are weak:
- Lower the low threshold
- Lower the high threshold
- Try 30/100 instead of 50/150

### K-means taking too long:
- Reduce number of clusters
- Resize image first
- Maximum 100 iterations (auto-stops)

### Custom kernel doesn't work:
- Check format: comma between values, semicolon between rows
- Ensure all rows have same number of values
- Example: `1,2,3;4,5,6;7,8,9` for 3x3

---

## Algorithm Details

### Convolution Formula:
```
output[i,j] = Σ Σ (image[i+m, j+n] × kernel[m,n])
```

### Gaussian Kernel:
```
G(x,y) = (1 / 2πσ²) × exp(-(x² + y²) / 2σ²)
```

### Gradient Magnitude:
```
|G| = √(Gx² + Gy²)
```

### K-Means Distance:
```
d = √(Σ(pixel - centroid)²)
```
