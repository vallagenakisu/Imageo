# Photo Editor - Architecture Documentation

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Photo Editor Application                     │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                          USER INTERFACE                          │
│                           (main.py)                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Menu Bar   │  │   Toolbar    │  │  Status Bar  │          │
│  │              │  │              │  │              │          │
│  │ File | Edit  │  │ Open | Save  │  │ Dimensions   │          │
│  │ Help         │  │ Undo | Redo  │  │ Status       │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                                                           │   │
│  │  Control Panel              Image Display Area           │   │
│  │  ┌──────────────┐          ┌──────────────────────┐    │   │
│  │  │ Blur Effects │          │                       │    │   │
│  │  │ - Gaussian   │          │   Current Image       │    │   │
│  │  │ - Average    │          │   (Scrollable)        │    │   │
│  │  │ - Median     │          │                       │    │   │
│  │  ├──────────────┤          └──────────────────────┘    │   │
│  │  │ Edge Detect  │                                       │   │
│  │  │ - Canny      │          Real-time Preview           │   │
│  │  │ - Sobel      │          of Current Image            │   │
│  │  ├──────────────┤                                       │   │
│  │  │ Enhancement  │                                       │   │
│  │  │ - Contrast   │                                       │   │
│  │  │ - Sharpen    │                                       │   │
│  │  ├──────────────┤                                       │   │
│  │  │ Transform    │                                       │   │
│  │  │ - Rotate     │                                       │   │
│  │  │ - Crop       │                                       │   │
│  │  │ - Flip H/V   │                                       │   │
│  │  ├──────────────┤                                       │   │
│  │  │ Adjustments  │                                       │   │
│  │  │ Brightness━━ │                                       │   │
│  │  │ Saturation━━ │                                       │   │
│  │  ├──────────────┤                                       │   │
│  │  │ Effects      │                                       │   │
│  │  │ - Grayscale  │                                       │   │
│  │  │ - Sepia      │                                       │   │
│  │  │ - Emboss     │                                       │   │
│  │  │ - Cartoon    │                                       │   │
│  │  │ - FG-BG Sep  │                                       │   │
│  │  └──────────────┘                                       │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                   │
└───────────────────────────────┬───────────────────────────────┘
                                │
                                │ Events / Signals
                                │
┌───────────────────────────────▼───────────────────────────────┐
│                     APPLICATION LOGIC                          │
│                   (PhotoEditorApp Class)                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────────┐  ┌─────────────────┐  ┌───────────────┐  │
│  │ File Operations │  │ History Manager │  │ UI Controllers│  │
│  │                 │  │                 │  │               │  │
│  │ - open_image()  │  │ - add_history() │  │ - display()   │  │
│  │ - save_image()  │  │ - undo()        │  │ - update_ui() │  │
│  │ - save_as()     │  │ - redo()        │  │ - show_msg()  │  │
│  └─────────────────┘  └─────────────────┘  └───────────────┘  │
│                                                                   │
└───────────────────────────────┬───────────────────────────────┘
                                │
                                │ Function Calls
                                │
┌───────────────────────────────▼───────────────────────────────┐
│                   IMAGE PROCESSING BACKEND                      │
│                  (image_processor.py)                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│                   ImageProcessor Class                           │
│                   (Static Methods)                               │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Blur Operations                                         │   │
│  │  - gaussian_blur()                                       │   │
│  │  - average_blur()                                        │   │
│  │  - median_blur()                                         │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Edge Detection                                          │   │
│  │  - canny_edge_detection()                                │   │
│  │  - sobel_edge_detection()                                │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Enhancement Operations                                  │   │
│  │  - enhance_contrast()                                    │   │
│  │  - sharpen_image()                                       │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Transform Operations                                    │   │
│  │  - rotate_image()                                        │   │
│  │  - crop_image()                                          │   │
│  │  - flip_image()                                          │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Adjustment Operations                                   │   │
│  │  - adjust_brightness()                                   │   │
│  │  - adjust_saturation()                                   │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Effect Operations                                       │   │
│  │  - convert_to_grayscale()                                │   │
│  │  - apply_sepia()                                         │   │
│  │  - emboss_effect()                                       │   │
│  │  - cartoonify()                                          │   │
│  │  - foreground_background_separation()                    │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                   │
└───────────────────────────────┬───────────────────────────────┘
                                │
                                │ Uses
                                │
