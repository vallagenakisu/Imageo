
# Enable High DPI support for responsive UI across different monitors
import os
os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
os.environ["QT_SCALE_FACTOR_ROUNDING_POLICY"] = "PassThrough"

import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QSlider, QFileDialog,
                             QAction, QMenuBar, QMenu, QToolBar, QStatusBar,
                             QMessageBox, QDialog, QSpinBox, QDialogButtonBox,
                             QGroupBox, QScrollArea, QComboBox, QInputDialog,
                             QProgressDialog, QGridLayout, QCheckBox, QSplitter, 
                             QToolButton, QLineEdit, QTextEdit)
from PyQt5.QtCore import Qt, QRect, QPoint, QTimer
from PyQt5.QtGui import QImage, QPixmap, QPainter, QPen, QIcon, QDoubleValidator, QFont
from typing import List, Optional
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from image_processor import ImageProcessor

# Set High DPI attributes before creating QApplication
QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)


class CustomKernelDialog(QDialog):
    """Interactive grid-based custom kernel dialog with animated convolution visualization"""
    
    def __init__(self, image: np.ndarray, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Custom Kernel Convolution - Animated Pixel-by-Pixel Visualization")
        self.setMinimumWidth(1200)
        self.setMinimumHeight(750)
        
        # Downscale image for animation if too large (for performance)
        max_size = 300
        h, w = image.shape[:2]
        if h > max_size or w > max_size:
            scale = min(max_size / h, max_size / w)
            new_h, new_w = int(h * scale), int(w * scale)
            self.animation_image = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)
        else:
            self.animation_image = image.copy()
        
        self.original_image = image.copy()
        self.current_image = image.copy()
        self.result_image = np.zeros_like(self.animation_image)
        self.processor = ImageProcessor()
        self.kernel_inputs = []
        
        # Animation state
        self.is_animating = False
        self.is_paused = False
        self.animation_completed = False  # Track if animation finished successfully
        self.current_row = 0
        self.current_col = 0
        self.animation_speed = 1  # milliseconds delay
        self.update_counter = 0
        self.update_interval = 100  # Update display every N pixels
        
        # Timer for animation
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.animate_convolution_step)
        
        self.init_ui()
        
    def init_ui(self):
        layout = QHBoxLayout()
        
        # Left panel - Controls (with scroll area)
        left_panel = QWidget()
        left_panel.setMaximumWidth(400)
        left_panel.setMinimumWidth(370)
        
        left_scroll = QScrollArea()
        left_scroll.setWidgetResizable(True)
        left_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        left_scroll.setStyleSheet("QScrollArea { border: none; }")
        
        left_content = QWidget()
        left_layout = QVBoxLayout()
        left_layout.setSpacing(10)
        
        # Title and instructions
        title = QLabel("🎓 Animated Convolution Visualizer")
        title.setStyleSheet("font-size: 14pt; font-weight: bold; color: #4ec9b0;")
        left_layout.addWidget(title)
        
        instructions = QLabel(
            "🎬 Watch convolution operation pixel-by-pixel!\n\n"
            "1. Enter kernel values or load a preset\n"
            "2. Click 'Start Animation' to see the magic\n"
            "3. Use Pause/Resume to control playback\n"
            "4. Adjust speed slider for faster/slower\n\n"
            "💡 The red box shows current kernel position.\n"
            "Watch how each pixel is computed!"
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("background-color: #2d2d30; padding: 0.8em; border-radius: 0.4em; color: #cccccc; font-size: 9pt;")
        left_layout.addWidget(instructions)
        
        # Kernel size selector
        size_layout = QHBoxLayout()
        size_layout.addWidget(QLabel("Kernel Size:"))
        self.size_combo = QComboBox()
        self.size_combo.addItems(["3x3", "5x5", "7x7"])
        self.size_combo.currentTextChanged.connect(self.change_kernel_size)
        size_layout.addWidget(self.size_combo)
        left_layout.addLayout(size_layout)
        
        # Animation controls
        animation_group = QGroupBox("Animation Controls")
        animation_layout = QVBoxLayout()
        
        # Start/Stop/Pause buttons
        btn_layout = QHBoxLayout()
        self.start_btn = QPushButton("▶ Start Animation")
        self.start_btn.clicked.connect(self.start_animation)
        btn_layout.addWidget(self.start_btn)
        
        self.pause_btn = QPushButton("⏸ Pause")
        self.pause_btn.clicked.connect(self.pause_animation)
        self.pause_btn.setEnabled(False)
        btn_layout.addWidget(self.pause_btn)
        
        self.stop_btn = QPushButton("⏹ Stop")
        self.stop_btn.clicked.connect(self.stop_animation)
        self.stop_btn.setEnabled(False)
        btn_layout.addWidget(self.stop_btn)
        animation_layout.addLayout(btn_layout)
        
        # Speed control
        speed_layout = QVBoxLayout()
        speed_label = QLabel("Animation Speed:")
        speed_layout.addWidget(speed_label)
        
        # Speed input box for precise control
        speed_input_layout = QHBoxLayout()
        self.speed_spinbox = QSpinBox()
        self.speed_spinbox.setMinimum(0)
        self.speed_spinbox.setMaximum(10)
        self.speed_spinbox.setValue(1)
        self.speed_spinbox.setSuffix(" ms")
        self.speed_spinbox.valueChanged.connect(self.update_speed_from_spinbox)
        speed_input_layout.addWidget(QLabel("Delay:"))
        speed_input_layout.addWidget(self.speed_spinbox)
        speed_layout.addLayout(speed_input_layout)
        
        # Preset speed buttons
        preset_speed_layout = QHBoxLayout()
        speed_0_001_btn = QPushButton("0.001 ms\n(Ultra Fast)")
        speed_0_001_btn.clicked.connect(lambda: self.speed_spinbox.setValue(0))
        speed_0_001_btn.setStyleSheet("font-size: 9px; padding: 4px;")
        preset_speed_layout.addWidget(speed_0_001_btn)
        
        speed_1_btn = QPushButton("1 ms\n(Fast)")
        speed_1_btn.clicked.connect(lambda: self.speed_spinbox.setValue(1))
        speed_1_btn.setStyleSheet("font-size: 9px; padding: 4px;")
        preset_speed_layout.addWidget(speed_1_btn)
        
        speed_5_btn = QPushButton("5 ms\n(Medium)")
        speed_5_btn.clicked.connect(lambda: self.speed_spinbox.setValue(5))
        speed_5_btn.setStyleSheet("font-size: 9px; padding: 4px;")
        preset_speed_layout.addWidget(speed_5_btn)
        
        speed_10_btn = QPushButton("10 ms\n(Slow)")
        speed_10_btn.clicked.connect(lambda: self.speed_spinbox.setValue(10))
        speed_10_btn.setStyleSheet("font-size: 9px; padding: 4px;")
        preset_speed_layout.addWidget(speed_10_btn)
        
        speed_layout.addLayout(preset_speed_layout)
        animation_layout.addLayout(speed_layout)
        
        # Progress label
        self.progress_label = QLabel("Progress: 0%")
        self.progress_label.setAlignment(Qt.AlignCenter)
        self.progress_label.setStyleSheet("font-size: 14px; color: #ffffff; background-color: #094771; padding: 8px; border-radius: 4px;")
        animation_layout.addWidget(self.progress_label)
        
        animation_group.setLayout(animation_layout)
        left_layout.addWidget(animation_group)
        
        # Preset kernels - wrapped in scroll area
        preset_group = QGroupBox("Preset Kernels")
        preset_scroll = QScrollArea()
        preset_scroll.setWidgetResizable(True)
        preset_scroll.setMaximumHeight(250)
        preset_scroll.setStyleSheet("QScrollArea { border: none; }")
        
        preset_widget = QWidget()
        preset_layout = QVBoxLayout()
        preset_layout.setSpacing(4)
        
        presets = [
            ("Box Blur 3x3", [[1/9,1/9,1/9], [1/9,1/9,1/9], [1/9,1/9,1/9]]),
            ("Edge Detection (Laplacian)", [[-1,-1,-1], [-1,8,-1], [-1,-1,-1]]),
            ("Sharpen", [[0,-1,0], [-1,5,-1], [0,-1,0]]),
            ("Sharpen Strong", [[-1,-1,-1], [-1,9,-1], [-1,-1,-1]]),
            ("Emboss", [[-2,-1,0], [-1,1,1], [0,1,2]]),
            ("Emboss Diagonal", [[0,1,1], [-1,0,1], [-1,-1,0]]),
            ("Edge Detection (Sobel X)", [[-1,0,1], [-2,0,2], [-1,0,1]]),
            ("Edge Detection (Sobel Y)", [[-1,-2,-1], [0,0,0], [1,2,1]]),
            ("Outline", [[-1,-1,-1], [-1,8,-1], [-1,-1,-1]]),
            ("Gaussian Blur 3x3", [[1/16,2/16,1/16], [2/16,4/16,2/16], [1/16,2/16,1/16]]),
            ("Identity", [[0,0,0], [0,1,0], [0,0,0]]),
            ("Ridge Detection", [[0,-1,0], [-1,4,-1], [0,-1,0]]),
            ("Unsharp Masking", [[1,4,6,4,1], [4,16,24,16,4], [6,24,-476,24,6], [4,16,24,16,4], [1,4,6,4,1]]),
            ("Motion Blur Horizontal", [[0,0,0,0,0], [0,0,0,0,0], [1/5,1/5,1/5,1/5,1/5], [0,0,0,0,0], [0,0,0,0,0]]),
            ("Motion Blur Diagonal", [[1/5,0,0,0,0], [0,1/5,0,0,0], [0,0,1/5,0,0], [0,0,0,1/5,0], [0,0,0,0,1/5]]),
        ]
        
        for preset_name, kernel_values in presets:
            btn = QPushButton(preset_name)
            btn.setStyleSheet("font-size: 9px; padding: 6px 4px; text-align: left;")
            btn.clicked.connect(lambda checked, k=kernel_values: self.load_preset(k))
            preset_layout.addWidget(btn)
        
        preset_widget.setLayout(preset_layout)
        preset_scroll.setWidget(preset_widget)
        
        preset_group_layout = QVBoxLayout()
        preset_group_layout.addWidget(preset_scroll)
        preset_group.setLayout(preset_group_layout)
        left_layout.addWidget(preset_group)
        
        # Clear and Reset buttons
        btn_layout2 = QHBoxLayout()
        clear_btn = QPushButton("Clear Grid")
        clear_btn.clicked.connect(self.clear_grid)
        btn_layout2.addWidget(clear_btn)
        
        reset_btn = QPushButton("Reset Image")
        reset_btn.clicked.connect(self.reset_image)
        btn_layout2.addWidget(reset_btn)
        left_layout.addLayout(btn_layout2)
        
        left_layout.addStretch()
        left_content.setLayout(left_layout)
        left_scroll.setWidget(left_content)
        
        # Wrap scroll in panel layout
        left_panel_layout = QVBoxLayout()
        left_panel_layout.setContentsMargins(0, 0, 0, 0)
        left_panel_layout.addWidget(left_scroll)
        left_panel.setLayout(left_panel_layout)
        
        # Center panel - Kernel Grid
        center_panel = QWidget()
        center_layout = QVBoxLayout()
        
        grid_title = QLabel("Kernel Matrix")
        grid_title.setStyleSheet("font-size: 12pt; font-weight: bold; color: #4ec9b0;")
        grid_title.setAlignment(Qt.AlignCenter)
        center_layout.addWidget(grid_title)
        
        # Kernel grid container
        self.grid_container = QWidget()
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(4)
        self.grid_container.setLayout(self.grid_layout)
        center_layout.addWidget(self.grid_container)
        
        center_layout.addStretch()
        center_panel.setLayout(center_layout)
        
        # Right panel - Image Preview with overlay
        right_panel = QWidget()
        right_layout = QVBoxLayout()
        
        preview_title = QLabel("Convolution Animation")
        preview_title.setStyleSheet("font-size: 12pt; font-weight: bold; color: #4ec9b0;")
        preview_title.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(preview_title)
        
        # Canvas for drawing image with kernel overlay
        self.canvas_label = QLabel()
        self.canvas_label.setAlignment(Qt.AlignCenter)
        self.canvas_label.setMinimumSize(500, 500)
        self.canvas_label.setStyleSheet("border: 2px solid #3e3e42; background-color: #1e1e1e; border-radius: 6px;")
        right_layout.addWidget(self.canvas_label)
        
        right_panel.setLayout(right_layout)
        
        # Add panels to main layout
        layout.addWidget(left_panel, 1)
        layout.addWidget(center_panel, 1)
        layout.addWidget(right_panel, 2)
        
        # Dialog buttons
        main_layout = QVBoxLayout()
        main_layout.addLayout(layout)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        main_layout.addWidget(buttons)
        
        self.setLayout(main_layout)
        
        # Initialize with 3x3 grid
        self.change_kernel_size("3x3")
        self.update_canvas()
    
    def create_kernel_grid(self, size):
        """Create an interactive grid of input boxes for kernel values"""
        # Clear existing grid
        for i in reversed(range(self.grid_layout.count())): 
            self.grid_layout.itemAt(i).widget().setParent(None)
        
        self.kernel_inputs = []
        
        for row in range(size):
            row_inputs = []
            for col in range(size):
                input_box = QLineEdit()
                input_box.setText("0")
                input_box.setAlignment(Qt.AlignCenter)
                # Adjust size based on kernel size for better display
                box_size = 70 if size <= 7 else (50 if size <= 11 else 35)
                input_box.setFixedSize(box_size, box_size)
                # Adjust font size based on kernel size
                font_size = 16 if size <= 7 else (12 if size <= 11 else 10)
                input_box.setStyleSheet(f"""
                    QLineEdit {{
                        background-color: #3e3e42;
                        color: #ffffff;
                        border: 2px solid #555555;
                        border-radius: 6px;
                        font-size: {font_size}px;
                        font-weight: bold;
                        padding: 2px;
                    }}
                    QLineEdit:focus {{
                        border: 2px solid #007acc;
                        background-color: #2d2d30;
                    }}
                """)
                
                # Validate input
                validator = QDoubleValidator()
                validator.setNotation(QDoubleValidator.StandardNotation)
                input_box.setValidator(validator)
                
                self.grid_layout.addWidget(input_box, row, col)
                row_inputs.append(input_box)
            
            self.kernel_inputs.append(row_inputs)
    
    def change_kernel_size(self, size_text):
        """Change the kernel grid size"""
        size = int(size_text[0])
        self.create_kernel_grid(size)
    
    def load_preset(self, kernel_values):
        """Load a preset kernel into the grid"""
        size = len(kernel_values)
        size_text = f"{size}x{size}"
        if self.size_combo.currentText() != size_text:
            self.size_combo.setCurrentText(size_text)
        
        for row in range(size):
            for col in range(size):
                self.kernel_inputs[row][col].setText(str(kernel_values[row][col]))
    
    def clear_grid(self):
        """Clear all grid values to 0"""
        for row in self.kernel_inputs:
            for input_box in row:
                input_box.setText("0")
    
    def update_speed_from_spinbox(self, value):
        """Update animation speed from spinbox"""
        if value == 0:
            # 0.001 ms (essentially no delay, but still yields to UI)
            self.animation_speed = 0
        else:
            self.animation_speed = value
    
    def start_animation(self):
        """Start the convolution animation"""
        try:
            kernel = self.get_kernel()
            
            if np.all(kernel == 0):
                QMessageBox.warning(self, "Invalid Kernel", "Kernel is all zeros!")
                return
            
            # Create downscaled preview for animation (200x200 for performance)
            preview_size = (200, 200)
            self.preview_image = cv2.resize(self.animation_image, preview_size, interpolation=cv2.INTER_AREA)
            
            # Reset state
            self.is_animating = True
            self.is_paused = False
            self.animation_completed = False  # Reset completion flag
            self.current_row = 0
            self.current_col = 0
            self.update_counter = 0
            self.result_image = np.zeros_like(self.preview_image)  # Match preview size
            
            # Calculate optimal update interval based on preview size
            h, w = self.preview_image.shape[:2]
            total_pixels = h * w
            # Update display 200-500 times during animation for smooth progress
            self.update_interval = max(1, total_pixels // 300)
            
            # Update UI
            self.start_btn.setEnabled(False)
            self.pause_btn.setEnabled(True)
            self.stop_btn.setEnabled(True)
            self.size_combo.setEnabled(False)
            
            # Start timer (use 1ms minimum for timer, actual speed controlled by processEvents)
            timer_interval = max(1, self.animation_speed) if self.animation_speed > 0 else 1
            self.animation_timer.start(timer_interval)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to start animation: {str(e)}")
    
    def pause_animation(self):
        """Pause/Resume animation"""
        if self.is_paused:
            self.is_paused = False
            self.pause_btn.setText("⏸ Pause")
            timer_interval = max(1, self.animation_speed) if self.animation_speed > 0 else 1
            self.animation_timer.start(timer_interval)
        else:
            self.is_paused = True
            self.pause_btn.setText("▶ Resume")
            self.animation_timer.stop()
    
    def stop_animation(self):
        """Stop the animation"""
        self.is_animating = False
        self.is_paused = False
        self.animation_timer.stop()
        
        # Update UI
        self.start_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)
        self.stop_btn.setEnabled(False)
        self.size_combo.setEnabled(True)
        self.pause_btn.setText("⏸ Pause")
        
        # Show final result
        self.current_image = self.result_image.copy()
        self.update_canvas()
    
    def animate_convolution_step(self):
        """Perform one step of convolution animation - OPTIMIZED"""
        if not self.is_animating or self.is_paused:
            return
        
        kernel = self.get_kernel()
        kernel_size = kernel.shape[0]
        half_kernel = kernel_size // 2
        
        # Use preview_image dimensions for animation
        h, w = self.preview_image.shape[:2]
        
        # Process multiple pixels per frame for better performance
        pixels_per_frame = max(1, int(10 / max(1, self.animation_speed))) if self.animation_speed > 0 else 50
        
        for _ in range(pixels_per_frame):
            if self.current_row >= h:
                break
                
            # Apply convolution at current position
            if self.current_col < w:
                # Get the region around current pixel from preview_image
                row_start = max(0, self.current_row - half_kernel)
                row_end = min(h, self.current_row + half_kernel + 1)
                col_start = max(0, self.current_col - half_kernel)
                col_end = min(w, self.current_col + half_kernel + 1)
                
                # Extract region from preview_image
                region = self.preview_image[row_start:row_end, col_start:col_end].astype(np.float32)
                
                # Adjust kernel if at edges
                k_row_start = half_kernel - (self.current_row - row_start)
                k_row_end = half_kernel + (row_end - self.current_row)
                k_col_start = half_kernel - (self.current_col - col_start)
                k_col_end = half_kernel + (col_end - self.current_col)
                
                kernel_slice = kernel[k_row_start:k_row_end, k_col_start:k_col_end]
                
                # Apply convolution for each channel
                for c in range(3):
                    result = np.sum(region[:, :, c] * kernel_slice)
                    self.result_image[self.current_row, self.current_col, c] = np.clip(result, 0, 255)
                
                # Move to next pixel
                self.current_col += 1
                self.update_counter += 1
            
            if self.current_col >= w:
                self.current_col = 0
                self.current_row += 1
        
        # Only update canvas at intervals (not every pixel!)
        if self.update_counter >= self.update_interval or self.current_row >= h:
            self.update_canvas()
            self.update_counter = 0
            
            # Calculate progress
            total_pixels = h * w
            current_pixel = min(self.current_row * w + self.current_col, total_pixels)
            progress = int((current_pixel / total_pixels) * 100)
            self.progress_label.setText(f"Progress: {progress}% ({current_pixel}/{total_pixels} pixels)")
            
            # Process events to keep UI responsive
            QApplication.processEvents()
        
        # Check if done
        if self.current_row >= h:
            self.stop_animation()
            self.progress_label.setText("Progress: 100% - Complete!")
            
            # Mark animation as completed
            self.animation_completed = True
            
            # Apply to full-size image if we downscaled
            if self.animation_image.shape != self.original_image.shape:
                self.current_image = self.processor.apply_custom_kernel(self.original_image, kernel)
            else:
                self.current_image = self.result_image.copy()
            
            # Update canvas to show the final result
            self.update_canvas()
            
            # Show completion message
            QMessageBox.information(self, "Complete", 
                "Convolution animation completed!\nThe result is now displayed in the preview.")
    
    def reset_image(self):
        """Reset to original image"""
        # Stop any ongoing animation
        if self.is_animating:
            self.stop_animation()
        
        # Reset animation flags
        self.is_animating = False
        self.is_paused = False
        self.animation_completed = False
        
        # Reinitialize preview if we're using it
        if hasattr(self, 'preview_image') and self.preview_image is not None:
            preview_size = (200, 200)
            self.preview_image = cv2.resize(self.animation_image, preview_size, interpolation=cv2.INTER_AREA)
            self.result_image = np.zeros_like(self.preview_image)
        else:
            self.result_image = np.zeros_like(self.animation_image)
        
        self.current_image = self.original_image.copy()
        self.current_row = 0
        self.current_col = 0
        self.update_counter = 0
        self.progress_label.setText("Progress: 0%")
        self.update_canvas()
    
    def update_canvas(self):
        """Update the canvas with current image and kernel overlay - OPTIMIZED"""
        # Use preview_image for display during animation
        if self.is_animating:
            display_img = self.result_image.copy()
            
            # Create a mask for processed pixels (MUCH faster than nested loops!)
            h, w = display_img.shape[:2]
            mask = np.zeros((h, w), dtype=bool)
            
            # Mark processed pixels as True
            if self.current_row > 0:
                mask[:self.current_row, :] = True
            if self.current_col > 0:
                mask[self.current_row, :self.current_col] = True
            
            # Dim unprocessed pixels using vectorized operation on preview_image
            display_img[~mask] = (self.preview_image[~mask] * 0.5).astype(np.uint8)
        elif self.animation_completed:
            # Show the result after animation completes
            if hasattr(self, 'result_image') and self.result_image is not None and self.result_image.size > 0:
                display_img = self.result_image.copy()
            else:
                display_img = self.current_image.copy()
        else:
            # Show original animation image before animation starts
            display_img = self.animation_image.copy()
        
        # If animating, overlay processed and unprocessed regions
        
        # Convert to RGB for display
        display_img_rgb = cv2.cvtColor(display_img, cv2.COLOR_BGR2RGB)
        
        # Draw kernel position overlay (only if animating and not too small)
        if self.is_animating and display_img.shape[0] > 50:
            kernel_size = len(self.kernel_inputs)
            half_kernel = kernel_size // 2
            
            # Draw red rectangle around current kernel position
            row_start = max(0, self.current_row - half_kernel)
            row_end = min(display_img.shape[0], self.current_row + half_kernel + 1)
            col_start = max(0, self.current_col - half_kernel)
            col_end = min(display_img.shape[1], self.current_col + half_kernel + 1)
            
            # Draw rectangle (directly on display_img_rgb, no copy needed)
            cv2.rectangle(display_img_rgb, (col_start, row_start), (col_end, row_end), (255, 0, 0), 2)
            # Draw center pixel
            if self.current_row < display_img.shape[0] and self.current_col < display_img.shape[1]:
                cv2.circle(display_img_rgb, (self.current_col, self.current_row), 2, (0, 255, 0), -1)
        
        # Convert to QPixmap
        h, w, ch = display_img_rgb.shape
        bytes_per_line = ch * w
        q_image = QImage(display_img_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_image)
        
        # Scale to fit
        scaled_pixmap = pixmap.scaled(500, 500, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.canvas_label.setPixmap(scaled_pixmap)
    
    def get_kernel(self):
        """Get the kernel matrix from the grid inputs"""
        size = len(self.kernel_inputs)
        kernel = np.zeros((size, size), dtype=np.float32)
        
        for row in range(size):
            for col in range(size):
                text = self.kernel_inputs[row][col].text()
                try:
                    kernel[row, col] = float(text) if text else 0
                except ValueError:
                    kernel[row, col] = 0
        
        return kernel
    
    def get_result_image(self):
        """Get the result image after animation completes"""
        if self.animation_completed:
            return self.current_image
        return None
    
    def has_animation_result(self):
        """Check if animation completed successfully"""
        return self.animation_completed


class CannyIntermediatesDialog(QDialog):
    """Dialog to display Canny edge detection intermediate steps in a grid"""
    
    def __init__(self, intermediates: dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Canny Edge Detection - Intermediate Steps")
        self.setMinimumSize(1400, 900)
        
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("🔍 Canny Edge Detection - Step-by-Step Visualization")
        title.setStyleSheet("font-size: 14pt; font-weight: bold; color: #4ec9b0; padding: 0.6em;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Create scroll area for grid
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background-color: #1e1e1e;")
        
        container = QWidget()
        grid_layout = QGridLayout()
        grid_layout.setSpacing(15)
        
        # Display each intermediate step in a grid (2 columns x 3 rows)
        step_names = {
            '1_grayscale': '1. Grayscale',
            '2_blurred': '2. Gaussian Blur',
            '3_gradient_magnitude': '3. Gradient Magnitude',
            '4_non_maximum_suppression': '4. Non-Max Suppression',
            '5_double_threshold': '5. Double Threshold',
            '6_final_edges': '6. Final Edges'
        }
        
        step_descriptions = {
            '1_grayscale': 'Convert to grayscale',
            '2_blurred': 'Reduce noise with Gaussian filter',
            '3_gradient_magnitude': 'Detect intensity gradients',
            '4_non_maximum_suppression': 'Thin edges to single pixels',
            '5_double_threshold': 'Classify edges (strong/weak)',
            '6_final_edges': 'Connect edges via hysteresis'
        }
        
        # Arrange in 2x3 grid
        row, col = 0, 0
        for key in sorted(intermediates.keys()):
            # Create frame for each step
            frame = QWidget()
            frame.setStyleSheet("background-color: #2d2d30; border-radius: 8px; padding: 10px;")
            frame_layout = QVBoxLayout()
            
            # Step title
            title = QLabel(f"<b style='color: #4ec9b0;'>{step_names.get(key, key)}</b>")
            title.setAlignment(Qt.AlignCenter)
            title.setStyleSheet("font-size: 11pt; padding: 0.3em;")
            frame_layout.addWidget(title)
            
            # Description
            desc = QLabel(step_descriptions.get(key, ''))
            desc.setAlignment(Qt.AlignCenter)
            desc.setStyleSheet("color: #cccccc; font-size: 9pt; padding-bottom: 0.5em;")
            desc.setWordWrap(True)
            frame_layout.addWidget(desc)
            
            # Image
            img_label = QLabel()
            img_label.setAlignment(Qt.AlignCenter)
            img = intermediates[key]
            
            # Convert to QPixmap
            display_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            height, width, channel = display_img.shape
            bytes_per_line = 3 * width
            q_image = QImage(display_img.data, width, height, bytes_per_line, 
                           QImage.Format_RGB888)
            
            # Scale image to fit in grid cell (fixed size for uniformity)
            pixmap = QPixmap.fromImage(q_image)
            pixmap = pixmap.scaled(550, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            
            img_label.setPixmap(pixmap)
            img_label.setStyleSheet("border: 2px solid #3e3e42; background-color: #1e1e1e; padding: 5px;")
            frame_layout.addWidget(img_label)
            
            frame.setLayout(frame_layout)
            
            # Add to grid (2 columns)
            grid_layout.addWidget(frame, row, col)
            col += 1
            if col >= 2:
                col = 0
                row += 1
        
        container.setLayout(grid_layout)
        scroll.setWidget(container)
        layout.addWidget(scroll)
        
        # Close button
        close_btn = QPushButton("✓ Close")
        close_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #0e639c, stop:1 #1177bb);
                color: white;
                border: none;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 6px;
                min-height: 42px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1177bb, stop:1 #1e88cc);
            }
        """)
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)


class BlurDialog(QDialog):
    """Unified dialog for all blur operations with live preview"""
    
    def __init__(self, image: np.ndarray, processor: ImageProcessor, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Blur Effects - Live Preview")
        self.setMinimumSize(1000, 700)
        
        self.original_image = image.copy()
        self.current_image = image.copy()
        self.processor = processor
        
        # Main layout
        main_layout = QHBoxLayout()
        
        # Left panel - Controls
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        
        # Title
        title = QLabel("🎨 Blur Effects")
        title.setStyleSheet("font-size: 12pt; font-weight: bold; color: #4ec9b0;")
        left_layout.addWidget(title)
        
        # Blur type selector
        type_label = QLabel("Blur Type:")
        left_layout.addWidget(type_label)
        
        self.blur_type_combo = QComboBox()
        self.blur_type_combo.addItems(["Gaussian Blur", "Average Blur", "Median Blur"])
        self.blur_type_combo.currentTextChanged.connect(self.on_blur_type_changed)
        left_layout.addWidget(self.blur_type_combo)
        
        # Intensity slider
        intensity_label = QLabel("Blur Intensity (Kernel Size):")
        left_layout.addWidget(intensity_label)
        
        self.intensity_slider = QSlider(Qt.Horizontal)
        self.intensity_slider.setMinimum(1)
        self.intensity_slider.setMaximum(25)
        self.intensity_slider.setValue(5)
        self.intensity_slider.setTickPosition(QSlider.TicksBelow)
        self.intensity_slider.setTickInterval(2)
        self.intensity_slider.valueChanged.connect(self.update_preview)
        left_layout.addWidget(self.intensity_slider)
        
        self.intensity_value_label = QLabel("Kernel Size: 5")
        self.intensity_value_label.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(self.intensity_value_label)
        
        # Sigma slider for Gaussian blur (initially visible)
        self.sigma_widget = QWidget()
        sigma_layout = QVBoxLayout()
        sigma_label = QLabel("Sigma (Standard Deviation):")
        sigma_layout.addWidget(sigma_label)
        
        self.sigma_slider = QSlider(Qt.Horizontal)
        self.sigma_slider.setMinimum(0)
        self.sigma_slider.setMaximum(100)
        self.sigma_slider.setValue(0)  # 0 means auto
        self.sigma_slider.setTickPosition(QSlider.TicksBelow)
        self.sigma_slider.setTickInterval(10)
        self.sigma_slider.valueChanged.connect(self.update_preview)
        sigma_layout.addWidget(self.sigma_slider)
        
        self.sigma_label = QLabel("Sigma: Auto")
        self.sigma_label.setAlignment(Qt.AlignCenter)
        sigma_layout.addWidget(self.sigma_label)
        
        self.sigma_widget.setLayout(sigma_layout)
        left_layout.addWidget(self.sigma_widget)
        
        # Reset button
        reset_btn = QPushButton("Reset to Original")
        reset_btn.clicked.connect(self.reset_preview)
        left_layout.addWidget(reset_btn)
        
        left_layout.addStretch()
        
        # Info label
        info_label = QLabel(
            "💡 Tips:\n"
            "• Adjust slider for live preview\n"
            "• Higher values = more blur\n"
            "• Gaussian: smooth, natural\n"
            "• Average: simple, fast\n"
            "• Median: removes noise"
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("background-color: #2d2d30; padding: 0.8em; border-radius: 0.4em;")
        left_layout.addWidget(info_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        apply_btn = QPushButton("✓ Apply")
        apply_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("✗ Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(apply_btn)
        button_layout.addWidget(cancel_btn)
        left_layout.addLayout(button_layout)
        
        left_panel.setLayout(left_layout)
        left_panel.setMaximumWidth(300)
        
        # Right panel - Image preview
        right_panel = QWidget()
        right_layout = QVBoxLayout()
        
        preview_title = QLabel("Live Preview")
        preview_title.setStyleSheet("font-size: 11pt; font-weight: bold; color: #4ec9b0;")
        preview_title.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(preview_title)
        
        # Image display
        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setMinimumSize(600, 500)
        self.preview_label.setStyleSheet("border: 2px solid #3e3e42; background-color: #1e1e1e;")
        right_layout.addWidget(self.preview_label)
        
        right_panel.setLayout(right_layout)
        
        # Add panels to main layout
        main_layout.addWidget(left_panel)
        main_layout.addWidget(right_panel)
        
        self.setLayout(main_layout)
        
        # Initial preview
        self.update_preview()
    
    def on_blur_type_changed(self):
        """Handle blur type change"""
        blur_type = self.blur_type_combo.currentText()
        
        # Show/hide sigma slider based on blur type
        if blur_type == "Gaussian Blur":
            self.sigma_widget.setVisible(True)
        else:
            self.sigma_widget.setVisible(False)
        
        self.update_preview()
    
    def update_preview(self):
        """Update the live preview with current settings"""
        blur_type = self.blur_type_combo.currentText()
        kernel_size = self.intensity_slider.value()
        
        # Ensure odd kernel size for Gaussian and Median
        if blur_type in ["Gaussian Blur", "Median Blur"] and kernel_size % 2 == 0:
            kernel_size += 1
            self.intensity_slider.blockSignals(True)
            self.intensity_slider.setValue(kernel_size)
            self.intensity_slider.blockSignals(False)
        
        # Update intensity label
        self.intensity_value_label.setText(f"Kernel Size: {kernel_size}")
        
        # Update sigma label
        sigma_value = self.sigma_slider.value()
        if sigma_value == 0:
            self.sigma_label.setText("Sigma: Auto")
            sigma = None
        else:
            sigma = sigma_value / 10.0
            self.sigma_label.setText(f"Sigma: {sigma:.1f}")
        
        # Apply blur based on type
        try:
            if blur_type == "Gaussian Blur":
                self.current_image = self.processor.gaussian_blur(self.original_image, kernel_size, sigma)
            elif blur_type == "Average Blur":
                self.current_image = self.processor.average_blur(self.original_image, kernel_size)
            elif blur_type == "Median Blur":
                self.current_image = self.processor.median_blur(self.original_image, kernel_size)
            
            # Display the preview
            self.display_preview()
        except Exception as e:
            print(f"Preview error: {e}")
    
    def display_preview(self):
        """Display the current image in the preview label"""
        display_img = cv2.cvtColor(self.current_image, cv2.COLOR_BGR2RGB)
        height, width, channel = display_img.shape
        bytes_per_line = 3 * width
        q_image = QImage(display_img.data, width, height, bytes_per_line, QImage.Format_RGB888)
        
        pixmap = QPixmap.fromImage(q_image)
        scaled_pixmap = pixmap.scaled(600, 500, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.preview_label.setPixmap(scaled_pixmap)
    
    def reset_preview(self):
        """Reset to original image"""
        self.current_image = self.original_image.copy()
        self.intensity_slider.setValue(5)
        self.sigma_slider.setValue(0)
        self.display_preview()
    
    def get_result_image(self):
        """Return the processed image"""
        return self.current_image


class CannyEdgeDialog(QDialog):
    """Dialog for Canny edge detection with threshold sliders"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Canny Edge Detection")
        self.setMinimumSize(400, 300)
        
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Canny Edge Detection Settings")
        title.setStyleSheet("font-size: 9pt; font-weight: bold; color: #ffffff;")
        layout.addWidget(title)
        
        # Low threshold slider
        low_label = QLabel("Low Threshold:")
        low_label.setStyleSheet("font-size: 7pt; color: #cccccc; margin-top: 0.8em;")
        layout.addWidget(low_label)
        
        self.low_slider = QSlider(Qt.Horizontal)
        self.low_slider.setMinimum(0)
        self.low_slider.setMaximum(255)
        self.low_slider.setValue(50)
        self.low_slider.setTickPosition(QSlider.TicksBelow)
        self.low_slider.setTickInterval(25)
        self.low_slider.valueChanged.connect(self.update_labels)
        layout.addWidget(self.low_slider)
        
        self.low_value_label = QLabel("50")
        self.low_value_label.setStyleSheet("font-size: 7pt; color: #ffffff;")
        self.low_value_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.low_value_label)
        
        # High threshold slider
        high_label = QLabel("High Threshold:")
        high_label.setStyleSheet("font-size: 7pt; color: #cccccc; margin-top: 0.8em;")
        layout.addWidget(high_label)
        
        self.high_slider = QSlider(Qt.Horizontal)
        self.high_slider.setMinimum(0)
        self.high_slider.setMaximum(255)
        self.high_slider.setValue(150)
        self.high_slider.setTickPosition(QSlider.TicksBelow)
        self.high_slider.setTickInterval(25)
        self.high_slider.valueChanged.connect(self.update_labels)
        layout.addWidget(self.high_slider)
        
        self.high_value_label = QLabel("150")
        self.high_value_label.setStyleSheet("font-size: 7pt; color: #ffffff;")
        self.high_value_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.high_value_label)
        
        # Info label
        info_label = QLabel("• Low threshold detects weak edges\n• High threshold detects strong edges\n• Recommended ratio: 1:2 or 1:3")
        info_label.setStyleSheet("font-size: 6pt; color: #888888; margin-top: 1em; padding: 0.5em; background-color: #252526; border-radius: 2px;")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        layout.addStretch()
        
        # Buttons
        button_layout = QHBoxLayout()
        
        reset_btn = QPushButton("Reset")
        reset_btn.setStyleSheet("""
            QPushButton {
                font-size: 7pt;
                padding: 0.4em 0.8em;
                background-color: #3f3f46;
                color: #ffffff;
                border: none;
                border-radius: 2px;
            }
            QPushButton:hover {
                background-color: #4f4f56;
            }
        """)
        reset_btn.clicked.connect(self.reset_values)
        button_layout.addWidget(reset_btn)
        
        apply_btn = QPushButton("Apply")
        apply_btn.setStyleSheet("""
            QPushButton {
                font-size: 7pt;
                padding: 0.4em 0.8em;
                background-color: #007acc;
                color: #ffffff;
                border: none;
                border-radius: 2px;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
        """)
        apply_btn.clicked.connect(self.accept)
        button_layout.addWidget(apply_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet("""
            QPushButton {
                font-size: 7pt;
                padding: 0.4em 0.8em;
                background-color: #3f3f46;
                color: #ffffff;
                border: none;
                border-radius: 2px;
            }
            QPushButton:hover {
                background-color: #4f4f56;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def update_labels(self):
        """Update value labels"""
        self.low_value_label.setText(str(self.low_slider.value()))
        self.high_value_label.setText(str(self.high_slider.value()))
    
    def reset_values(self):
        """Reset to default values"""
        self.low_slider.setValue(50)
        self.high_slider.setValue(150)
    
    def get_thresholds(self):
        """Return the threshold values"""
        return self.low_slider.value(), self.high_slider.value()


class LaplacianEdgeDialog(QDialog):
    """Dialog for Laplacian edge detection parameters"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Laplacian Edge Detection Settings")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("Robust Laplacian Edge Detection (LoG + Zero Crossing)")
        title.setStyleSheet("font-size: 9pt; font-weight: bold; color: #ffffff;")
        layout.addWidget(title)
        
        # Description
        desc_label = QLabel("Uses LoG operator, zero-crossing detection, and adaptive variance thresholding")
        desc_label.setStyleSheet("font-size: 6pt; color: #888888; margin-bottom: 0.5em;")
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        # Threshold slider
        threshold_label = QLabel("Variance Threshold Multiplier:")
        threshold_label.setStyleSheet("font-size: 7pt; color: #cccccc; margin-top: 0.8em;")
        layout.addWidget(threshold_label)
        
        threshold_layout = QHBoxLayout()
        self.threshold_slider = QSlider(Qt.Horizontal)
        self.threshold_slider.setMinimum(0)
        self.threshold_slider.setMaximum(255)
        self.threshold_slider.setValue(50)
        self.threshold_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #3a3a3a;
                height: 6px;
                background: #2d2d30;
                margin: 0px;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #007acc, stop:1 #005a9e);
                border: 1px solid #005a9e;
                width: 14px;
                height: 14px;
                margin: -5px 0;
                border-radius: 7px;
            }
            QSlider::handle:horizontal:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #1e90ff, stop:1 #007acc);
            }
        """)
        self.threshold_slider.valueChanged.connect(self.update_labels)
        threshold_layout.addWidget(self.threshold_slider)
        
        self.threshold_value_label = QLabel("50 (≈100)")
        self.threshold_value_label.setStyleSheet("font-size: 7pt; color: #ffffff; min-width: 5em;")
        threshold_layout.addWidget(self.threshold_value_label)
        
        layout.addLayout(threshold_layout)
        
        # Help text for threshold
        threshold_help = QLabel("Higher values = more selective (only strong edges)")
        threshold_help.setStyleSheet("font-size: 6pt; color: #666666; font-style: italic;")
        layout.addWidget(threshold_help)
        
        # Kernel size dropdown (kept for UI consistency, not used in algorithm)
        kernel_label = QLabel("LoG Sigma (controls kernel size):")
        kernel_label.setStyleSheet("font-size: 7pt; color: #cccccc; margin-top: 0.8em;")
        layout.addWidget(kernel_label)
        
        kernel_help = QLabel("Automatically calculated as 9×sigma")
        kernel_help.setStyleSheet("font-size: 6pt; color: #666666; font-style: italic;")
        layout.addWidget(kernel_help)
        
        self.kernel_combo = QComboBox()
        self.kernel_combo.addItems(["1", "3", "5"])
        self.kernel_combo.setCurrentIndex(1)  # Default to 3
        self.kernel_combo.setStyleSheet("""
            QComboBox {
                background-color: #2d2d30;
                color: #ffffff;
                border: 1px solid #3a3a3a;
                padding: 0.4em;
                font-size: 7pt;
                border-radius: 3px;
            }
            QComboBox:hover {
                border: 1px solid #007acc;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox QAbstractItemView {
                background-color: #2d2d30;
                color: #ffffff;
                selection-background-color: #007acc;
                border: 1px solid #3a3a3a;
            }
        """)
        layout.addWidget(self.kernel_combo)
        
        # Blur kernel size slider (used as sigma multiplier)
        blur_label = QLabel("LoG Sigma Value (0.2-3.0):")
        blur_label.setStyleSheet("font-size: 7pt; color: #cccccc; margin-top: 0.8em;")
        layout.addWidget(blur_label)
        
        sigma_help = QLabel("Controls smoothing and edge scale")
        sigma_help.setStyleSheet("font-size: 6pt; color: #666666; font-style: italic;")
        layout.addWidget(sigma_help)
        
        blur_layout = QHBoxLayout()
        self.blur_slider = QSlider(Qt.Horizontal)
        self.blur_slider.setMinimum(1)
        self.blur_slider.setMaximum(15)
        self.blur_slider.setValue(5)
        self.blur_slider.setSingleStep(2)  # Only odd values
        self.blur_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #3a3a3a;
                height: 6px;
                background: #2d2d30;
                margin: 0px;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #007acc, stop:1 #005a9e);
                border: 1px solid #005a9e;
                width: 14px;
                height: 14px;
                margin: -5px 0;
                border-radius: 7px;
            }
            QSlider::handle:horizontal:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #1e90ff, stop:1 #007acc);
            }
        """)
        self.blur_slider.valueChanged.connect(self.update_labels)
        blur_layout.addWidget(self.blur_slider)
        
        self.blur_value_label = QLabel("5 (σ=1.00)")
        self.blur_value_label.setStyleSheet("font-size: 7pt; color: #ffffff; min-width: 5em;")
        blur_layout.addWidget(self.blur_value_label)
        
        layout.addLayout(blur_layout)
        
        layout.addStretch()
        
        # Buttons
        button_layout = QHBoxLayout()
        
        reset_btn = QPushButton("Reset to Default")
        reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #3a3a3a;
                color: #ffffff;
                border: 1px solid #3a3a3a;
                padding: 0.5em 1em;
                font-size: 7pt;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #505050;
                border: 1px solid #007acc;
            }
        """)
        reset_btn.clicked.connect(self.reset_values)
        button_layout.addWidget(reset_btn)
        
        button_layout.addStretch()
        
        ok_btn = QPushButton("Apply")
        ok_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #007acc, stop:1 #005a9e);
                color: #ffffff;
                border: 1px solid #005a9e;
                padding: 0.5em 1.5em;
                font-size: 7pt;
                border-radius: 3px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #1e90ff, stop:1 #007acc);
            }
        """)
        ok_btn.clicked.connect(self.accept)
        button_layout.addWidget(ok_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #3a3a3a;
                color: #ffffff;
                border: 1px solid #3a3a3a;
                padding: 0.5em 1em;
                font-size: 7pt;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #505050;
                border: 1px solid #007acc;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def update_labels(self):
        """Update value labels with actual values"""
        # Variance threshold display
        threshold_val = self.threshold_slider.value()
        variance_threshold = 10 + (threshold_val / 255.0) * 490
        self.threshold_value_label.setText(f"{threshold_val} (≈{variance_threshold:.0f})")
        
        # Sigma value display
        blur_val = self.blur_slider.value()
        sigma = blur_val / 5.0
        sigma = max(0.5, min(sigma, 3.0))
        self.blur_value_label.setText(f"{blur_val} (σ={sigma:.2f})")
    
    def reset_values(self):
        """Reset to default values"""
        self.threshold_slider.setValue(50)
        self.kernel_combo.setCurrentIndex(1)
        self.blur_slider.setValue(5)
    
    def get_parameters(self):
        """Return the parameter values"""
        return (
            self.threshold_slider.value(),
            int(self.kernel_combo.currentText()),
            self.blur_slider.value()
        )


class LaplacianIntermediatesDialog(QDialog):
    """Dialog to display intermediate steps of Laplacian edge detection in a grid"""
    
    def __init__(self, intermediates, parent=None):
        super().__init__(parent)
        self.intermediates = intermediates
        
        self.setWindowTitle("Robust Laplacian Edge Detection - Processing Steps")
        self.setMinimumSize(1400, 900)
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("Robust Laplacian-based Edge Detector (LoG + Zero Crossing)")
        title.setStyleSheet("font-size: 10pt; font-weight: bold; color: #ffffff; margin-bottom: 1em;")
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)
        
        # Create grid layout for images (3x3 grid for 7 steps)
        grid_widget = QWidget()
        grid_layout = QGridLayout()
        grid_layout.setSpacing(15)
        grid_widget.setLayout(grid_layout)
        
        # Step titles
        step_titles = [
            "1. Grayscale Conversion",
            "2. LoG Kernel Applied",
            "3. Local Variance Map (σ²)",
            "4. Zero-Crossing Strength Map",
            "5. Zero Crossings Detected",
            "6. Variance Filtered Edges",
            "7. Final Edges (Post-processed)"
        ]
        
        # Add images to grid (3 columns)
        row, col = 0, 0
        for i, (key, img) in enumerate(sorted(self.intermediates.items())):
            # Create container for this step
            step_container = QVBoxLayout()
            step_container.setSpacing(5)
            
            # Step title
            step_label = QLabel(step_titles[i])
            step_label.setStyleSheet("font-size: 8pt; color: #cccccc; font-weight: bold;")
            step_label.setAlignment(Qt.AlignCenter)
            step_container.addWidget(step_label)
            
            # Image label
            image_label = QLabel()
            image_label.setAlignment(Qt.AlignCenter)
            image_label.setStyleSheet("background-color: #252526; border: 1px solid #3a3a3a;")
            
            # Convert and display image
            height, width = img.shape[:2]
            max_size = 400
            if width > max_size or height > max_size:
                scale = max_size / max(width, height)
                new_width = int(width * scale)
                new_height = int(height * scale)
                img_resized = cv2.resize(img, (new_width, new_height))
            else:
                img_resized = img
            
            rgb_image = cv2.cvtColor(img_resized, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qt_image)
            
            image_label.setPixmap(pixmap)
            step_container.addWidget(image_label)
            
            # Create widget for this step
            step_widget = QWidget()
            step_widget.setLayout(step_container)
            
            # Add to grid
            grid_layout.addWidget(step_widget, row, col)
            
            col += 1
            if col >= 3:  # 3 columns per row
                col = 0
                row += 1
        
        # Add grid to main layout with scroll
        scroll_area = QScrollArea()
        scroll_area.setWidget(grid_widget)
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: #1e1e1e;
                border: none;
            }
            QScrollBar:vertical {
                background-color: #1e1e1e;
                width: 12px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background-color: #3a3a3a;
                min-height: 20px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #505050;
            }
        """)
        main_layout.addWidget(scroll_area)
        
        # Close button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        close_btn = QPushButton("Close")
        close_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #007acc, stop:1 #005a9e);
                color: #ffffff;
                border: 1px solid #005a9e;
                padding: 0.6em 2em;
                font-size: 8pt;
                border-radius: 3px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #1e90ff, stop:1 #007acc);
            }
        """)
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)
        
        button_layout.addStretch()
        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)


