# Histogram Analysis & Equalization Feature

## Overview
A comprehensive histogram analysis tool that displays the original and equalized versions of an image along with their statistical distributions.

## Features

### Visualization Layout (2×4 Grid)

#### Row 1: Original Image Analysis
1. **Original Image** - Grayscale version of the input image
2. **Histogram** - Frequency distribution of pixel intensities (0-255)
3. **PDF (Probability Density Function)** - Normalized histogram showing probability of each intensity
4. **CDF (Cumulative Distribution Function)** - Cumulative probability distribution

#### Row 2: Equalized Image Analysis
5. **Equalized Image** - Result of histogram equalization
6. **Histogram (Equalized)** - More uniformly distributed intensity frequencies
7. **PDF (Equalized)** - Normalized probability distribution after equalization
8. **CDF (Equalized)** - More linear cumulative distribution

## What is Histogram Equalization?

Histogram equalization is an image enhancement technique that:
- Improves contrast in images with low dynamic range
- Spreads out intensity values more uniformly
- Makes details more visible in dark or washed-out images

### Mathematical Process

1. **Calculate Histogram**: `H(i)` = count of pixels with intensity `i`
2. **Calculate PDF**: `PDF(i) = H(i) / total_pixels`
3. **Calculate CDF**: `CDF(i) = Σ PDF(j)` for `j = 0 to i`
4. **Transform**: `new_intensity(i) = round(CDF(i) × 255)`

## Usage

1. **Load an Image** in the main application
2. **Click** "Histogram Analysis & Equalization" button in the Enhancement group
3. **View** the 8-panel analysis window showing:
   - Original vs Equalized images
   - Histograms comparing intensity distributions
   - PDF curves showing probability densities
   - CDF curves showing cumulative distributions
4. **Optional**: Click "Apply Equalization to Main Image" to use the equalized version

## Visual Indicators