┌───────────────────────────────▼───────────────────────────────┐
│                    EXTERNAL LIBRARIES                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │  OpenCV  │  │  NumPy   │  │  PyQt5   │  │  Pillow  │       │
│  │          │  │          │  │          │  │          │       │
│  │  Image   │  │  Array   │  │   GUI    │  │  Format  │       │
│  │  Process │  │  Ops     │  │  Widgets │  │  Support │       │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘       │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow

```
┌──────────┐
│   User   │
└────┬─────┘
     │ Interacts
     ▼
┌─────────────────┐
│  GUI Controls   │
│  (Buttons,      │
│   Sliders)      │
└────┬────────────┘
     │ Triggers Event
     ▼
┌─────────────────────┐
│  Event Handler      │
│  (button_clicked)   │
└────┬────────────────┘
     │ Calls Method
     ▼
┌─────────────────────┐        ┌──────────────────┐
│  App Logic          │───────▶│  Add to History  │
│  (apply_effect)     │        └──────────────────┘
└────┬────────────────┘
     │ Calls Processing
     ▼
┌─────────────────────┐
│  ImageProcessor     │
│  (static method)    │
└────┬────────────────┘
     │ Returns Result
     ▼
┌─────────────────────┐
│  Update Image       │
│  (display_image)    │
└────┬────────────────┘
     │ Shows Result
     ▼
┌─────────────────────┐
│  User sees change   │
└─────────────────────┘
```

## Class Diagram

```
┌─────────────────────────────────────────┐
│         PhotoEditorApp                  │
│         (QMainWindow)                   │
├─────────────────────────────────────────┤
│ - current_image: np.ndarray             │
│ - original_image: np.ndarray            │
│ - history: List[np.ndarray]             │
│ - history_index: int                    │
│ - processor: ImageProcessor             │
├─────────────────────────────────────────┤
│ + init_ui()                             │
│ + create_menu_bar()                     │
│ + create_toolbar()                      │
│ + create_control_panel()                │
│ + display_image()                       │
│ + add_to_history()                      │
│ + open_image()                          │
│ + save_image()                          │
│ + undo()                                │
│ + redo()                                │
│ + apply_gaussian_blur()                 │
│ + apply_canny_edge()                    │
│ + ... (all effect methods)              │
└─────────────────────────────────────────┘
              │
              │ uses
              ▼
┌─────────────────────────────────────────┐
│         ImageProcessor                  │
│         (Static Class)                  │
├─────────────────────────────────────────┤
│ @staticmethod                           │
│ + gaussian_blur()                       │
│ + average_blur()                        │
│ + canny_edge_detection()                │
│ + sobel_edge_detection()                │
│ + enhance_contrast()                    │
│ + rotate_image()                        │
│ + sharpen_image()                       │
│ + adjust_brightness()                   │
│ + adjust_saturation()                   │
│ + crop_image()                          │
│ + flip_image()                          │
│ + convert_to_grayscale()                │
│ + apply_sepia()                         │
│ + emboss_effect()                       │
│ + cartoonify()                          │
│ + foreground_background_separation()    │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│         CropDialog                      │
│         (QDialog)                       │
├─────────────────────────────────────────┤
│ - image: np.ndarray                     │
│ - crop_rect: QRect                      │
│ - start_point: QPoint                   │
│ - end_point: QPoint                     │
├─────────────────────────────────────────┤
│ + display_image()                       │
│ + mouse_press()                         │
│ + mouse_move()                          │
│ + mouse_release()                       │
│ + get_crop_rect()                       │
└─────────────────────────────────────────┘
```