class HistogramMatchingDialog(QDialog):
    """Dialog for histogram matching with predefined mapping functions - OPTIMIZED"""
    
    def __init__(self, image, parent=None):
        super().__init__(parent)
        self.original_image = image.copy()
        
        # Convert to grayscale if needed
        if len(self.original_image.shape) == 3:
            self.gray_image = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2GRAY)
        else:
            self.gray_image = self.original_image.copy()
        
        # Downsample for preview if too large (PERFORMANCE BOOST)
        max_size = 512
        h, w = self.gray_image.shape
        if max(h, w) > max_size:
            scale = max_size / max(h, w)
            new_w, new_h = int(w * scale), int(h * scale)
            self.preview_image = cv2.resize(self.gray_image, (new_w, new_h), interpolation=cv2.INTER_AREA)
        else:
            self.preview_image = self.gray_image.copy()
        
        self.matched_image = self.gray_image.copy()
        self.matched_preview = self.preview_image.copy()
        self.current_function = "Linear (Identity)"
        self.param_value = 1.0
        
        # Cache original histogram (compute once)
        self.original_hist = cv2.calcHist([self.preview_image], [0], None, [256], [0, 256])
        
        # Cache for LUT
        self.current_lut = None
        
        # Debounce timer for slider updates
        self.update_timer = QTimer()
        self.update_timer.setSingleShot(True)
        self.update_timer.timeout.connect(self.update_plots)
        
        self.setWindowTitle("Histogram Matching with Mapping Functions")
        self.setMinimumSize(1500, 844)  # 25% larger than 75% size (1200x675 * 1.25)
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("📊 Histogram Matching with Predefined Functions")
        title.setStyleSheet("font-size: 11pt; font-weight: bold; color: #ffffff; margin-bottom: 0.5em;")
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)
        
        # Create top panel with controls
        control_panel = QWidget()
        control_layout = QHBoxLayout()
        
        # Function selector
        func_group = QGroupBox("Mapping Function")
        func_group.setStyleSheet("QGroupBox { font-weight: bold; color: #ffffff; }")
        func_layout = QVBoxLayout()
        
        self.function_combo = QComboBox()
        self.function_combo.addItems([
            "Linear (Identity)",
            "Power (Gamma)",
            "Exponential",
            "Sigmoid",
            "Piecewise Linear (Contrast Stretch)"
        ])
        self.function_combo.currentTextChanged.connect(self.on_function_changed)
        self.function_combo.setStyleSheet("""
            QComboBox {
                padding: 5px;
                font-size: 9pt;
                background-color: #2d2d30;
                color: #ffffff;
                border: 1px solid #3a3a3a;
            }
        """)
        func_layout.addWidget(self.function_combo)
        
        # Parameter slider
        self.param_label = QLabel("Parameter (γ): 1.0")
        self.param_label.setStyleSheet("color: #cccccc; font-size: 8pt; margin-top: 10px;")
        func_layout.addWidget(self.param_label)
        
        self.param_slider = QSlider(Qt.Horizontal)
        self.param_slider.setMinimum(1)
        self.param_slider.setMaximum(500)
        self.param_slider.setValue(100)
        self.param_slider.valueChanged.connect(self.on_parameter_changed_debounced)
        func_layout.addWidget(self.param_slider)
        
        # Function description
        self.func_description = QLabel("f(x) = x (Identity mapping)")
        self.func_description.setStyleSheet("color: #888888; font-size: 7pt; font-style: italic; margin-top: 5px;")
        self.func_description.setWordWrap(True)
        func_layout.addWidget(self.func_description)
        
        func_group.setLayout(func_layout)
        control_layout.addWidget(func_group)
        
        control_panel.setLayout(control_layout)
        main_layout.addWidget(control_panel)
        
        # Create scroll area for content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: #1e1e1e;
                border: none;
            }
        """)
        
        # Content widget
        content_widget = QWidget()
        content_layout = QVBoxLayout()
        content_layout.setSpacing(20)
        
        # Create matplotlib figure with subplots
        self.figure = Figure(figsize=(16, 10), facecolor='#1e1e1e')
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setStyleSheet("background-color: #1e1e1e;")
        
        # Create axes once (reuse them - PERFORMANCE BOOST)
        self.ax1 = self.figure.add_subplot(2, 3, 1)
        self.ax2 = self.figure.add_subplot(2, 3, 2)
        self.ax3 = self.figure.add_subplot(2, 3, 3)
        self.ax4 = self.figure.add_subplot(2, 3, 4)
        self.ax5 = self.figure.add_subplot(2, 3, 5)
        self.ax6 = self.figure.add_subplot(2, 3, 6)
        
        # Plot original data once (never changes - PERFORMANCE BOOST)
        self.plot_original_data()
        
        # Create plots
        self.update_plots()
        
        content_layout.addWidget(self.canvas)
        content_widget.setLayout(content_layout)
        scroll_area.setWidget(content_widget)
        
        main_layout.addWidget(scroll_area)
        
        # Bottom buttons
        button_layout = QHBoxLayout()
        
        # Apply button
        apply_btn = QPushButton("Apply Mapping to Main Image")
        apply_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #007acc, stop:1 #005a9e);
                color: #ffffff;
                border: 1px solid #005a9e;
                padding: 0.6em 1.5em;
                font-size: 8pt;
                border-radius: 3px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #1e90ff, stop:1 #007acc);
            }
        """)
        apply_btn.clicked.connect(self.apply_mapping)
        button_layout.addWidget(apply_btn)
        
        button_layout.addStretch()
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #3a3a3a;
                color: #ffffff;
                border: 1px solid #3a3a3a;
                padding: 0.6em 1.5em;
                font-size: 8pt;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #505050;
                border: 1px solid #007acc;
            }
        """)
        close_btn.clicked.connect(self.reject)
        button_layout.addWidget(close_btn)
        
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)
        
        self.mapping_applied = False
    
    def create_lut(self, func_name, param):
        """Create 256-entry lookup table for fast mapping - OPTIMIZED"""
        lut = np.zeros(256, dtype=np.uint8)
        
        for i in range(256):
            x = i / 255.0
            
            if func_name == "Linear (Identity)":
                y = x
            elif func_name == "Power (Gamma)":
                y = np.power(x, param)
            elif func_name == "Exponential":
                c = param
                if c != 0:
                    y = (np.exp(c * x) - 1) / (np.exp(c) - 1)
                else:
                    y = x
                y = np.clip(y, 0, 1)
            elif func_name == "Sigmoid":
                c = param * 10
                y = 1.0 / (1.0 + np.exp(-c * (x - 0.5)))
                # Normalize
                y_min = 1.0 / (1.0 + np.exp(c * 0.5))
                y_max = 1.0 / (1.0 + np.exp(-c * 0.5))
                y = (y - y_min) / (y_max - y_min)
            elif func_name == "Piecewise Linear (Contrast Stretch)":
                threshold_low = 0.5 - param * 0.4
                threshold_high = 0.5 + param * 0.4
                y = np.clip((x - threshold_low) / (threshold_high - threshold_low), 0, 1)
            else:
                y = x
            
            lut[i] = int(y * 255)
        
        return lut
    
    def apply_mapping_function(self, img, func_name, param):
        """Apply mapping function using fast LUT - OPTIMIZED"""
        # Special case for Contrast Stretch (needs percentiles from actual image)
        if func_name == "Piecewise Linear (Contrast Stretch)":
            p_low = (1.0 - param) * 50
            p_high = 100 - p_low
            v_low = np.percentile(img, p_low)
            v_high = np.percentile(img, p_high)
            result = np.clip((img.astype(np.float32) - v_low) / (v_high - v_low) * 255, 0, 255).astype(np.uint8)
            return result
        
        # Use cached LUT for all other functions
        if self.current_lut is None:
            self.current_lut = self.create_lut(func_name, param)
        
        # Apply LUT (very fast - single array lookup)
        result = cv2.LUT(img, self.current_lut)
        return result
    
    def get_mapping_curve(self, func_name, param):
        """Get mapping curve using cached LUT - OPTIMIZED"""
        if self.current_lut is None:
            self.current_lut = self.create_lut(func_name, param)
        
        x = np.arange(256)
        y = self.current_lut.astype(np.float32)
        
        return x, y
    
    def plot_original_data(self):
        """Plot original image and histogram once - OPTIMIZED (never changes)"""
        # Style axes
        for ax in [self.ax1, self.ax2]:
            ax.set_facecolor('#252526')
            ax.tick_params(colors='#cccccc', labelsize=8)
            ax.spines['bottom'].set_color('#3a3a3a')
            ax.spines['top'].set_color('#3a3a3a')
            ax.spines['left'].set_color('#3a3a3a')
            ax.spines['right'].set_color('#3a3a3a')
        
        # Original image
        self.ax1.imshow(self.preview_image, cmap='gray')
        self.ax1.set_title('Original Image', color='#ffffff', fontsize=9, pad=8)
        self.ax1.axis('off')
        
        # Original histogram
        self.ax2.plot(self.original_hist, color='#00d4ff', linewidth=1.5)
        self.ax2.fill_between(range(256), self.original_hist.flatten(), alpha=0.3, color='#00d4ff')
        self.ax2.set_title('Original Histogram', color='#ffffff', fontsize=9, pad=8)
        self.ax2.set_xlabel('Intensity', color='#cccccc', fontsize=7)
        self.ax2.set_ylabel('Frequency', color='#cccccc', fontsize=7)
        self.ax2.set_xlim([0, 255])
        self.ax2.grid(True, alpha=0.2, color='#3a3a3a')
        
        # Adjust layout with better spacing to prevent text overlap
        self.figure.subplots_adjust(left=0.08, right=0.95, top=0.93, bottom=0.08, wspace=0.3, hspace=0.35)
    
    def update_plots(self):
        """Update only matched plots (right column) - OPTIMIZED"""
        # Apply mapping to preview (fast with LUT)
        self.matched_preview = self.apply_mapping_function(
            self.preview_image, self.current_function, self.param_value
        )
        
        # Also apply to full resolution for final result
        self.matched_image = self.apply_mapping_function(
            self.gray_image, self.current_function, self.param_value
        )
        
        # Calculate matched histogram
        hist_matched = cv2.calcHist([self.matched_preview], [0], None, [256], [0, 256])
        
        # Get mapping curve (uses cached LUT)
        x_curve, y_curve = self.get_mapping_curve(self.current_function, self.param_value)
        
        # Calculate difference
        diff = cv2.absdiff(self.preview_image, self.matched_preview)
        
        # Clear only right column axes
        self.ax3.clear()
        self.ax4.clear()
        self.ax5.clear()
        self.ax6.clear()
        
        # Style right column axes
        for ax in [self.ax3, self.ax4, self.ax5, self.ax6]:
            ax.set_facecolor('#252526')
            ax.tick_params(colors='#cccccc', labelsize=8)
            ax.spines['bottom'].set_color('#3a3a3a')
            ax.spines['top'].set_color('#3a3a3a')
            ax.spines['left'].set_color('#3a3a3a')
            ax.spines['right'].set_color('#3a3a3a')
        
        # Mapping function curve
        self.ax3.plot(x_curve, y_curve, color='#ff9500', linewidth=2)
        self.ax3.plot([0, 255], [0, 255], 'r--', alpha=0.3, linewidth=1, label='Identity')
        self.ax3.set_title('Mapping Function', color='#ffffff', fontsize=9, pad=8)
        self.ax3.set_xlabel('Input Intensity', color='#cccccc', fontsize=7)
        self.ax3.set_ylabel('Output Intensity', color='#cccccc', fontsize=7)
        self.ax3.set_xlim([0, 255])
        self.ax3.set_ylim([0, 255])
        self.ax3.grid(True, alpha=0.2, color='#3a3a3a')
        self.ax3.legend(facecolor='#252526', edgecolor='#3a3a3a', labelcolor='#cccccc', fontsize=6, loc='upper left')
        
        # Matched image
        self.ax4.imshow(self.matched_preview, cmap='gray')
        self.ax4.set_title('Matched Image', color='#ffffff', fontsize=9, pad=8)
        self.ax4.axis('off')
        
        # Matched histogram
        self.ax5.plot(hist_matched, color='#00ff88', linewidth=1.5)
        self.ax5.fill_between(range(256), hist_matched.flatten(), alpha=0.3, color='#00ff88')
        self.ax5.set_title('Matched Histogram', color='#ffffff', fontsize=9, pad=8)
        self.ax5.set_xlabel('Intensity', color='#cccccc', fontsize=7)
        self.ax5.set_ylabel('Frequency', color='#cccccc', fontsize=7)
        self.ax5.set_xlim([0, 255])
        self.ax5.grid(True, alpha=0.2, color='#3a3a3a')
        
        # Difference map
        self.ax6.imshow(diff, cmap='hot')
        self.ax6.set_title('Difference Map', color='#ffffff', fontsize=9, pad=8)
        self.ax6.axis('off')
        
        # Don't call tight_layout here - it causes window resizing issues
        self.canvas.draw_idle()  # Use draw_idle() for better performance
    
    def on_function_changed(self):
        """Handle function selection change"""
        self.current_function = self.function_combo.currentText()
        self.current_lut = None  # Invalidate cached LUT
        
        # Update parameter label and description based on function
        if self.current_function == "Linear (Identity)":
            self.param_label.setText("Parameter: N/A")
            self.param_slider.setEnabled(False)
            self.func_description.setText("f(x) = x (No transformation)")
        
        elif self.current_function == "Power (Gamma)":
            self.param_label.setText(f"Parameter (γ): {self.param_value:.2f}")
            self.param_slider.setEnabled(True)
            self.func_description.setText("f(x) = x^γ (γ<1 brightens, γ>1 darkens)")
        
        elif self.current_function == "Exponential":
            self.param_label.setText(f"Parameter (c): {self.param_value:.2f}")
            self.param_slider.setEnabled(True)
            self.func_description.setText("f(x) = (e^(cx) - 1) / (e^c - 1) (Darkens bright regions)")
        
        elif self.current_function == "Sigmoid":
            self.param_label.setText(f"Parameter (steepness): {self.param_value:.2f}")
            self.param_slider.setEnabled(True)
            self.func_description.setText("f(x) = 1/(1+e^(-c(x-0.5))) (S-shaped contrast adjustment)")
        
        elif self.current_function == "Piecewise Linear (Contrast Stretch)":
            self.param_label.setText(f"Parameter (stretch): {self.param_value:.2f}")
            self.param_slider.setEnabled(True)
            self.func_description.setText("Stretches histogram between percentiles (increases contrast)")
        
        self.update_plots()
    
    def on_parameter_changed_debounced(self):
        """Handle parameter slider change with debouncing - OPTIMIZED"""
        # Map slider value (1-500) to appropriate parameter range
        func_name = self.current_function
        slider_val = self.param_slider.value()
        
        if func_name == "Power (Gamma)":
            # Map to 0.1 - 5.0
            self.param_value = 0.1 + (slider_val / 500.0) * 4.9
            self.param_label.setText(f"Parameter (γ): {self.param_value:.2f}")
        
        elif func_name == "Exponential":
            # Map to 0.5 - 5.0
            self.param_value = 0.5 + (slider_val / 500.0) * 4.5
            self.param_label.setText(f"Parameter (c): {self.param_value:.2f}")
        
        elif func_name == "Sigmoid":
            # Map to 0.1 - 2.0
            self.param_value = 0.1 + (slider_val / 500.0) * 1.9
            self.param_label.setText(f"Parameter (steepness): {self.param_value:.2f}")
        
        elif func_name == "Piecewise Linear (Contrast Stretch)":
            # Map to 0.1 - 1.0
            self.param_value = 0.1 + (slider_val / 500.0) * 0.9
            self.param_label.setText(f"Parameter (stretch): {self.param_value:.2f}")
        
        # Invalidate cached LUT
        self.current_lut = None
        
        # Debounce: delay update by 30ms to avoid excessive redraws
        self.update_timer.stop()
        self.update_timer.start(30)
    
    def apply_mapping(self):
        """Mark that mapping should be applied"""
        self.mapping_applied = True
        self.accept()


class HistogramAnalysisDialog(QDialog):
    """Dialog to display histogram analysis with PDF, CDF, and equalization"""
    
    def __init__(self, image, parent=None):
        super().__init__(parent)
        self.original_image = image.copy()
        
        # Convert to grayscale if needed
        if len(self.original_image.shape) == 3:
            self.gray_image = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2GRAY)
        else:
            self.gray_image = self.original_image.copy()
        
        # Apply histogram equalization
        self.equalized_image = cv2.equalizeHist(self.gray_image)
        
        self.setWindowTitle("Histogram Analysis & Equalization")
        self.setMinimumSize(1500, 844)  # 25% larger than 75% size (1200x675 * 1.25)
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("📊 Histogram Analysis with Equalization")
        title.setStyleSheet("font-size: 11pt; font-weight: bold; color: #ffffff; margin-bottom: 0.5em;")
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)
        
        # Create scroll area for content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: #1e1e1e;
                border: none;
            }
        """)
        
        # Content widget
        content_widget = QWidget()
        content_layout = QVBoxLayout()
        content_layout.setSpacing(20)
        
        # Create matplotlib figure with subplots
        self.figure = Figure(figsize=(16, 10), facecolor='#1e1e1e')
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setStyleSheet("background-color: #1e1e1e;")
        
        # Create 2x4 grid: 
        # Row 1: Original Image, Original Histogram, Original PDF, Original CDF
        # Row 2: Equalized Image, Equalized Histogram, Equalized PDF, Equalized CDF
        
        # Original image and analysis
        ax1 = self.figure.add_subplot(2, 4, 1)
        ax2 = self.figure.add_subplot(2, 4, 2)
        ax3 = self.figure.add_subplot(2, 4, 3)
        ax4 = self.figure.add_subplot(2, 4, 4)
        
        # Equalized image and analysis
        ax5 = self.figure.add_subplot(2, 4, 5)
        ax6 = self.figure.add_subplot(2, 4, 6)
        ax7 = self.figure.add_subplot(2, 4, 7)
        ax8 = self.figure.add_subplot(2, 4, 8)
        
        # Calculate histograms
        hist_original = cv2.calcHist([self.gray_image], [0], None, [256], [0, 256])
        hist_equalized = cv2.calcHist([self.equalized_image], [0], None, [256], [0, 256])
        
        # Calculate PDF (Probability Density Function)
        pdf_original = hist_original / hist_original.sum()
        pdf_equalized = hist_equalized / hist_equalized.sum()
        
        # Calculate CDF (Cumulative Distribution Function)
        cdf_original = pdf_original.cumsum()
        cdf_equalized = pdf_equalized.cumsum()
        
        # Style all axes
        all_axes = [ax1, ax2, ax3, ax4, ax5, ax6, ax7, ax8]
        for ax in all_axes:
            ax.set_facecolor('#252526')
            ax.tick_params(colors='#cccccc', labelsize=8)
            ax.spines['bottom'].set_color('#3a3a3a')
            ax.spines['top'].set_color('#3a3a3a')
            ax.spines['left'].set_color('#3a3a3a')
            ax.spines['right'].set_color('#3a3a3a')
            for spine in ax.spines.values():
                spine.set_linewidth(1.5)
        
        # Row 1: Original Image Analysis
        ax1.imshow(self.gray_image, cmap='gray')
        ax1.set_title('Original Image', color='#ffffff', fontsize=10, pad=10)
        ax1.axis('off')
        
        ax2.plot(hist_original, color='#00d4ff', linewidth=1.5)
        ax2.fill_between(range(256), hist_original.flatten(), alpha=0.3, color='#00d4ff')
        ax2.set_title('Histogram', color='#ffffff', fontsize=10, pad=10)
        ax2.set_xlabel('Pixel Intensity', color='#cccccc', fontsize=8)
        ax2.set_ylabel('Frequency', color='#cccccc', fontsize=8)
        ax2.set_xlim([0, 255])
        ax2.grid(True, alpha=0.2, color='#3a3a3a')
        
        ax3.plot(pdf_original, color='#00ff88', linewidth=1.5)
        ax3.fill_between(range(256), pdf_original.flatten(), alpha=0.3, color='#00ff88')
        ax3.set_title('PDF (Probability Density)', color='#ffffff', fontsize=10, pad=10)
        ax3.set_xlabel('Pixel Intensity', color='#cccccc', fontsize=8)
        ax3.set_ylabel('Probability', color='#cccccc', fontsize=8)
        ax3.set_xlim([0, 255])
        ax3.grid(True, alpha=0.2, color='#3a3a3a')
        
        ax4.plot(cdf_original, color='#ff9500', linewidth=2)
        ax4.set_title('CDF (Cumulative Distribution)', color='#ffffff', fontsize=10, pad=10)
        ax4.set_xlabel('Pixel Intensity', color='#cccccc', fontsize=8)
        ax4.set_ylabel('Cumulative Probability', color='#cccccc', fontsize=8)
        ax4.set_xlim([0, 255])
        ax4.set_ylim([0, 1])
        ax4.grid(True, alpha=0.2, color='#3a3a3a')
        
        # Row 2: Equalized Image Analysis
        ax5.imshow(self.equalized_image, cmap='gray')
        ax5.set_title('Equalized Image', color='#ffffff', fontsize=10, pad=10)
        ax5.axis('off')
        
        ax6.plot(hist_equalized, color='#00d4ff', linewidth=1.5)
        ax6.fill_between(range(256), hist_equalized.flatten(), alpha=0.3, color='#00d4ff')
        ax6.set_title('Histogram (Equalized)', color='#ffffff', fontsize=10, pad=10)
        ax6.set_xlabel('Pixel Intensity', color='#cccccc', fontsize=8)
        ax6.set_ylabel('Frequency', color='#cccccc', fontsize=8)
        ax6.set_xlim([0, 255])
        ax6.grid(True, alpha=0.2, color='#3a3a3a')
        
        ax7.plot(pdf_equalized, color='#00ff88', linewidth=1.5)
        ax7.fill_between(range(256), pdf_equalized.flatten(), alpha=0.3, color='#00ff88')
        ax7.set_title('PDF (Equalized)', color='#ffffff', fontsize=10, pad=10)
        ax7.set_xlabel('Pixel Intensity', color='#cccccc', fontsize=8)
        ax7.set_ylabel('Probability', color='#cccccc', fontsize=8)
        ax7.set_xlim([0, 255])
        ax7.grid(True, alpha=0.2, color='#3a3a3a')
        
        ax8.plot(cdf_equalized, color='#ff9500', linewidth=2)
        ax8.set_title('CDF (Equalized)', color='#ffffff', fontsize=10, pad=10)
        ax8.set_xlabel('Pixel Intensity', color='#cccccc', fontsize=8)
        ax8.set_ylabel('Cumulative Probability', color='#cccccc', fontsize=8)
        ax8.set_xlim([0, 255])
        ax8.set_ylim([0, 1])
        ax8.grid(True, alpha=0.2, color='#3a3a3a')
        
        self.figure.tight_layout(pad=2.0)
        
        content_layout.addWidget(self.canvas)
        content_widget.setLayout(content_layout)
        scroll_area.setWidget(content_widget)
        
        main_layout.addWidget(scroll_area)
        
        # Bottom buttons
        button_layout = QHBoxLayout()
        
        # Apply equalization button
        apply_btn = QPushButton("Apply Equalization to Main Image")
        apply_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #007acc, stop:1 #005a9e);
                color: #ffffff;
                border: 1px solid #005a9e;
                padding: 0.6em 1.5em;
                font-size: 8pt;
                border-radius: 3px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #1e90ff, stop:1 #007acc);
            }
        """)
        apply_btn.clicked.connect(self.apply_equalization)
        button_layout.addWidget(apply_btn)
        
        button_layout.addStretch()
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #3a3a3a;
                color: #ffffff;
                border: 1px solid #3a3a3a;
                padding: 0.6em 1.5em;
                font-size: 8pt;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #505050;
                border: 1px solid #007acc;
            }
        """)
        close_btn.clicked.connect(self.reject)
        button_layout.addWidget(close_btn)
        
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)
        
        self.equalization_applied = False
    
    def apply_equalization(self):
        """Mark that equalization should be applied"""
        self.equalization_applied = True
        self.accept()