### Color Coding
- **Cyan (#00d4ff)**: Histogram bars and lines
- **Green (#00ff88)**: PDF (Probability Density Function)
- **Orange (#ff9500)**: CDF (Cumulative Distribution Function)

### Chart Features
- Dark themed to match application style
- Grid lines for easier reading
- Filled areas under curves for visual clarity
- Consistent x-axis (0-255 pixel intensity)
- CDF normalized to 0-1 range

## When to Use Histogram Equalization

### Good Use Cases ✅
- Low contrast images (foggy, hazy)
- Underexposed or overexposed photos
- Medical images (X-rays, CT scans)
- Satellite imagery
- Old photographs
- Images with narrow intensity range

### Poor Use Cases ❌
- Already high-contrast images (may over-enhance)
- Images with important color information (converts to grayscale)
- Artistic photos where mood depends on specific tones
- Images with intentional low/high key lighting

## Technical Details

### Implementation
- **Library**: OpenCV's `cv2.equalizeHist()`
- **Input**: Grayscale image (automatically converted if color)
- **Output**: Grayscale with improved contrast
- **Processing**: ~10-50ms for typical images

### Algorithm Steps
```python
1. Convert to grayscale (if needed)
2. Calculate histogram (256 bins)
3. Compute PDF: histogram / total_pixels
4. Compute CDF: cumulative sum of PDF
5. Map intensities: new = CDF × 255
6. Apply mapping to all pixels
```

### Histogram Calculations
```python
# Histogram
hist = cv2.calcHist([image], [0], None, [256], [0, 256])

# PDF (Probability Density Function)
pdf = hist / hist.sum()

# CDF (Cumulative Distribution Function)
cdf = pdf.cumsum()
```

## Understanding the Plots

### Histogram
- **X-axis**: Pixel intensity (0 = black, 255 = white)
- **Y-axis**: Frequency (number of pixels)
- **Interpretation**: 
  - Peaks show common intensities
  - Narrow distribution = low contrast
  - Wide distribution = high contrast

### PDF (Probability Density Function)
- **X-axis**: Pixel intensity
- **Y-axis**: Probability (0-1)
- **Interpretation**:
  - Normalized version of histogram
  - Area under curve = 1.0
  - Shows relative likelihood of intensities

### CDF (Cumulative Distribution Function)
- **X-axis**: Pixel intensity
- **Y-axis**: Cumulative probability (0-1)
- **Interpretation**:
  - Monotonically increasing
  - Value at x = probability of pixel ≤ x
  - Steep slope = high frequency range
  - Flat slope = low frequency range
  - Ideal equalized CDF is linear diagonal

## Comparison: Before vs After

### Before Equalization (Original)
- CDF may be steep in some regions (overrepresented intensities)
- CDF may be flat in others (underrepresented intensities)
- Histogram concentrated in limited range
- Low overall contrast

### After Equalization
- CDF approximately linear (uniform distribution)
- Histogram spread more evenly across 0-255
- Better utilization of available intensity range
- Enhanced contrast and detail visibility

## Example Interpretations

### Scenario 1: Dark Image
- **Original**: Histogram peaks at low intensities (0-100)
- **Original CDF**: Reaches 1.0 early, flat after 100
- **Equalized**: Histogram spread across full range
- **Equalized CDF**: More linear, utilizing full dynamic range

### Scenario 2: Low Contrast Image
- **Original**: Histogram narrow peak (e.g., 100-150)
- **Original CDF**: Steep slope in narrow region
- **Equalized**: Histogram stretched to 0-255
- **Equalized CDF**: Linear, better contrast

### Scenario 3: Already Uniform Image
- **Original**: Histogram already distributed
- **Original CDF**: Already relatively linear
- **Equalized**: Minimal change
- **Equalized CDF**: Slightly more linear

## Integration with Application

### Button Location
- **Group**: Enhancement
- **Position**: First button (above Contrast & Sharpen)
- **Label**: "Histogram Analysis & Equalization"

### Workflow
1. Analysis is non-destructive (doesn't modify main image)
2. View statistics and distributions
3. Decide if equalization is beneficial
4. Optionally apply to main image
5. Can undo with Ctrl+Z if not satisfied

### Dialog Features
- **Scrollable**: Accommodates all 8 panels
- **Resizable**: Window can be enlarged for detail
- **Apply Button**: Applies equalization to main image
- **Close Button**: Closes without applying

## Performance

### Processing Time
- Histogram calculation: ~5ms
- PDF/CDF computation: ~1ms
- Equalization: ~10-30ms
- Visualization: ~50-100ms
- **Total**: ~70-140ms

### Memory Usage
- Original image: n bytes
- Grayscale conversion: n bytes
- Equalized image: n bytes
- Histograms: 256×4 = 1KB each
- **Total**: ~3n + 4KB

## Educational Value

This feature helps understand:
- **Histogram**: Distribution of pixel intensities
- **PDF**: Probability theory applied to images
- **CDF**: Cumulative statistics and transformation mapping
- **Equalization**: How transformation improves contrast
- **Visual Comparison**: Before/after effects

## Code Structure

### Dialog Class
```python
HistogramAnalysisDialog(QDialog):
    __init__(image, parent)
    apply_equalization()
```

### Main Application Method
```python
ImageProcessorApp:
    show_histogram_analysis()
```

### Key Components
- **Matplotlib Integration**: FigureCanvasQTAgg for plotting
- **2×4 Subplot Grid**: Organized visualization
- **Dark Theme**: Matches application style
- **Interactive**: Apply button for immediate use

## Dependencies

- **OpenCV**: `cv2.calcHist()`, `cv2.equalizeHist()`
- **NumPy**: Array operations, cumsum
- **Matplotlib**: Visualization (Qt5Agg backend)
- **PyQt5**: Dialog and widgets

## Future Enhancements (Optional)

1. **CLAHE**: Contrast Limited Adaptive Histogram Equalization
2. **Color Equalization**: Per-channel or HSV-based
3. **Comparison Mode**: Side-by-side with synchronized zoom
4. **Export**: Save plots as images
5. **Statistics Table**: Mean, std dev, entropy, etc.
6. **Custom Mapping**: User-defined transformation curves
7. **Animation**: Show transformation process
8. **Batch Processing**: Apply to multiple images

## Tips

### For Best Results
- Use on grayscale or low-contrast images
- Check CDF linearity after equalization
- Compare before/after visually
- Consider CLAHE for better local contrast
- May need to adjust brightness after equalization

### Troubleshooting
- **No visible change**: Image already well-distributed
- **Over-enhanced**: Original had good contrast
- **Noise amplified**: Try denoising before equalization
- **Color loss**: Feature works on grayscale only
