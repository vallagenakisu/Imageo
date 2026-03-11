# Photo Editor - User Guide

## Table of Contents
1. [Getting Started](#getting-started)
2. [Interface Overview](#interface-overview)
3. [Basic Operations](#basic-operations)
4. [Image Processing Features](#image-processing-features)
5. [Tips and Tricks](#tips-and-tricks)
6. [Keyboard Shortcuts](#keyboard-shortcuts)

## Getting Started

### First Launch

1. Run the application by executing `python main.py` or double-clicking `PhotoEditor.exe`
2. Click "Open Image" button or use `File → Open Image` (Ctrl+O)
3. Select an image file (JPG, PNG, or BMP format)
4. Your image will appear in the main workspace

### Recommended Workflow

```
Open Image → Apply Effects → Adjust Settings → Save Result
```

## Interface Overview

### Main Window Components

```
┌─────────────────────────────────────────────────────────┐
│ Menu Bar: File | Edit | Help                            │
├─────────────────────────────────────────────────────────┤
│ Toolbar: [Open] [Save] [Undo] [Redo]                   │
├──────────────┬──────────────────────────────────────────┤
│              │                                           │
│   Control    │         Image Display Area               │
│   Panel      │         (Your Image Here)                │
│              │                                           │
│  [Buttons]   │                                           │
│  [Sliders]   │                                           │
│              │                                           │
├──────────────┴──────────────────────────────────────────┤
│ Status Bar: Image dimensions and current operation      │
└─────────────────────────────────────────────────────────┘
```

### Control Panel Sections

1. **Blur Effects** - Smoothing and noise reduction
2. **Edge Detection** - Find edges and contours
3. **Enhancement** - Improve image quality
4. **Transform** - Rotate, flip, and crop
5. **Adjustments** - Real-time brightness and saturation
6. **Effects** - Artistic and special effects

## Basic Operations

### Opening an Image

**Method 1: Toolbar**
- Click "Open Image" button

**Method 2: Menu**
- File → Open Image

**Method 3: Keyboard**
- Press `Ctrl+O`

**Supported Formats:**
- JPEG (.jpg, .jpeg)
- PNG (.png)
- BMP (.bmp)

### Saving an Image

**Save (overwrite current file):**
- Click "Save Image" button or press `Ctrl+S`

**Save As (new file):**
- File → Save As... or press `Ctrl+Shift+S`
- Choose format and location
- For JPEG: You'll be prompted for quality (0-100, recommended: 90-95)

### Undo/Redo

**Undo last operation:**
- Click "Undo" button or press `Ctrl+Z`
- Can undo up to 20 operations

**Redo:**
- Click "Redo" button or press `Ctrl+Y`

### Reset to Original

- Click "Reset to Original" button (red button at bottom of control panel)
- This restores the image as it was when first opened

## Image Processing Features

### 1. Blur Effects

#### Gaussian Blur
**Purpose:** Smooth images while preserving edges  
**Best for:** Reducing noise, creating soft focus effect  
**Parameters:** Kernel size (1-51, odd numbers)  
**Tip:** Larger kernel = more blur

#### Average Blur
**Purpose:** Reduce noise by averaging pixels  
**Best for:** General noise reduction  
**Parameters:** Kernel size (1-51)  
**Tip:** Good for uniform noise

#### Median Blur
**Purpose:** Remove salt-and-pepper noise  
**Best for:** Speckle noise removal  
**Parameters:** Kernel size (1-51, odd numbers)  
**Tip:** Excellent for preserving edges while removing noise

### 2. Edge Detection

#### Canny Edge Detection
**Purpose:** Detect edges with optimal accuracy  
**Best for:** Object boundary detection  
**Output:** White edges on black background  
**Algorithm:** Multi-stage edge detection with gradient analysis

#### Sobel Edge Detection
**Purpose:** Gradient-based edge detection  
**Best for:** Quick edge detection  
**Output:** Edge intensity map  
**Algorithm:** First-order derivative calculation

### 3. Enhancement

#### Contrast Enhancement
**Purpose:** Improve visibility of details  
**Best for:** Low-contrast or flat images  
**Method:** CLAHE (Contrast Limited Adaptive Histogram Equalization)  
**Tip:** Great for photos taken in poor lighting

#### Sharpen Image
**Purpose:** Enhance details and edges  
**Best for:** Slightly blurry images  
**Effect:** Makes features more defined  
**Warning:** Can amplify noise in low-quality images

### 4. Transform Operations

#### Rotate Image
**Purpose:** Rotate by any angle  
**Parameters:** Angle in degrees (-360 to 360)  
**Positive:** Counter-clockwise rotation  
**Negative:** Clockwise rotation  
**Note:** Canvas automatically adjusts to fit rotated image

#### Crop Image
**Purpose:** Cut out a specific region  
**How to use:**
1. Click "Crop Image" button
2. Click and drag on the image to select region
3. Green rectangle shows selection
4. Click "OK" to apply or "Cancel" to abort

**Tips:**
- Drag from top-left to bottom-right
- You can adjust by dragging again
- Hold mouse button while dragging

#### Flip Horizontal
**Purpose:** Mirror image left-to-right  
**Effect:** Creates horizontal mirror reflection

#### Flip Vertical
**Purpose:** Mirror image top-to-bottom  
**Effect:** Creates vertical mirror reflection

### 5. Adjustments (Real-time)

#### Brightness
**Control:** Slider (-100 to +100)  
**Effect:** Lighter or darker image  
**Real-time:** Changes appear as you move slider  
**Reset:** Set to 0 or click "Reset Adjustments"

#### Saturation
**Control:** Slider (0% to 200%)  
**Effect:** Color vibrancy  
- 0%: Grayscale (no color)
- 100%: Original colors
- 200%: Highly vibrant colors

**Real-time:** Changes appear as you move slider  
**Reset:** Set to 100 or click "Reset Adjustments"

**Note:** Both sliders work together on the original image

### 6. Artistic Effects

#### Grayscale
**Purpose:** Convert to black and white  
**Use:** Classic monochrome photography  
**Note:** Removes all color information

#### Sepia Tone
**Purpose:** Vintage photo effect  
**Effect:** Warm brown tones  
**Use:** Nostalgic or antique look

#### Emboss Effect
**Purpose:** 3D relief effect  
**Effect:** Makes image appear carved or raised  
**Best for:** Artistic rendering

#### Cartoon Effect
**Purpose:** Cartoon-style rendering  
**Method:** Bilateral filter + edge detection  
**Effect:** Simplified colors with strong edges  
**Note:** May take a few seconds to process

#### Foreground-Background Separation
**Purpose:** Isolate subject from background  
**Method:** GrabCut algorithm  
**Effect:** Subject remains, background becomes white  
**Best for:** Images with clear subject in center  
**Note:** Works best with centered subjects  
**Processing time:** May take several seconds

## Tips and Tricks

### Performance Tips

1. **Large Images:**
   - Consider working with medium-sized images (1-3 MB)
   - Very large images may slow down operations

2. **Memory Management:**
   - History is limited to 20 operations
   - If app becomes slow, restart it

3. **Real-time Adjustments:**
   - Brightness and Saturation sliders update in real-time
   - Other effects require clicking buttons

### Best Practices

1. **Save Frequently:**
   - Use "Save As" to keep original intact
   - Save different versions with descriptive names

2. **Non-Destructive Editing:**
   - Use "Reset to Original" to start over
   - Undo is available for recent operations

3. **Order Matters:**
   - Apply major transformations (rotate, crop) first
   - Apply effects and adjustments after
   - Fine-tune with brightness/saturation last

4. **Experimenting:**
   - Don't be afraid to try different effects
   - You can always undo or reset
   - Some effects combine well (e.g., sharpen + contrast)

### Common Workflows

**Portrait Enhancement:**
1. Open portrait
2. Enhance Contrast
3. Sharpen Image
4. Adjust Brightness slightly (+10 to +20)
5. Increase Saturation slightly (110-120)

**Artistic Photo:**
1. Open image
2. Apply Cartoon Effect or Sepia Tone
3. Adjust Saturation for desired mood
4. Optional: Add slight Emboss for texture

**Document Scanning:**
1. Open scanned document
2. Enhance Contrast
3. Sharpen Image
4. Optional: Convert to Grayscale

**Edge Analysis:**
1. Open image
2. Apply Gaussian Blur (small kernel)
3. Apply Canny or Sobel Edge Detection
4. Use for analysis or artistic effect

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+O` | Open Image |
| `Ctrl+S` | Save Image |
| `Ctrl+Shift+S` | Save Image As |
| `Ctrl+Z` | Undo |
| `Ctrl+Y` | Redo |
| `Ctrl+Q` | Quit Application |

## Troubleshooting

**Problem:** Image appears distorted  
**Solution:** Click "Reset to Original" and try again

**Problem:** Effect is too strong  
**Solution:** Use Undo (Ctrl+Z) and try with lower parameters

**Problem:** Sliders don't work  
**Solution:** Ensure you have an image loaded first

**Problem:** Crop dialog shows wrong size  
**Solution:** The crop coordinates are in original image pixels

**Problem:** Foreground separation doesn't work well  
**Solution:** This works best when subject is in center. Try cropping first.

**Problem:** Application is slow  
**Solution:** Restart application, work with smaller images

## Getting Help

- Check this user guide
- Review SETUP.md for installation issues
- Check README.md for feature overview

## Version Information

**Current Version:** 1.0  
**Release Date:** October 2025  
**Platform:** Windows, Linux, macOS

---

Enjoy editing your photos! 📸✨
