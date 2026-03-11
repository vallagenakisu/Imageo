# Photo Editor - Quick Reference Card

## 🚀 Quick Start
```powershell
pip install -r requirements.txt
python main.py
```

## ⌨️ Keyboard Shortcuts
| Key | Action |
|-----|--------|
| `Ctrl+O` | Open Image |
| `Ctrl+S` | Save Image |
| `Ctrl+Shift+S` | Save As |
| `Ctrl+Z` | Undo |
| `Ctrl+Y` | Redo |
| `Ctrl+Q` | Quit |

## 🎨 18 Image Operations

### Blur (3)
- Gaussian Blur - Smooth edges
- Average Blur - Noise reduction  
- Median Blur - Salt-pepper noise

### Edges (2)
- Canny - Optimal edges
- Sobel - Gradient edges

### Enhance (2)
- Contrast - CLAHE algorithm
- Sharpen - Detail enhancement

### Transform (4)
- Rotate - Any angle
- Crop - Interactive select
- Flip H - Mirror left-right
- Flip V - Mirror top-bottom

### Adjust (2)
- Brightness - Slider (-100 to +100)
- Saturation - Slider (0% to 200%)

### Effects (5)
- Grayscale - B&W conversion
- Sepia - Vintage tone
- Emboss - 3D relief
- Cartoon - Artistic render
- FG-BG Separation - Subject isolation

## 💡 Tips

### Best Workflow
```
Open → Transform → Enhance → Adjust → Effects → Save
```

### Performance
- Work with medium images (1-3 MB)
- Undo history: 20 operations
- Restart if app becomes slow

### Quality Settings
- JPEG quality: 90-95 recommended
- PNG: Lossless compression
- BMP: No compression

## 📁 Files
```
main.py              # Run this
image_processor.py   # Backend
requirements.txt     # Dependencies
README.md           # Full docs
```

## 🔧 Build Executable
```powershell
.\build.ps1
# Output: .\dist\PhotoEditor.exe
```

## 🐛 Troubleshooting

**Image won't open?**
→ Check format (JPG, PNG, BMP only)

**Effect too strong?**
→ Undo (Ctrl+Z) and try lower values

**App is slow?**
→ Restart app, use smaller images

**Sliders don't work?**
→ Load an image first

## 📚 Documentation
- `README.md` - Overview
- `SETUP.md` - Installation
- `USER_GUIDE.md` - Detailed guide
- `PROJECT_SUMMARY.md` - Technical details

## 🎯 Common Workflows

### Portrait Enhancement
1. Enhance Contrast
2. Sharpen Image
3. Brightness: +15
4. Saturation: 115

### Artistic Photo
1. Cartoon Effect
2. Saturation: 130
3. Optional: Sepia Tone

### Document Scan
1. Enhance Contrast
2. Sharpen Image
3. Grayscale

---
**Version 1.0** | Built with Python + PyQt5 + OpenCV
