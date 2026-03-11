# Modern UI Theme and Components
# Add this code to your PhotoEditorApp class

MODERN_DARK_THEME = """
/* Main Window */
QMainWindow {
    background-color: #1e1e1e;
}

/* Menu Bar */
QMenuBar {
    background-color: #2d2d30;
    color: #ffffff;
    border-bottom: 1px solid #3e3e42;
    padding: 4px;
}
QMenuBar::item {
    background-color: transparent;
    padding: 6px 12px;
    border-radius: 4px;
}
QMenuBar::item:selected {
    background-color: #3e3e42;
}
QMenu {
    background-color: #2d2d30;
    color: #ffffff;
    border: 1px solid #3e3e42;
    padding: 4px;
}
QMenu::item {
    padding: 6px 24px;
    border-radius: 4px;
}
QMenu::item:selected {
    background-color: #094771;
}

/* Status Bar */
QStatusBar {
    background-color: #007acc;
    color: #ffffff;
    font-weight: bold;
    padding: 4px;
}

/* Scroll Area */
QScrollArea {
    background-color: #252526;
    border: none;
}

/* Group Box */
QGroupBox {
    color: #ffffff;
    border: 1px solid #3e3e42;
    border-radius: 6px;
    margin-top: 12px;
    padding-top: 12px;
    font-weight: bold;
    background-color: #2d2d30;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
    color: #4ec9b0;
}

/* Buttons */
QPushButton {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #0e639c, stop:1 #094771);
    color: #ffffff;
    border: 1px solid #1177bb;
    border-radius: 5px;
    padding: 8px 16px;
    font-weight: bold;
    font-size: 5px;
    min-height: 24px;
}
QPushButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #1177bb, stop:1 #0e639c);
    border: 1px solid #1c97ea;
}
QPushButton:pressed {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #094771, stop:1 #062d4a);
    padding-top: 10px;
    padding-left: 18px;
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
    font-size: 14px;
    font-weight: bold;
}
QToolButton:hover {
    background: #3e3e42;
}

/* Labels */
QLabel {
    color: #cccccc;
    background-color: transparent;
}

/* Image Display Area */
QLabel#imageDisplay {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #1e1e1e, stop:0.5 #252526, stop:1 #1e1e1e);
    border: 2px solid #3e3e42;
    border-radius: 8px;
}

/* Sliders */
QSlider::groove:horizontal {
    height: 6px;
    background: #3e3e42;
    border-radius: 3px;
}
QSlider::handle:horizontal {
    background: #007acc;
    border: 2px solid #1177bb;
    width: 16px;
    margin: -6px 0;
    border-radius: 8px;
}
QSlider::handle:horizontal:hover {
    background: #1177bb;
    border: 2px solid #1c97ea;
}

/* Spin Box */
QSpinBox, QDoubleSpinBox {
    background-color: #3e3e42;
    color: #ffffff;
    border: 1px solid #555555;
    border-radius: 4px;
    padding: 4px;
    min-height: 20px;
}
QSpinBox:focus, QDoubleSpinBox:focus {
    border: 1px solid #007acc;
}
QSpinBox::up-button, QDoubleSpinBox::up-button {
    background-color: #2d2d30;
    border-left: 1px solid #555555;
    border-top-right-radius: 4px;
}
QSpinBox::down-button, QDoubleSpinBox::down-button {
    background-color: #2d2d30;
    border-left: 1px solid #555555;
    border-bottom-right-radius: 4px;
}
QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover,
QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {
    background-color: #3e3e42;
}

/* Combo Box */
QComboBox {
    background-color: #3e3e42;
    color: #ffffff;
    border: 1px solid #555555;
    border-radius: 4px;
    padding: 6px;
    min-height: 20px;
}
QComboBox:hover {
    border: 1px solid #007acc;
}
QComboBox::drop-down {
    border: none;
    width: 20px;
}
QComboBox::down-arrow {
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 6px solid #cccccc;
    margin-right: 6px;
}
QComboBox QAbstractItemView {
    background-color: #2d2d30;
    color: #ffffff;
    border: 1px solid #555555;
    selection-background-color: #094771;
    outline: none;
}

/* Splitter */
QSplitter::handle {
    background-color: #3e3e42;
}
QSplitter::handle:hover {
    background-color: #007acc;
}

/* Line Edit */
QLineEdit {
    background-color: #3e3e42;
    color: #ffffff;
    border: 1px solid #555555;
    border-radius: 4px;
    padding: 6px;
}
QLineEdit:focus {
    border: 1px solid #007acc;
}

/* Text Edit */
QTextEdit {
    background-color: #1e1e1e;
    color: #d4d4d4;
    border: 1px solid #3e3e42;
    border-radius: 4px;
    padding: 8px;
    font-family: 'Consolas', 'Courier New', monospace;
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
}

/* Message Box */
QMessageBox {
    background-color: #2d2d30;
}
QMessageBox QLabel {
    color: #ffffff;
}

/* Toolbar */
QToolBar {
    background-color: #2d2d30;
    border-bottom: 1px solid #3e3e42;
    spacing: 6px;
    padding: 4px;
}
"""

def toggle_sidebar(self):
    """Toggle sidebar collapse/expand"""
    if self.sidebar_collapsed:
        # Expand
        self.control_panel.setVisible(True)
        self.collapse_btn.setText("◀")
        self.collapse_btn.setToolTip("Collapse Sidebar")
        self.splitter.setSizes([300, 1100])
        self.sidebar_collapsed = False
    else:
        # Collapse
        self.control_panel.setVisible(False)
        self.collapse_btn.setText("▶")
        self.collapse_btn.setToolTip("Expand Sidebar")
        self.splitter.setSizes([30, 1370])
        self.sidebar_collapsed = True