## History Management

```
User makes changes:
┌───────────────────────────────────────┐
│  History Stack (Max 20)               │
├───────────────────────────────────────┤
│  Index 4: [Current Image]     ◄─────  │ Current
│  Index 3: [After Sharpen]             │
│  Index 2: [After Contrast]            │
│  Index 1: [After Blur]                │
│  Index 0: [Original Image]            │
└───────────────────────────────────────┘

After Undo:
┌───────────────────────────────────────┐
│  History Stack                        │
├───────────────────────────────────────┤
│  Index 4: [After Effect]              │
│  Index 3: [After Sharpen]     ◄─────  │ Current
│  Index 2: [After Contrast]            │
│  Index 1: [After Blur]                │
│  Index 0: [Original Image]            │
└───────────────────────────────────────┘

After Redo:
┌───────────────────────────────────────┐
│  History Stack                        │
├───────────────────────────────────────┤
│  Index 4: [After Effect]      ◄─────  │ Current
│  Index 3: [After Sharpen]             │
│  Index 2: [After Contrast]            │
│  Index 1: [After Blur]                │
│  Index 0: [Original Image]            │
└───────────────────────────────────────┘

New operation after undo:
┌───────────────────────────────────────┐
│  History Stack (Forward cleared)      │
├───────────────────────────────────────┤
│  Index 4: [New Operation]     ◄─────  │ Current
│  Index 3: [After Sharpen]             │
│  Index 2: [After Contrast]            │
│  Index 1: [After Blur]                │
│  Index 0: [Original Image]            │
└───────────────────────────────────────┘
```

## Image Processing Pipeline

```
┌──────────────────┐
│  Load Image      │
│  (BGR format)    │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  Store Original  │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  Apply Operation │
│  (OpenCV)        │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  Convert to RGB  │
│  (for display)   │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  QImage/QPixmap  │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  Display in GUI  │
└──────────────────┘
```

## Module Dependencies

```
main.py
  ├─→ PyQt5.QtWidgets (GUI components)
  ├─→ PyQt5.QtCore (Core functionality)
  ├─→ PyQt5.QtGui (Graphics)
  ├─→ cv2 (Image I/O)
  ├─→ numpy (Array operations)
  └─→ image_processor (Backend logic)

image_processor.py
  ├─→ cv2 (All image operations)
  ├─→ numpy (Array manipulation)
  └─→ typing (Type hints)
```

## Error Handling Flow

```
┌──────────────────┐
│  User Action     │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  Check Image     │
│  Loaded?         │
└───┬─────────┬────┘
    │ No      │ Yes
    ▼         ▼
┌─────────┐ ┌──────────────────┐
│ Warning │ │  Execute         │
│ Message │ │  Operation       │
└─────────┘ └───┬──────────────┘
                 │
                 ▼
          ┌──────────────────┐
          │  Success?        │
          └───┬─────────┬────┘
              │ Yes     │ No
              ▼         ▼
        ┌─────────┐ ┌─────────┐
        │ Update  │ │ Error   │
        │ Display │ │ Dialog  │
        └─────────┘ └─────────┘
```

## Performance Considerations

```
Memory Management:
┌────────────────────────────────────┐
│  Current Image:     ~10-50 MB      │
│  Original Image:    ~10-50 MB      │
│  History (20):      ~200-1000 MB   │
│  UI Components:     ~100 MB        │
│  ─────────────────────────────     │
│  Total:             ~320-1200 MB   │
└────────────────────────────────────┘

Processing Speed:
┌────────────────────────────────────┐
│  Fast (<100ms):                    │
│  - Blur, Flip, Brightness          │
│                                    │
│  Medium (100-500ms):               │
│  - Edge Detection, Contrast        │
│                                    │
│  Slow (1-3s):                      │
│  - Cartoon, FG-BG Separation       │
└────────────────────────────────────┘
```

---

This architecture provides a clean separation of concerns, making the application maintainable, extensible, and easy to understand.