class RotationDialog(QDialog):
    """Dialog for image rotation with angle slider and live preview"""
    
    def __init__(self, image, parent=None):
        super().__init__(parent)
        self.original_image = image.copy()
        self.parent_app = parent
        
        self.setWindowTitle("Rotate Image")
        self.setMinimumSize(1000, 700)
        
        # Main layout (horizontal)
        main_layout = QHBoxLayout()
        
        # Left panel for controls
        left_panel = QVBoxLayout()
        left_panel_widget = QWidget()
        left_panel_widget.setLayout(left_panel)
        left_panel_widget.setMaximumWidth(300)
        
        # Title
        title = QLabel("Rotation Settings")
        title.setStyleSheet("font-size: 9pt; font-weight: bold; color: #ffffff;")
        left_panel.addWidget(title)
        
        # Angle slider
        angle_label = QLabel("Rotation Angle (degrees):")
        angle_label.setStyleSheet("font-size: 7pt; color: #cccccc; margin-top: 0.8em;")
        left_panel.addWidget(angle_label)
        
        self.angle_slider = QSlider(Qt.Horizontal)
        self.angle_slider.setMinimum(-180)
        self.angle_slider.setMaximum(180)
        self.angle_slider.setValue(0)
        self.angle_slider.setTickPosition(QSlider.TicksBelow)
        self.angle_slider.setTickInterval(30)
        self.angle_slider.valueChanged.connect(self.update_preview)
        left_panel.addWidget(self.angle_slider)
        
        self.angle_value_label = QLabel("0°")
        self.angle_value_label.setStyleSheet("font-size: 7pt; color: #ffffff;")
        self.angle_value_label.setAlignment(Qt.AlignCenter)
        left_panel.addWidget(self.angle_value_label)
        
        # Info label
        info_label = QLabel("• Positive = clockwise rotation\n• Negative = counter-clockwise rotation\n• 0° = no rotation")
        info_label.setStyleSheet("font-size: 6pt; color: #888888; margin-top: 1em; padding: 0.5em; background-color: #252526; border-radius: 2px;")
        info_label.setWordWrap(True)
        left_panel.addWidget(info_label)
        
        left_panel.addStretch()
        
        # Buttons
        button_layout = QHBoxLayout()
        
        reset_btn = QPushButton("Reset")
        reset_btn.setStyleSheet("""
            QPushButton {
                font-size: 7pt;
                padding: 0.4em 0.8em;
                background-color: #3f3f46;
                color: #ffffff;
                border: none;
                border-radius: 2px;
            }
            QPushButton:hover {
                background-color: #4f4f56;
            }
        """)
        reset_btn.clicked.connect(self.reset_values)
        button_layout.addWidget(reset_btn)
        
        apply_btn = QPushButton("Apply")
        apply_btn.setStyleSheet("""
            QPushButton {
                font-size: 7pt;
                padding: 0.4em 0.8em;
                background-color: #007acc;
                color: #ffffff;
                border: none;
                border-radius: 2px;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
        """)
        apply_btn.clicked.connect(self.accept)
        button_layout.addWidget(apply_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet("""
            QPushButton {
                font-size: 7pt;
                padding: 0.4em 0.8em;
                background-color: #3f3f46;
                color: #ffffff;
                border: none;
                border-radius: 2px;
            }
            QPushButton:hover {
                background-color: #4f4f56;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        left_panel.addLayout(button_layout)
        
        # Right panel for preview
        right_panel = QVBoxLayout()
        
        preview_title = QLabel("Preview")
        preview_title.setStyleSheet("font-size: 8pt; font-weight: bold; color: #ffffff;")
        preview_title.setAlignment(Qt.AlignCenter)
        right_panel.addWidget(preview_title)
        
        self.preview_label = QLabel()
        self.preview_label.setMinimumSize(600, 500)
        self.preview_label.setMaximumSize(600, 500)
        self.preview_label.setStyleSheet("background-color: #1e1e1e; border: 1px solid #3f3f46;")
        self.preview_label.setAlignment(Qt.AlignCenter)
        right_panel.addWidget(self.preview_label)
        
        # Add panels to main layout
        main_layout.addWidget(left_panel_widget)
        main_layout.addLayout(right_panel)
        
        self.setLayout(main_layout)
        
        # Initial preview
        self.update_preview()
    
    def update_preview(self):
        """Update the preview with current rotation"""
        angle = self.angle_slider.value()
        self.angle_value_label.setText(f"{angle}°")
        
        # Apply rotation
        try:
            from image_processor import ImageProcessor
            processor = ImageProcessor()
            rotated = processor.rotate_image(self.original_image, angle)
            
            # Convert BGR to RGB for display
            if len(rotated.shape) == 3:
                rotated_rgb = cv2.cvtColor(rotated, cv2.COLOR_BGR2RGB)
            else:
                rotated_rgb = cv2.cvtColor(rotated, cv2.COLOR_GRAY2RGB)
            
            # Update dialog preview
            height, width = rotated_rgb.shape[:2]
            bytes_per_line = 3 * width
            q_image = QImage(rotated_rgb.data, width, height, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(q_image)
            
            # Scale to fit preview
            scaled_pixmap = pixmap.scaled(
                self.preview_label.width(), 
                self.preview_label.height(),
                Qt.KeepAspectRatio, 
                Qt.SmoothTransformation
            )
            self.preview_label.setPixmap(scaled_pixmap)
            
            # Update main window preview
            if self.parent_app and hasattr(self.parent_app, 'current_image'):
                temp_image = self.parent_app.current_image
                self.parent_app.current_image = rotated
                self.parent_app.display_image()
                self.parent_app.current_image = temp_image
        
        except Exception as e:
            print(f"Preview error: {e}")
    
    def reset_values(self):
        """Reset to default value"""
        self.angle_slider.setValue(0)
    
    def get_angle(self):
        """Return the rotation angle"""
        return self.angle_slider.value()
    
    def closeEvent(self, event):
        """Restore original image when dialog closes"""
        if self.parent_app and hasattr(self.parent_app, 'display_image'):
            self.parent_app.display_image()
        event.accept()
    
    def reject(self):
        """Restore original image when cancelled"""
        if self.parent_app and hasattr(self.parent_app, 'display_image'):
            self.parent_app.display_image()
        super().reject()


class KMeansDialog(QDialog):
    """Dialog for K-means clustering with K slider"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("K-Means Clustering")
        self.setMinimumSize(400, 250)
        
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("K-Means Clustering Settings")
        title.setStyleSheet("font-size: 9pt; font-weight: bold; color: #ffffff;")
        layout.addWidget(title)
        
        # K clusters slider
        k_label = QLabel("Number of Clusters (K):")
        k_label.setStyleSheet("font-size: 7pt; color: #cccccc; margin-top: 0.8em;")
        layout.addWidget(k_label)
        
        self.k_slider = QSlider(Qt.Horizontal)
        self.k_slider.setMinimum(2)
        self.k_slider.setMaximum(10)
        self.k_slider.setValue(3)
        self.k_slider.setTickPosition(QSlider.TicksBelow)
        self.k_slider.setTickInterval(1)
        self.k_slider.valueChanged.connect(self.update_label)
        layout.addWidget(self.k_slider)
        
        self.k_value_label = QLabel("3 clusters")
        self.k_value_label.setStyleSheet("font-size: 7pt; color: #ffffff;")
        self.k_value_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.k_value_label)
        
        # Info label
        info_label = QLabel("• Higher K = more color segments\n• Lower K = fewer, broader colors\n• Processing time increases with K")
        info_label.setStyleSheet("font-size: 6pt; color: #888888; margin-top: 1em; padding: 0.5em; background-color: #252526; border-radius: 2px;")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        layout.addStretch()
        
        # Buttons
        button_layout = QHBoxLayout()
        
        reset_btn = QPushButton("Reset")
        reset_btn.setStyleSheet("""
            QPushButton {
                font-size: 7pt;
                padding: 0.4em 0.8em;
                background-color: #3f3f46;
                color: #ffffff;
                border: none;
                border-radius: 2px;
            }
            QPushButton:hover {
                background-color: #4f4f56;
            }
        """)
        reset_btn.clicked.connect(self.reset_values)
        button_layout.addWidget(reset_btn)
        
        apply_btn = QPushButton("Apply")
        apply_btn.setStyleSheet("""
            QPushButton {
                font-size: 7pt;
                padding: 0.4em 0.8em;
                background-color: #007acc;
                color: #ffffff;
                border: none;
                border-radius: 2px;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
        """)
        apply_btn.clicked.connect(self.accept)
        button_layout.addWidget(apply_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet("""
            QPushButton {
                font-size: 7pt;
                padding: 0.4em 0.8em;
                background-color: #3f3f46;
                color: #ffffff;
                border: none;
                border-radius: 2px;
            }
            QPushButton:hover {
                background-color: #4f4f56;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def update_label(self):
        """Update value label"""
        k = self.k_slider.value()
        self.k_value_label.setText(f"{k} cluster{'s' if k > 1 else ''}")
    
    def reset_values(self):
        """Reset to default value"""
        self.k_slider.setValue(3)
    
    def get_k(self):
        """Return the K value"""
        return self.k_slider.value()


class CropDialog(QDialog):
    """Dialog for interactive image cropping"""
    
    def __init__(self, image: np.ndarray, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Crop Image")
        self.setMinimumSize(400, 300)  # 50% of typical size
        self.image = image
        self.crop_rect = QRect()
        self.start_point = QPoint()
        self.end_point = QPoint()
        self.is_drawing = False
        
        # Create layout
        layout = QVBoxLayout()
        
        # Image label
        self.image_label = QLabel()
        self.image_label.setMouseTracking(True)
        self.display_image()
        
        layout.addWidget(self.image_label)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
        
        # Connect mouse events
        self.image_label.mousePressEvent = self.mouse_press
        self.image_label.mouseMoveEvent = self.mouse_move
        self.image_label.mouseReleaseEvent = self.mouse_release
    
    def display_image(self):
        """Display the image with crop rectangle"""
        display_img = self.image.copy()
        
        if not self.crop_rect.isNull():
            # Draw rectangle on image
            cv2.rectangle(display_img, 
                         (self.crop_rect.x(), self.crop_rect.y()),
                         (self.crop_rect.x() + self.crop_rect.width(),
                          self.crop_rect.y() + self.crop_rect.height()),
                         (0, 255, 0), 2)
        
        # Convert to QPixmap
        height, width, channel = display_img.shape
        bytes_per_line = 3 * width
        q_image = QImage(display_img.data, width, height, bytes_per_line, 
                        QImage.Format_RGB888).rgbSwapped()
        
        pixmap = QPixmap.fromImage(q_image)
        # Scale to 50% for display
        pixmap = pixmap.scaled(pixmap.width() // 2, pixmap.height() // 2, 
                               Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.image_label.setPixmap(pixmap)
    
    def mouse_press(self, event):
        """Handle mouse press event"""
        if event.button() == Qt.LeftButton:
            # Scale coordinates back to original image size (2x)
            self.start_point = QPoint(event.pos().x() * 2, event.pos().y() * 2)
            self.is_drawing = True
    
    def mouse_move(self, event):
        """Handle mouse move event"""
        if self.is_drawing:
            # Scale coordinates back to original image size (2x)
            self.end_point = QPoint(event.pos().x() * 2, event.pos().y() * 2)
            self.crop_rect = QRect(self.start_point, self.end_point).normalized()
            self.display_image()
    
    def mouse_release(self, event):
        """Handle mouse release event"""
        if event.button() == Qt.LeftButton:
            self.is_drawing = False
            # Scale coordinates back to original image size (2x)
            self.end_point = QPoint(event.pos().x() * 2, event.pos().y() * 2)
            self.crop_rect = QRect(self.start_point, self.end_point).normalized()
            self.display_image()
    
    def get_crop_rect(self):
        """Return the crop rectangle coordinates (already in original image coordinates)"""
        return (self.crop_rect.x(), self.crop_rect.y(),
                self.crop_rect.width(), self.crop_rect.height())


class GrabCutDialog(QDialog):
    """Dialog for interactive GrabCut segmentation - draw rectangle around subject"""
    
    def __init__(self, image: np.ndarray, parent=None):
        super().__init__(parent)
        self.setWindowTitle("GrabCut Segmentation - Draw Rectangle Around Subject")
        self.setMinimumSize(400, 300)  # 50% of original size (800x600)
        self.image = image
        self.selection_rect = QRect()
        self.start_point = QPoint()
        self.end_point = QPoint()
        self.is_drawing = False
        
        # Create layout
        layout = QVBoxLayout()
        
        # Instructions
        instructions = QLabel(
            "<b>Instructions:</b><br>"
            "1. Click and drag to draw a rectangle around the subject (human/object)<br>"
            "2. Make sure the rectangle covers the entire subject<br>"
            "3. The algorithm will automatically separate foreground from background<br>"
            "4. Click 'Apply' to process"
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("padding: 10px; background-color: #e8f4f8; border-radius: 5px;")
        layout.addWidget(instructions)
        
        # Image display in scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        self.image_label = QLabel()
        self.image_label.setMouseTracking(True)
        self.display_image()
        
        scroll_area.setWidget(self.image_label)
        layout.addWidget(scroll_area)
        
        # Iterations slider
        iter_layout = QHBoxLayout()
        iter_layout.addWidget(QLabel("Iterations (quality):"))
        self.iter_slider = QSlider(Qt.Horizontal)
        self.iter_slider.setMinimum(1)
        self.iter_slider.setMaximum(10)
        self.iter_slider.setValue(5)
        self.iter_slider.setTickPosition(QSlider.TicksBelow)
        self.iter_slider.setTickInterval(1)
        iter_layout.addWidget(self.iter_slider)
        self.iter_label = QLabel("5")
        self.iter_slider.valueChanged.connect(lambda v: self.iter_label.setText(str(v)))
        iter_layout.addWidget(self.iter_label)
        layout.addLayout(iter_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        reset_btn = QPushButton("Reset Rectangle")
        reset_btn.clicked.connect(self.reset_selection)
        button_layout.addWidget(reset_btn)
        
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        button_layout.addWidget(button_box)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # Connect mouse events
        self.image_label.mousePressEvent = self.mouse_press
        self.image_label.mouseMoveEvent = self.mouse_move
        self.image_label.mouseReleaseEvent = self.mouse_release
    
    def display_image(self):
        """Display the image with selection rectangle"""
        display_img = self.image.copy()
        
        if not self.selection_rect.isNull():
            # Draw rectangle on image
            cv2.rectangle(display_img, 
                         (self.selection_rect.x(), self.selection_rect.y()),
                         (self.selection_rect.x() + self.selection_rect.width(),
                          self.selection_rect.y() + self.selection_rect.height()),
                         (0, 255, 0), 3)
            
            # Add semi-transparent overlay outside rectangle
            overlay = display_img.copy()
            cv2.rectangle(overlay, (0, 0), (display_img.shape[1], display_img.shape[0]), 
                         (0, 0, 0), -1)
            cv2.rectangle(overlay, 
                         (self.selection_rect.x(), self.selection_rect.y()),
                         (self.selection_rect.x() + self.selection_rect.width(),
                          self.selection_rect.y() + self.selection_rect.height()),
                         (255, 255, 255), -1)
            display_img = cv2.addWeighted(display_img, 0.7, overlay, 0.3, 0)
        
        # Convert to QPixmap
        height, width, channel = display_img.shape
        bytes_per_line = 3 * width
        q_image = QImage(display_img.data, width, height, bytes_per_line, 
                        QImage.Format_RGB888).rgbSwapped()
        
        pixmap = QPixmap.fromImage(q_image)
        # Scale to 50% for display
        pixmap = pixmap.scaled(pixmap.width() // 2, pixmap.height() // 2, 
                               Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.image_label.setPixmap(pixmap)
        self.image_label.adjustSize()
    
    def mouse_press(self, event):
        """Handle mouse press event"""
        if event.button() == Qt.LeftButton:
            # Scale coordinates back to original image size (2x)
            self.start_point = QPoint(event.pos().x() * 2, event.pos().y() * 2)
            self.is_drawing = True
    
    def mouse_move(self, event):
        """Handle mouse move event"""
        if self.is_drawing:
            # Scale coordinates back to original image size (2x)
            self.end_point = QPoint(event.pos().x() * 2, event.pos().y() * 2)
            self.selection_rect = QRect(self.start_point, self.end_point).normalized()
            self.display_image()
    
    def mouse_release(self, event):
        """Handle mouse release event"""
        if event.button() == Qt.LeftButton:
            self.is_drawing = False
            # Scale coordinates back to original image size (2x)
            self.end_point = QPoint(event.pos().x() * 2, event.pos().y() * 2)
            self.selection_rect = QRect(self.start_point, self.end_point).normalized()
            self.display_image()
    
    def reset_selection(self):
        """Reset the selection rectangle"""
        self.selection_rect = QRect()
        self.display_image()
    
    def get_selection_rect(self):
        """Return the selection rectangle coordinates (already in original image coordinates)"""
        return (self.selection_rect.x(), self.selection_rect.y(),
                self.selection_rect.width(), self.selection_rect.height())
    
    def get_iterations(self):
        """Return the number of iterations"""
        return self.iter_slider.value()


class PhotoEditorApp(QMainWindow):
    """Main Photo Editor Application Window"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Photo Editor - Advanced Image Processing")
        self.setGeometry(100, 100, 1400, 800)
        
        # Initialize variables
        self.current_image: Optional[np.ndarray] = None
        self.original_image: Optional[np.ndarray] = None
        self.history: List[np.ndarray] = []
        self.history_index: int = -1
        self.current_file_path: Optional[str] = None
        self.max_history = 20
        self.sidebar_collapsed = False
        
        # Initialize processor
        self.processor = ImageProcessor()
        
        # Setup UI
        self.init_ui()
        
        # Apply modern theme
        self.apply_modern_theme()
        
    def init_ui(self):
        """Initialize the user interface"""
        # Create menu bar
        self.create_menu_bar()
        
        # Create toolbar
        self.create_toolbar()
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout with no margins
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create splitter for resizable sidebar
        from PyQt5.QtWidgets import QSplitter, QToolButton
        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.setHandleWidth(3)
        
        # Create sidebar container with collapse button
        sidebar_container = QWidget()
        sidebar_layout = QVBoxLayout()
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)
        
        # Collapse/Expand button
        self.collapse_btn = QToolButton()
        self.collapse_btn.setText("◀")
        self.collapse_btn.setToolTip("Collapse Sidebar")
        self.collapse_btn.clicked.connect(self.toggle_sidebar)
        self.collapse_btn.setFixedHeight(30)
        sidebar_layout.addWidget(self.collapse_btn)
        
        # Left panel (controls)
        self.control_panel_widget = self.create_control_panel()
        sidebar_layout.addWidget(self.control_panel_widget)
        
        sidebar_container.setLayout(sidebar_layout)
        
        # Right panel (image display)
        self.create_image_display()
        
        # Add to splitter
        self.splitter.addWidget(sidebar_container)
        self.splitter.addWidget(self.scroll_area)
        
        # Set initial sizes (350px for sidebar, rest for image)
        self.splitter.setSizes([350, 1050])
        self.splitter.setStretchFactor(0, 0)
        self.splitter.setStretchFactor(1, 1)
        
        # Make splitter resizable
        self.splitter.setCollapsible(0, False)
        self.splitter.setCollapsible(1, False)
        
        main_layout.addWidget(self.splitter)
        central_widget.setLayout(main_layout)
        
        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
    def create_menu_bar(self):
        """Create application menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        open_action = QAction("Open Image", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_image)
        file_menu.addAction(open_action)
        
        save_action = QAction("Save Image", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_image)
        file_menu.addAction(save_action)
        
        save_as_action = QAction("Save As...", self)
        save_as_action.setShortcut("Ctrl+Shift+S")
        save_as_action.triggered.connect(self.save_image_as)
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu("Edit")
        
        undo_action = QAction("Undo", self)
        undo_action.setShortcut("Ctrl+Z")
        undo_action.triggered.connect(self.undo)
        edit_menu.addAction(undo_action)
        
        redo_action = QAction("Redo", self)
        redo_action.setShortcut("Ctrl+Y")
        redo_action.triggered.connect(self.redo)
        edit_menu.addAction(redo_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def create_toolbar(self):
        """Create application toolbar"""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        
        # Open button
        open_btn = QPushButton("Open Image")
        open_btn.clicked.connect(self.open_image)
        toolbar.addWidget(open_btn)
        
        # Save button
        save_btn = QPushButton("Save Image")
        save_btn.clicked.connect(self.save_image)
        toolbar.addWidget(save_btn)
        
        toolbar.addSeparator()
        
        # Undo button
        undo_btn = QPushButton("Undo")
        undo_btn.clicked.connect(self.undo)
        toolbar.addWidget(undo_btn)
        
        # Redo button
        redo_btn = QPushButton("Redo")
        redo_btn.clicked.connect(self.redo)
        toolbar.addWidget(redo_btn)
    
    def create_control_panel(self) -> QWidget:
        """Create the control panel with all editing options"""
        panel = QScrollArea()
        panel.setWidgetResizable(True)
        panel.setMinimumWidth(250)
        
        container = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(8)
        layout.setContentsMargins(8, 8, 8, 8)
        
        # Blur effects group
        blur_group = QGroupBox("Blur Effects (Manual Implementation)")
        blur_layout = QVBoxLayout()
        
        blur_btn = QPushButton("🎨 Apply Blur Effects")
        blur_btn.clicked.connect(self.apply_blur_unified)
        blur_layout.addWidget(blur_btn)
        
        blur_group.setLayout(blur_layout)
        layout.addWidget(blur_group)
        
        # Edge detection group
        edge_group = QGroupBox("Edge Detection")
        edge_layout = QVBoxLayout()
        
        canny_btn = QPushButton("Canny Edge Detection (Manual)")
        canny_btn.clicked.connect(self.apply_canny_edge_manual)
        edge_layout.addWidget(canny_btn)
        
        laplacian_btn = QPushButton("Laplacian Edge (Robust LoG)")
        laplacian_btn.clicked.connect(self.apply_laplacian_edge_manual)
        edge_layout.addWidget(laplacian_btn)
        
        sobel_btn = QPushButton("Sobel Edge Detection")
        sobel_btn.clicked.connect(self.apply_sobel_edge)
        edge_layout.addWidget(sobel_btn)
        
        edge_group.setLayout(edge_layout)
        layout.addWidget(edge_group)
        
        # Custom convolution group
        conv_group = QGroupBox("Custom Convolution")
        conv_layout = QVBoxLayout()
        
        custom_kernel_btn = QPushButton("Apply Custom Kernel")
        custom_kernel_btn.clicked.connect(self.apply_custom_kernel)
        conv_layout.addWidget(custom_kernel_btn)
        
        conv_group.setLayout(conv_layout)
        layout.addWidget(conv_group)
        
        # Segmentation group
        segment_group = QGroupBox("Segmentation")
        segment_layout = QVBoxLayout()
        
        kmeans_btn = QPushButton("K-Means Clustering")
        kmeans_btn.clicked.connect(self.apply_kmeans_segmentation)
        segment_layout.addWidget(kmeans_btn)
        
        fg_bg_btn = QPushButton("Foreground-Background Separation")
        fg_bg_btn.clicked.connect(self.apply_fg_bg_separation)
        segment_layout.addWidget(fg_bg_btn)
        
        segment_group.setLayout(segment_layout)
        layout.addWidget(segment_group)
        
        # Enhancement group
        enhance_group = QGroupBox("Enhancement")
        enhance_layout = QVBoxLayout()
        
        histogram_btn = QPushButton("Histogram Analysis & Equalization")
        histogram_btn.clicked.connect(self.show_histogram_analysis)
        enhance_layout.addWidget(histogram_btn)
        
        histogram_match_btn = QPushButton("Histogram Matching (Functions)")
        histogram_match_btn.clicked.connect(self.show_histogram_matching)
        enhance_layout.addWidget(histogram_match_btn)
        
        contrast_btn = QPushButton("Enhance Contrast")
        contrast_btn.clicked.connect(self.apply_contrast_enhancement)
        enhance_layout.addWidget(contrast_btn)
        
        enhance_group.setLayout(enhance_layout)
        layout.addWidget(enhance_group)
        
        # Transform group
        transform_group = QGroupBox("Transform")
        transform_layout = QVBoxLayout()
        
        rotate_btn = QPushButton("Rotate Image")
        rotate_btn.clicked.connect(self.apply_rotation)
        transform_layout.addWidget(rotate_btn)
        
        crop_btn = QPushButton("Crop Image")
        crop_btn.clicked.connect(self.apply_crop)
        transform_layout.addWidget(crop_btn)
        
        flip_h_btn = QPushButton("Flip Horizontal")
        flip_h_btn.clicked.connect(lambda: self.apply_flip('horizontal'))
        transform_layout.addWidget(flip_h_btn)
        
        flip_v_btn = QPushButton("Flip Vertical")
        flip_v_btn.clicked.connect(lambda: self.apply_flip('vertical'))
        transform_layout.addWidget(flip_v_btn)
        
        transform_group.setLayout(transform_layout)
        layout.addWidget(transform_group)
        
        # Adjustments group
        adjust_group = QGroupBox("Adjustments")
        adjust_layout = QVBoxLayout()
        
        # Brightness slider
        brightness_label = QLabel("Brightness")
        adjust_layout.addWidget(brightness_label)
        
        self.brightness_slider = QSlider(Qt.Horizontal)
        self.brightness_slider.setMinimum(-100)
        self.brightness_slider.setMaximum(100)
        self.brightness_slider.setValue(0)
        self.brightness_slider.setTickPosition(QSlider.TicksBelow)
        self.brightness_slider.setTickInterval(20)
        self.brightness_slider.valueChanged.connect(self.adjust_brightness)
        adjust_layout.addWidget(self.brightness_slider)
        
        # Saturation slider
        saturation_label = QLabel("Saturation")
        adjust_layout.addWidget(saturation_label)
        
        self.saturation_slider = QSlider(Qt.Horizontal)
        self.saturation_slider.setMinimum(0)
        self.saturation_slider.setMaximum(200)
        self.saturation_slider.setValue(100)
        self.saturation_slider.setTickPosition(QSlider.TicksBelow)
        self.saturation_slider.setTickInterval(20)
        self.saturation_slider.valueChanged.connect(self.adjust_saturation)
        adjust_layout.addWidget(self.saturation_slider)
        
        # Apply adjustments button
        apply_btn = QPushButton("Apply Adjustments")
        apply_btn.clicked.connect(self.apply_adjustments)
        apply_btn.setStyleSheet("QPushButton { background-color: #2e7d32; } QPushButton:hover { background-color: #4caf50; }")
        adjust_layout.addWidget(apply_btn)
        
        adjust_group.setLayout(adjust_layout)
        layout.addWidget(adjust_group)
        
        # Reset button
        reset_original_btn = QPushButton("Reset to Original")
        reset_original_btn.clicked.connect(self.reset_to_original)
        reset_original_btn.setStyleSheet("QPushButton { background-color: #d32f2f; } QPushButton:hover { background-color: #f44336; }")
        layout.addWidget(reset_original_btn)
        
        layout.addStretch()
        
        container.setLayout(layout)
        panel.setWidget(container)
        
        return panel
    
    def create_image_display(self):
        """Create the image display area"""
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setObjectName("imageDisplay")
        self.image_label.setText("No image loaded.\nClick 'Open Image' to start editing.")
        self.image_label.setMinimumSize(800, 600)
        
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidget(self.image_label)
        self.scroll_area.setWidgetResizable(True)
    
    def toggle_sidebar(self):
        """Toggle sidebar collapse/expand"""
        if self.sidebar_collapsed:
            # Expand
            self.control_panel_widget.setVisible(True)
            self.collapse_btn.setText("◀")
            self.collapse_btn.setToolTip("Collapse Sidebar")
            self.splitter.setSizes([350, 1050])
            self.sidebar_collapsed = False
        else:
            # Collapse
            self.control_panel_widget.setVisible(False)
            self.collapse_btn.setText("▶")
            self.collapse_btn.setToolTip("Expand Sidebar")
            self.splitter.setSizes([30, 1370])
            self.sidebar_collapsed = True
    
    def apply_modern_theme(self):
        """Apply modern dark theme with responsive font sizes"""
        self.setStyleSheet("""
            /* Main Window */
            QMainWindow {
                background-color: #1e1e1e;
            }
            
            /* Menu Bar - Using pt for responsive font sizing */
            QMenuBar {
                background-color: #2d2d30;
                color: #ffffff;
                border-bottom: 1px solid #3e3e42;
                padding: 0.3em;
                font-size: 7pt;
            }
            QMenuBar::item {
                background-color: transparent;
                padding: 0.4em 0.8em;
                border-radius: 0.3em;
            }
            QMenuBar::item:selected {
                background-color: #3e3e42;
            }
            QMenu {
                background-color: #2d2d30;
                color: #ffffff;
                border: 1px solid #3e3e42;
                padding: 0.3em;
                font-size: 7pt;
            }
            QMenu::item {
                padding: 0.5em 1.5em;
                border-radius: 0.3em;
            }
            QMenu::item:selected {
                background-color: #094771;
            }
            
            /* Status Bar */
            QStatusBar {
                background-color: #007acc;
                color: #ffffff;
                font-weight: bold;
                padding: 0.3em;
                font-size: 7pt;
            }
            
            /* Toolbar */
            QToolBar {
                background-color: #2d2d30;
                border-bottom: 1px solid #3e3e42;
                spacing: 0.4em;
                padding: 0.3em;
            }
            
            /* Scroll Area */
            QScrollArea {
                background-color: #252526;
                border: none;
            }
            QScrollArea > QWidget > QWidget {
                background-color: #252526;
            }
            QScrollArea > QWidget {
                background-color: #252526;
            }
            
            /* Group Box */
            QGroupBox {
                color: #ffffff;
                border: 1px solid #3e3e42;
                border-radius: 0.4em;
                margin-top: 0.8em;
                padding-top: 0.8em;
                font-weight: bold;
                background-color: #2d2d30;
                font-size: 8pt;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 0.8em;
                padding: 0 0.4em;
                color: #4ec9b0;
            }
            
            /* Buttons - Using pt for font size and em for padding */
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #0e639c, stop:1 #094771);
                color: #ffffff;
                border: 1px solid #1177bb;
                border-radius: 0.4em;
                padding: 0.7em 1.2em;
                font-weight: bold;
                font-size: 8pt;
                min-height: 2em;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1177bb, stop:1 #0e639c);
                border: 1px solid #1c97ea;
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #094771, stop:1 #062d4a);
                padding-top: 0.8em;
                padding-left: 1.3em;
            }
            QPushButton:disabled {
                background: #3e3e42;
                color: #656565;
                border: 1px solid #2d2d30;
            }
            
            /* Tool Button (for collapse button) */
            QToolButton {
                background: #2d2d30;
                color: #ffffff;
                border: none;
                font-size: 8pt;
                font-weight: bold;
            }
            QToolButton:hover {
                background: #3e3e42;
            }
            
            /* Labels */
            QLabel {
                color: #cccccc;
                background-color: transparent;
                font-size: 7pt;
            }
            
            /* Image Display Area */
            QLabel#imageDisplay {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1e1e1e, stop:0.5 #252526, stop:1 #1e1e1e);
                border: 2px solid #3e3e42;
                border-radius: 0.5em;
                color: #888888;
                font-size: 8pt;
            }
            
            /* Sliders - Using em for responsive sizing */
            QSlider::groove:horizontal {
                height: 0.4em;
                background: #3e3e42;
                border-radius: 0.2em;
            }
            QSlider::handle:horizontal {
                background: #007acc;
                border: 2px solid #1177bb;
                width: 1em;
                margin: -0.4em 0;
                border-radius: 0.5em;
            }
            QSlider::handle:horizontal:hover {
                background: #1177bb;
                border: 2px solid #1c97ea;
            }
            
            /* Spin Box - Responsive sizing */
            QSpinBox, QDoubleSpinBox {
                background-color: #3e3e42;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 0.3em;
                padding: 0.3em;
                min-height: 1.5em;
                font-size: 7pt;
            }
            QSpinBox:focus, QDoubleSpinBox:focus {
                border: 1px solid #007acc;
            }
            QSpinBox::up-button, QDoubleSpinBox::up-button {
                background-color: #2d2d30;
                border-left: 1px solid #555555;
                border-top-right-radius: 0.3em;
            }
            QSpinBox::down-button, QDoubleSpinBox::down-button {
                background-color: #2d2d30;
                border-left: 1px solid #555555;
                border-bottom-right-radius: 0.3em;
            }
            QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover,
            QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {
                background-color: #3e3e42;
            }
            
            /* Combo Box - Responsive sizing */
            QComboBox {
                background-color: #3e3e42;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 0.3em;
                padding: 0.4em;
                min-height: 1.5em;
                font-size: 7pt;
            }
            QComboBox:hover {
                border: 1px solid #007acc;
            }
            QComboBox::drop-down {
                border: none;
                width: 1.5em;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 0.3em solid transparent;
                border-right: 0.3em solid transparent;
                border-top: 0.4em solid #cccccc;
                margin-right: 0.4em;
            }
            QComboBox QAbstractItemView {
                background-color: #2d2d30;
                color: #ffffff;
                border: 1px solid #555555;
                selection-background-color: #094771;
                outline: none;
                font-size: 7pt;
            }
            
            /* Splitter */
            QSplitter::handle {
                background-color: #3e3e42;
                width: 3px;
            }
            QSplitter::handle:horizontal {
                width: 3px;
            }
            QSplitter::handle:hover {
                background-color: #007acc;
            }
            QSplitter::handle:pressed {
                background-color: #1c97ea;
            }
            
            /* Line Edit - Responsive sizing */
            QLineEdit {
                background-color: #3e3e42;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 0.3em;
                padding: 0.4em;
                font-size: 7pt;
            }
            QLineEdit:focus {
                border: 1px solid #007acc;
            }
            
            /* Text Edit - Responsive sizing */
            QTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: 1px solid #3e3e42;
                border-radius: 0.3em;
                padding: 0.5em;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 7pt;
            }
            QTextEdit:focus {
                border: 1px solid #007acc;
            }
            
            /* Dialog */
            QDialog {
                background-color: #2d2d30;
            }
            
            /* Progress Dialog */
            QProgressDialog {
                background-color: #2d2d30;
                color: #ffffff;
                font-size: 7pt;
            }
            
            /* Message Box */
            QMessageBox {
                background-color: #2d2d30;
            }
            QMessageBox QLabel {
                color: #ffffff;
                font-size: 7pt;
            }
            
            /* Progress Bar */
            QProgressBar {
                border: 1px solid #3e3e42;
                border-radius: 0.3em;
                background-color: #2d2d30;
                text-align: center;
                color: #ffffff;
                font-size: 7pt;
            }
            QProgressBar::chunk {
                background-color: #007acc;
                border-radius: 0.2em;
            }
        """)
    
    def display_image(self):
        """Display the current image"""
        if self.current_image is None:
            return
        
        # Convert BGR to RGB for display
        display_img = cv2.cvtColor(self.current_image, cv2.COLOR_BGR2RGB)
        
        height, width, channel = display_img.shape
        bytes_per_line = 3 * width
        q_image = QImage(display_img.data, width, height, bytes_per_line, 
                        QImage.Format_RGB888)
        
        pixmap = QPixmap.fromImage(q_image)
        
        # Scale to 75% of original size
        scaled_width = int(width * 0.75)
        scaled_height = int(height * 0.75)
        scaled_pixmap = pixmap.scaled(scaled_width, scaled_height, 
                                      Qt.KeepAspectRatio, 
                                      Qt.SmoothTransformation)
        
        self.image_label.setPixmap(scaled_pixmap)
        self.image_label.adjustSize()
        
        # Update status bar
        self.status_bar.showMessage(f"Image: {width}x{height} pixels (displayed at 75%)")
    
    def add_to_history(self):
        """Add current image to history for undo/redo"""
        if self.current_image is None:
            return
        
        # Clear adjustment base image when a permanent change is made
        if hasattr(self, 'adjustment_base_image'):
            self.adjustment_base_image = None
        
        # Remove any forward history
        self.history = self.history[:self.history_index + 1]
        
        # Add current state
        self.history.append(self.current_image.copy())
        
        # Limit history size
        if len(self.history) > self.max_history:
            self.history.pop(0)
        else:
            self.history_index += 1
    
    def open_image(self):
        """Open an image file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Image", "",
            "Image Files (*.jpg *.jpeg *.png *.bmp);;All Files (*)"
        )
        
        if file_path:
            image = cv2.imread(file_path)
            if image is not None:
                # Check if image is too large and offer to resize
                max_dimension = 1920
                height, width = image.shape[:2]
                
                if max(height, width) > max_dimension:
                    scale = max_dimension / max(height, width)
                    new_width = int(width * scale)
                    new_height = int(height * scale)
                    
                    reply = QMessageBox.question(
                        self, 'Large Image Detected',
                        f'Image is {width}x{height}. Resize to {new_width}x{new_height} for better performance?\n\n'
                        f'(Large images can be very slow for manual operations)',
                        QMessageBox.Yes | QMessageBox.No
                    )
                    
                    if reply == QMessageBox.Yes:
                        image = cv2.resize(image, (new_width, new_height), 
                                          interpolation=cv2.INTER_AREA)
                        self.status_bar.showMessage(f"Image resized to {new_width}x{new_height} for performance")
                
                self.current_image = image
                self.original_image = image.copy()
                self.current_file_path = file_path
                
                # Reset history
                self.history = [image.copy()]
                self.history_index = 0
                
                self.display_image()
                self.status_bar.showMessage(f"Loaded: {os.path.basename(file_path)}")
            else:
                QMessageBox.critical(self, "Error", "Failed to load image!")
    
    def save_image(self):
        """Save the current image"""
        if self.current_image is None:
            QMessageBox.warning(self, "Warning", "No image to save!")
            return
        
        if self.current_file_path:
            cv2.imwrite(self.current_file_path, self.current_image)
            self.status_bar.showMessage(f"Saved: {os.path.basename(self.current_file_path)}")
            QMessageBox.information(self, "Success", "Image saved successfully!")
        else:
            self.save_image_as()
    
    def save_image_as(self):
        """Save the current image with a new name"""
        if self.current_image is None:
            QMessageBox.warning(self, "Warning", "No image to save!")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Image As", "",
            "JPEG Image (*.jpg);;PNG Image (*.png);;BMP Image (*.bmp);;All Files (*)"
        )
        
        if file_path:
            # Get quality setting for JPEG
            if file_path.lower().endswith('.jpg') or file_path.lower().endswith('.jpeg'):
                quality, ok = QInputDialog.getInt(
                    self, "JPEG Quality", 
                    "Enter quality (0-100):", 95, 0, 100, 1
                )
                if ok:
                    cv2.imwrite(file_path, self.current_image, 
                               [cv2.IMWRITE_JPEG_QUALITY, quality])
            else:
                cv2.imwrite(file_path, self.current_image)
            
            self.current_file_path = file_path
            self.status_bar.showMessage(f"Saved: {os.path.basename(file_path)}")
            QMessageBox.information(self, "Success", "Image saved successfully!")
    
    def undo(self):
        """Undo last operation"""
        if self.history_index > 0:
            self.history_index -= 1
            self.current_image = self.history[self.history_index].copy()
            self.display_image()
            self.status_bar.showMessage("Undo")
        else:
            self.status_bar.showMessage("Nothing to undo")
    
    def redo(self):
        """Redo last undone operation"""
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.current_image = self.history[self.history_index].copy()
            self.display_image()
            self.status_bar.showMessage("Redo")
        else:
            self.status_bar.showMessage("Nothing to redo")
    
    def apply_blur_unified(self):
        """Apply blur effects with unified dialog and live preview"""
        if self.current_image is None:
            QMessageBox.warning(self, "Warning", "Please load an image first!")
            return
        
        dialog = BlurDialog(self.current_image, self.processor, self)
        if dialog.exec_() == QDialog.Accepted:
            self.add_to_history()
            self.current_image = dialog.get_result_image()
            self.display_image()
            
            blur_type = dialog.blur_type_combo.currentText()
            self.status_bar.showMessage(f"Applied {blur_type}")
    
    def apply_gaussian_blur(self):
        """Apply Gaussian blur with slider (legacy method)"""
        if self.current_image is None:
            return
        
        # Use the new unified dialog
        self.apply_blur_unified()
    
    def apply_average_blur(self):
        """Apply average blur with slider (legacy method)"""
        if self.current_image is None:
            return
        
        # Use the new unified dialog
        self.apply_blur_unified()
    
    def apply_median_blur(self):
        """Apply median blur with slider (legacy method)"""
        if self.current_image is None:
            return
        
        # Use the new unified dialog
        self.apply_blur_unified()
    
    def apply_canny_edge_manual(self):
        """Apply manual Canny edge detection with intermediate steps"""
        if self.current_image is None:
            return
        
        # Get thresholds from dialog with sliders
        dialog = CannyEdgeDialog(self)
        if dialog.exec_() != QDialog.Accepted:
            return
        
        low_threshold, high_threshold = dialog.get_thresholds()
        
        # Show progress
        progress = QProgressDialog("Processing Canny Edge Detection...", None, 0, 0, self)
        progress.setWindowModality(Qt.WindowModal)
        progress.show()
        QApplication.processEvents()
        
        self.add_to_history()
        
        # Apply Canny edge detection
        result, intermediates = self.processor.canny_edge_detection_manual(
            self.current_image, low_threshold, high_threshold
        )
        self.current_image = result
        
        progress.close()
        self.display_image()
        self.status_bar.showMessage("Applied Manual Canny Edge Detection")
        
        # Show intermediate steps dialog
        dialog = CannyIntermediatesDialog(intermediates, self)
        dialog.exec_()
    
    def apply_canny_edge(self):
        """Apply Canny edge detection (legacy method)"""
        self.apply_canny_edge_manual()
    
    def apply_laplacian_edge_manual(self):
        """Apply robust Laplacian edge detection with intermediate steps"""
        if self.current_image is None:
            return
        
        # Get parameters from dialog with sliders
        dialog = LaplacianEdgeDialog(self)
        if dialog.exec_() != QDialog.Accepted:
            return
        
        threshold, kernel_size, blur_kernel = dialog.get_parameters()
        
        # Show progress
        progress = QProgressDialog("Processing Laplacian Edge Detection...", None, 0, 0, self)
        progress.setWindowModality(Qt.WindowModal)
        progress.show()
        QApplication.processEvents()
        
        self.add_to_history()
        
        # Apply Laplacian edge detection
        result, intermediates = self.processor.laplacian_edge_detection_manual(
            self.current_image, threshold, kernel_size, blur_kernel
        )
        self.current_image = result
        
        progress.close()
        self.display_image()
        self.status_bar.showMessage("Applied Laplacian Edge Detection")
        
        # Show intermediate steps dialog
        dialog = LaplacianIntermediatesDialog(intermediates, self)
        dialog.exec_()
    
    def apply_sobel_edge(self):
        """Apply Sobel edge detection"""
        if self.current_image is None:
            return
        
        self.add_to_history()
        self.current_image = self.processor.sobel_edge_detection(self.current_image)
        self.display_image()
        self.status_bar.showMessage("Applied Sobel Edge Detection")
    
    def show_histogram_analysis(self):
        """Show histogram analysis with PDF, CDF, and equalization"""
        if self.current_image is None:
            return
        
        # Open histogram analysis dialog
        dialog = HistogramAnalysisDialog(self.current_image, self)
        if dialog.exec_() == QDialog.Accepted:
            # If user clicked "Apply Equalization"
            if dialog.equalization_applied:
                self.add_to_history()
                
                # Convert to grayscale if needed and apply equalization
                if len(self.current_image.shape) == 3:
                    gray = cv2.cvtColor(self.current_image, cv2.COLOR_BGR2GRAY)
                    equalized = cv2.equalizeHist(gray)
                    # Convert back to BGR for display
                    self.current_image = cv2.cvtColor(equalized, cv2.COLOR_GRAY2BGR)
                else:
                    self.current_image = cv2.equalizeHist(self.current_image)
                
                self.display_image()
                self.status_bar.showMessage("Applied Histogram Equalization")
    
    def show_histogram_matching(self):
        """Show histogram matching dialog with predefined transformation functions"""
        if self.current_image is None:
            self.status_bar.showMessage("No image loaded!")
            return
        
        # Convert to grayscale if needed
        if len(self.current_image.shape) == 3:
            gray_image = cv2.cvtColor(self.current_image, cv2.COLOR_BGR2GRAY)
        else:
            gray_image = self.current_image.copy()
        
        dialog = HistogramMatchingDialog(gray_image, self)
        if dialog.exec_() == QDialog.Accepted:
            self.add_to_history()
            # Convert matched grayscale image back to BGR
            self.current_image = cv2.cvtColor(dialog.matched_image, cv2.COLOR_GRAY2BGR)
            self.display_image()
            self.status_bar.showMessage("Applied Histogram Matching")
    
    def apply_contrast_enhancement(self):
        """Apply contrast enhancement"""
        if self.current_image is None:
            return
        
        self.add_to_history()
        self.current_image = self.processor.enhance_contrast(self.current_image)
        self.display_image()
        self.status_bar.showMessage("Applied Contrast Enhancement")
    
    def apply_sharpen(self):
        """Apply sharpening"""
        if self.current_image is None:
            return
        
        self.add_to_history()
        self.current_image = self.processor.sharpen_image(self.current_image)
        self.display_image()
        self.status_bar.showMessage("Applied Sharpening")
    
    def apply_rotation(self):
        """Apply rotation"""
        if self.current_image is None:
            return
        
        # Get angle from dialog with slider and live preview
        dialog = RotationDialog(self.current_image, self)
        if dialog.exec_() != QDialog.Accepted:
            self.display_image()  # Restore original view
            return
        
        angle = dialog.get_angle()
        self.add_to_history()
        self.current_image = self.processor.rotate_image(self.current_image, angle)
        self.display_image()
        self.status_bar.showMessage(f"Rotated by {angle}°")
    
    def apply_crop(self):
        """Apply cropping with interactive selection"""
        if self.current_image is None:
            return
        
        dialog = CropDialog(self.current_image, self)
        if dialog.exec_() == QDialog.Accepted:
            x, y, w, h = dialog.get_crop_rect()
            if w > 0 and h > 0:
                self.add_to_history()
                self.current_image = self.processor.crop_image(self.current_image, x, y, w, h)
                self.display_image()
                self.status_bar.showMessage("Image Cropped")
    
    def apply_flip(self, direction: str):
        """Apply flip"""
        if self.current_image is None:
            return
        
        self.add_to_history()
        self.current_image = self.processor.flip_image(self.current_image, direction)
        self.display_image()
        self.status_bar.showMessage(f"Flipped {direction}")
    
    def adjust_brightness(self):
        """Adjust brightness using slider"""
        if self.current_image is None:
            return
        
        # Get the base image (from history if available, otherwise use current)
        if hasattr(self, 'adjustment_base_image') and self.adjustment_base_image is not None:
            base_image = self.adjustment_base_image
        else:
            # Store current image as base for adjustments
            self.adjustment_base_image = self.current_image.copy()
            base_image = self.adjustment_base_image
        
        value = self.brightness_slider.value()
        temp_image = self.processor.adjust_brightness(base_image.copy(), value)
        
        # Apply saturation on top
        sat_value = self.saturation_slider.value() / 100.0
        self.current_image = self.processor.adjust_saturation(temp_image, sat_value)
        
        self.display_image()
    
    def adjust_saturation(self):
        """Adjust saturation using slider"""
        if self.current_image is None:
            return
        
        # Get the base image (from history if available, otherwise use current)
        if hasattr(self, 'adjustment_base_image') and self.adjustment_base_image is not None:
            base_image = self.adjustment_base_image
        else:
            # Store current image as base for adjustments
            self.adjustment_base_image = self.current_image.copy()
            base_image = self.adjustment_base_image
        
        # Apply brightness first
        bright_value = self.brightness_slider.value()
        temp_image = self.processor.adjust_brightness(base_image.copy(), bright_value)
        
        # Then apply saturation
        sat_value = self.saturation_slider.value() / 100.0
        self.current_image = self.processor.adjust_saturation(temp_image, sat_value)
        
        self.display_image()
    
    def apply_adjustments(self):
        """Apply current brightness/saturation adjustments permanently"""
        if not hasattr(self, 'adjustment_base_image') or self.adjustment_base_image is None:
            # No adjustments to apply
            return
        
        # Current_image already has the adjustments applied
        # Just add to history to make it permanent
        self.add_to_history()
        
        # Reset sliders to neutral
        self.brightness_slider.setValue(0)
        self.saturation_slider.setValue(100)
        
        self.status_bar.showMessage("Adjustments Applied")
    
    def reset_adjustments(self):
        """Reset brightness and saturation adjustments"""
        if not hasattr(self, 'adjustment_base_image') or self.adjustment_base_image is None:
            return
        
        self.brightness_slider.setValue(0)
        self.saturation_slider.setValue(100)
        self.add_to_history()
        self.current_image = self.adjustment_base_image.copy()
        self.adjustment_base_image = None  # Clear the base image
        self.display_image()
        self.status_bar.showMessage("Adjustments Reset")
    
    def apply_fg_bg_separation(self):
        """Apply foreground-background separation using GrabCut with interactive rectangle"""
        if self.current_image is None:
            return
        
        # Open dialog for user to draw rectangle
        dialog = GrabCutDialog(self.current_image, self)
        if dialog.exec_() == QDialog.Accepted:
            x, y, w, h = dialog.get_selection_rect()
            iterations = dialog.get_iterations()
            
            # Check if rectangle is valid
            if w <= 0 or h <= 0:
                QMessageBox.warning(
                    self, "Invalid Selection", 
                    "Please draw a rectangle around the subject (human/object) you want to segment."
                )
                return
            
            # Show progress
            progress = QProgressDialog(
                f"Processing GrabCut segmentation with {iterations} iterations...\n"
                "This may take 10-30 seconds depending on image size...", 
                None, 0, 0, self
            )
            progress.setWindowModality(Qt.WindowModal)
            progress.show()
            QApplication.processEvents()
            
            self.add_to_history()
            
            # Apply GrabCut with user-defined rectangle
            try:
                self.current_image = self.processor.foreground_background_separation(
                    self.current_image, rect=(x, y, w, h), iterations=iterations
                )
                progress.close()
                self.display_image()
                self.status_bar.showMessage("Applied GrabCut Foreground-Background Separation")
                
                QMessageBox.information(
                    self, "Segmentation Complete",
                    "Subject has been separated from background!\n"
                    "Background is now white. You can save the result."
                )
            except Exception as e:
                progress.close()
                QMessageBox.critical(
                    self, "Error", 
                    f"GrabCut segmentation failed: {str(e)}\n\n"
                    "Try drawing a larger rectangle around the subject."
                )
    
    def reset_to_original(self):
        """Reset to original image"""
        if self.original_image is None:
            return
        
        self.add_to_history()
        self.current_image = self.original_image.copy()
        self.brightness_slider.setValue(0)
        self.saturation_slider.setValue(100)
        self.display_image()
        self.status_bar.showMessage("Reset to Original Image")
    
    def apply_custom_kernel(self):
        """Apply custom convolution kernel with interactive grid editor and live preview"""
        if self.current_image is None:
            return
        
        # Open interactive kernel dialog with live preview
        dialog = CustomKernelDialog(self.current_image, self)
        if dialog.exec_() == QDialog.Accepted:
            try:
                # Check if animation was completed and get result
                if dialog.has_animation_result():
                    result_image = dialog.get_result_image()
                    self.add_to_history()
                    self.current_image = result_image
                    self.display_image()
                    kernel = dialog.get_kernel()
                    self.status_bar.showMessage(
                        f"Applied custom kernel ({kernel.shape[0]}x{kernel.shape[1]}) - Animation Result"
                    )
                else:
                    # No animation or animation didn't complete, apply kernel normally
                    kernel = dialog.get_kernel()
                    
                    # Check if kernel is all zeros
                    if np.all(kernel == 0):
                        QMessageBox.warning(
                            self, "Invalid Kernel",
                            "Kernel is all zeros. Please enter at least one non-zero value."
                        )
                        return
                    
                    # Show progress
                    progress = QProgressDialog("Applying custom kernel convolution...", None, 0, 0, self)
                    progress.setWindowModality(Qt.WindowModal)
                    progress.show()
                    QApplication.processEvents()
                    
                    self.add_to_history()
                    self.current_image = self.processor.apply_custom_kernel(
                        self.current_image, kernel
                    )
                    
                    progress.close()
                    self.display_image()
                    self.status_bar.showMessage(
                        f"Applied custom kernel ({kernel.shape[0]}x{kernel.shape[1]})"
                    )
            except ValueError as e:
                QMessageBox.critical(self, "Error", str(e))
    
    def apply_kmeans_segmentation(self):
        """Apply K-means segmentation"""
        if self.current_image is None:
            return
        
        # Get K value from dialog with slider
        dialog = KMeansDialog(self)
        if dialog.exec_() != QDialog.Accepted:
            return
        
        k = dialog.get_k()
        
        # Show progress
        progress = QProgressDialog(f"Processing K-means with {k} clusters...\nThis may take a moment...", 
                                  None, 0, 0, self)
        progress.setWindowModality(Qt.WindowModal)
        progress.show()
        QApplication.processEvents()
        
        self.add_to_history()
        self.current_image = self.processor.kmeans_segmentation(self.current_image, k)
        
        progress.close()
        self.display_image()
        self.status_bar.showMessage(f"Applied K-Means Segmentation (k={k})")
    
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self, "About Photo Editor",
            "<h2>Photo Editor</h2>"
            "<p>Version 2.0</p>"
            "<p>A comprehensive desktop photo editing application.</p>"
            "<p><b>Features:</b></p>"
            "<ul>"
            "<li>Manual blur effects (Gaussian, Average, Median)</li>"
            "<li>Manual Canny edge detection with intermediate steps</li>"
            "<li>Custom kernel convolution</li>"
            "<li>K-means clustering segmentation</li>"
            "<li>Contrast and sharpness enhancement</li>"
            "<li>Image transformations</li>"
            "<li>Color adjustments</li>"
            "<li>Special effects</li>"
            "<li>Undo/Redo functionality</li>"
            "</ul>"
            "<p><b>Technologies:</b> Python, PyQt5, OpenCV, NumPy</p>"
            "<p>Created for educational purposes.</p>"
        )


def main():
    """Main application entry point with responsive DPI support"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Modern look
    
    # Set base font that scales with DPI (10pt will scale automatically)
    base_font = QFont()
    base_font.setPointSize(6)
    base_font.setFamily("Segoe UI")
    app.setFont(base_font)
    
    window = PhotoEditorApp()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
