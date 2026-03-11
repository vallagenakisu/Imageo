# Usage Examples and Expected Outputs

## Example 1: Gaussian Blur with Different Intensities

### Input Image:
- Natural photograph with sharp details
- Resolution: 800x600 pixels

### Steps:
1. Open image
2. Click "Gaussian Blur"
3. Test different kernel sizes:

| Kernel Size | Sigma | Effect | Use Case |
|-------------|-------|--------|----------|
| 3 | Auto | Slight blur | Subtle noise reduction |
| 5 | Auto | Moderate blur | General smoothing |
| 7 | Auto | Noticeable blur | Heavy noise reduction |
| 11 | Auto | Strong blur | Artistic effect |
| 21 | Auto | Very strong blur | Background blur effect |

### Expected Output:
- Larger kernel = More blur
- Edge preservation depends on sigma
- Processing time increases with kernel size

---

## Example 2: Comparing Three Blur Types

### Test Image: Portrait with noise

### Gaussian Blur (kernel=5):
**Effect:** Smooth blur, edges slightly preserved
**Best for:** General purpose noise reduction
**Speed:** Moderate

### Average Blur (kernel=5):
**Effect:** Uniform blur, edges more blurred
**Best for:** Simple smoothing
**Speed:** Fast

### Median Blur (kernel=5):
**Effect:** Preserves edges well, removes salt-pepper noise
**Best for:** Noise with outliers
**Speed:** Slow

---

## Example 3: Canny Edge Detection Step-by-Step

### Input: Color photograph of a building

### Step-by-Step Output:

**Step 1 - Grayscale:**
- Color removed, luminance preserved
- Buildings clearly visible in gray tones

**Step 2 - Gaussian Blur:**
- Slightly smoothed
- Noise reduced
- Edges still visible

**Step 3 - Gradient Magnitude:**
- Edges highlighted as bright regions
- Uniform areas appear dark
- Shows edge strength

**Step 4 - Non-Maximum Suppression:**
- Edges are now thin lines (1 pixel wide)
- Blurry edges removed
- Only edge peaks remain

**Step 5 - Double Threshold:**
- White pixels: Strong edges (threshold ≥ 150)
- Gray pixels: Weak edges (50 ≤ threshold < 150)
- Black pixels: Non-edges (threshold < 50)

**Step 6 - Final Edges:**
- Clean edge map
- Connected edges
- Weak edges removed if not connected to strong edges

### Threshold Comparison:

| Low | High | Result |
|-----|------|--------|
| 30 | 100 | Many edges, some noise |
| 50 | 150 | Balanced result |
| 70 | 200 | Only strong edges |
| 100 | 250 | Very few edges |

---

## Example 4: Custom Kernel Applications

### Test Image: Portrait photo

### Edge Detection Kernel:
```
-1  -1  -1
-1   8  -1
-1  -1  -1
```
**Result:** White edges on black background
**Use:** Find object boundaries

### Sharpen Kernel:
```
 0  -1   0
-1   5  -1
 0  -1   0
```
**Result:** Enhanced details and edges
**Use:** Make blurry images crisper

### Emboss Kernel:
```
-2  -1   0
-1   1   1
 0   1   2
```
**Result:** 3D raised effect
**Use:** Artistic styling

### Horizontal Edge Kernel:
```
-1  -1  -1
 0   0   0
 1   1   1
```
**Result:** Only horizontal edges detected
**Use:** Detect horizontal features

### Custom Example - Extreme Sharpen:
```
0,-2,0;-2,9,-2;0,-2,0
```
**Result:** Very sharp, may create artifacts
**Use:** Extremely blurry images

---

## Example 5: K-Means Segmentation

### Test Image: Landscape with sky, grass, trees

### k=2 (Binary Segmentation):
**Clusters:** 
- Cluster 1: Dark regions (trees, shadows)
- Cluster 2: Light regions (sky, grass)

**Result:** Two distinct colors
**Use:** Simple foreground/background separation

### k=3 (Three Segments):
**Clusters:**
- Cluster 1: Sky (blue)
- Cluster 2: Trees (dark green)
- Cluster 3: Grass (light green)

**Result:** Three distinct colors
**Use:** Basic scene segmentation

### k=5 (Detailed Segmentation):
**Clusters:**
- Cluster 1: Sky
- Cluster 2: Tree trunks
- Cluster 3: Tree leaves
- Cluster 4: Grass
- Cluster 5: Shadows

**Result:** Five distinct colors
**Use:** Detailed color analysis

### k=8 (Very Detailed):
**Clusters:** 8 different color regions
**Result:** More nuanced segmentation
**Use:** Color palette extraction

**Performance Note:**
- k=2: ~2 seconds
- k=3: ~3 seconds
- k=5: ~5 seconds
- k=8: ~8-10 seconds
(on 800x600 image)

---

## Example 6: Workflow - Photo Enhancement

### Original Image: Slightly blurry portrait with noise

**Step 1 - Noise Reduction:**
- Apply Median Blur (kernel=3)
- Result: Noise removed, edges preserved

**Step 2 - Sharpening:**
- Apply Custom Kernel: Sharpen preset
- Result: Details enhanced

**Step 3 - Edge Detection:**
- Apply Canny (low=40, high=120)
- Result: Clear edge map

**Step 4 - Compare:**
- Use Undo/Redo to compare before/after
- Save best result

---

## Example 7: Workflow - Artistic Effect

### Original Image: Nature photograph

**Step 1 - Blur Background:**
- Apply Gaussian Blur (kernel=15, sigma=3.0)
- Result: Dreamy, soft appearance

**Step 2 - Edge Enhancement:**
- Undo blur
- Apply Custom Kernel: Edge Detection
- Result: Line art style

**Step 3 - Color Segmentation:**
- Undo previous
- Apply K-Means (k=4)
- Result: Posterized, cartoon-like appearance

**Step 4 - Combine Effects:**
- Save segmented version
- Open original
- Apply light blur + cartoon effect
- Result: Stylized artwork

---

## Example 8: Kernel Experimentation

### Creating Custom Effects:

**Blur Variation 1 - Weighted Center:**
```
1,2,1;2,4,2;1,2,1
```
(Normalized: divide by 16)
**Result:** Gaussian-like blur

**Blur Variation 2 - Strong Center:**
```
1,1,1;1,10,1;1,1,1
```
(Normalized: divide by 18)
**Result:** Less blur, maintains center detail

**Edge Variation - Diagonal:**
```
-1,0,1;0,0,0;1,0,-1
```
**Result:** Diagonal edges emphasized

**Custom Effect - Motion Blur:**
```
0,0,0,0,1;0,0,0,1,0;0,0,1,0,0;0,1,0,0,0;1,0,0,0,0
```
(Normalized: divide by 5)
**Result:** Diagonal motion blur

---

## Performance Benchmarks

### Test System: 
- Processor: Mid-range CPU
- RAM: 8GB
- Image: 800x600 (480k pixels)

### Blur Operations:

| Operation | Kernel Size | Time |
|-----------|-------------|------|
| Gaussian Blur | 3x3 | ~0.5s |
| Gaussian Blur | 5x5 | ~1.0s |
| Gaussian Blur | 11x11 | ~3.0s |
| Average Blur | 5x5 | ~0.8s |
| Median Blur | 3x3 | ~2.0s |
| Median Blur | 5x5 | ~5.0s |

### Other Operations:

| Operation | Parameters | Time |
|-----------|------------|------|
| Canny Edge Detection | low=50, high=150 | ~3.0s |
| Custom Kernel | 3x3 | ~0.8s |
| K-Means | k=3 | ~3.0s |
| K-Means | k=5 | ~5.0s |
| K-Means | k=8 | ~8.0s |

---

## Common Issues and Solutions

### Issue 1: Blur too slow
**Solution:** 
- Use smaller kernel size
- Resize image before processing
- Choose Average blur over Median

### Issue 2: Canny edges incomplete
**Solution:**
- Lower both thresholds
- Try: low=30, high=90

### Issue 3: K-means creates noise
**Solution:**
- Blur image before segmentation
- Use fewer clusters (k=3 instead of k=6)

### Issue 4: Custom kernel produces strange colors
**Solution:**
- Check kernel normalization
- For blur kernels, ensure sum = 1
- Example: `1,1,1;1,1,1;1,1,1` should be divided by 9

### Issue 5: Out of memory
**Solution:**
- Process smaller images
- Reduce number of K-means clusters
- Close other applications

---

## Quality Comparison

### Blur Quality (subjective):

**Gaussian > Average > Median**
- Gaussian: Smoothest, most natural
- Average: Good for simple tasks
- Median: Best for noise, but pixelated

### Edge Detection Accuracy:

**Canny > Sobel > Custom kernels**
- Canny: Most accurate, complete edges
- Sobel: Fast but noisy
- Custom: Depends on kernel design

### Segmentation Quality:

**Optimal k depends on image:**
- Simple images: k=2-3
- Complex images: k=5-7
- Don't exceed k=10 (diminishing returns)

---

## Tips for Best Results

1. **Always start with noise reduction** before edge detection
2. **Experiment with thresholds** - no "perfect" value
3. **Use Undo frequently** to compare results
4. **Save intermediate steps** for comparison
5. **Resize large images** before processing
6. **Try different blur types** - each has strengths
7. **Combine effects** for artistic results
8. **Document your settings** for reproducibility
