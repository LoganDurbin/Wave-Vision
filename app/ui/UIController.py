from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                                QHBoxLayout, QLabel, QComboBox, QPushButton,
                                QTextEdit, QGroupBox, QDoubleSpinBox, QInputDialog,
                                QMessageBox, QFrame)
from PySide6.QtGui import QFont, QPainter, QColor, QPen
from PySide6.QtCore import Qt
import cv2
import sys

class HandVisualizationWidget(QFrame):
    EDGE_THRESHOLD = 10  # pixels threshold for edge detection
    
    def __init__(self, parent=None, on_bounds_changed=None):  # pragma: no cover
        super().__init__(parent)
        self.setMinimumSize(200, 150)
        self.setMaximumSize(200, 150)
        self.setStyleSheet("background-color: black; border: 1px solid gray;")
        self.landmarks = None
        self.area_bounds = (0.0, 0.0, 1.0, 1.0)  # (top_left_x, top_left_y, bottom_right_x, bottom_right_y)
        self.on_bounds_changed = on_bounds_changed

        self.dragging = None  # None, 'left', 'right', 'top', 'bottom'
        self.setMouseTracking(True)
    
    def set_landmarks(self, landmarks: list[tuple[float, float]] | None):  # pragma: no cover
        self.landmarks = landmarks
        self.update()
    
    def set_area_bounds(self, bounds: tuple[float, float, float, float]):  # pragma: no cover
        self.area_bounds = bounds
        self.update()
    
    def _get_rect_coords(self):  # pragma: no cover
        width = self.width()
        height = self.height()
        # Mirror x coordinate to match camera view
        x1 = int((1 - self.area_bounds[2]) * width)  # bottom_right_x becomes left
        y1 = int(self.area_bounds[1] * height)        # top_left_y
        x2 = int((1 - self.area_bounds[0]) * width)  # top_left_x becomes right
        y2 = int(self.area_bounds[3] * height)        # bottom_right_y
        return x1, y1, x2, y2
    
    def _detect_edge(self, pos):  # pragma: no cover
        x, y = pos.x(), pos.y()
        x1, y1, x2, y2 = self._get_rect_coords()
        threshold = self.EDGE_THRESHOLD

        in_v_range = y1 - threshold <= y <= y2 + threshold
        in_h_range = x1 - threshold <= x <= x2 + threshold

        near_left = abs(x - x1) <= threshold and in_v_range
        near_right = abs(x - x2) <= threshold and in_v_range
        near_top = abs(y - y1) <= threshold and in_h_range
        near_bottom = abs(y - y2) <= threshold and in_h_range
        
        if near_left:
            return 'left'
        elif near_right:
            return 'right'
        elif near_top:
            return 'top'
        elif near_bottom:
            return 'bottom'
        return None
    
    def mousePressEvent(self, event):  # pragma: no cover
        if event.button() == Qt.LeftButton:
            edge = self._detect_edge(event.pos())
            if edge:
                self.dragging = edge
        super().mousePressEvent(event)
    
    def mouseReleaseEvent(self, event):  # pragma: no cover
        if event.button() == Qt.LeftButton and self.dragging:
            self.dragging = None
            # Notify that bounds changed
            if self.on_bounds_changed:
                self.on_bounds_changed(self.area_bounds)
        super().mouseReleaseEvent(event)
    
    def mouseMoveEvent(self, event):  # pragma: no cover
        pos = event.pos()
        width = self.width()
        height = self.height()
        
        if self.dragging:
            norm_x = max(0.0, min(1.0, pos.x() / width))
            norm_y = max(0.0, min(1.0, pos.y() / height))

            actual_x = 1 - norm_x
            
            top_left_x, top_left_y, bottom_right_x, bottom_right_y = self.area_bounds
            
            min_size = 0.1  # Minimum area size
            
            if self.dragging == 'left':
                # Left edge in widget = bottom_right_x in actual coords
                new_val = max(top_left_x + min_size, min(1.0, actual_x))
                bottom_right_x = new_val
            elif self.dragging == 'right':
                # Right edge in widget = top_left_x in actual coords
                new_val = max(0.0, min(bottom_right_x - min_size, actual_x))
                top_left_x = new_val
            elif self.dragging == 'top':
                new_val = max(0.0, min(bottom_right_y - min_size, norm_y))
                top_left_y = new_val
            elif self.dragging == 'bottom':
                new_val = max(top_left_y + min_size, min(1.0, norm_y))
                bottom_right_y = new_val
            
            self.area_bounds = (top_left_x, top_left_y, bottom_right_x, bottom_right_y)
            self.update()
        else:
            edge = self._detect_edge(pos)
            if edge in ('left', 'right'):
                self.setCursor(Qt.SizeHorCursor)
            elif edge in ('top', 'bottom'):
                self.setCursor(Qt.SizeVerCursor)
            else:
                self.setCursor(Qt.ArrowCursor)
        
        super().mouseMoveEvent(event)
    
    def paintEvent(self, event):  # pragma: no cover
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        width = self.width()
        height = self.height()
        
        x1, y1, x2, y2 = self._get_rect_coords()

        pen = QPen(QColor(255, 255, 255))
        pen.setWidth(2)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        
        painter.drawRect(x1, y1, x2 - x1, y2 - y1)

        handle_size = 6
        painter.setBrush(QColor(255, 255, 255))
        mid_y = (y1 + y2) // 2
        mid_x = (x1 + x2) // 2
        # Left handle
        painter.drawRect(x1 - handle_size//2, mid_y - handle_size//2, handle_size, handle_size)
        # Right handle
        painter.drawRect(x2 - handle_size//2, mid_y - handle_size//2, handle_size, handle_size)
        # Top handle
        painter.drawRect(mid_x - handle_size//2, y1 - handle_size//2, handle_size, handle_size)
        # Bottom handle
        painter.drawRect(mid_x - handle_size//2, y2 - handle_size//2, handle_size, handle_size)

        if self.landmarks:
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor(255, 0, 0))
            
            for lm_x, lm_y in self.landmarks:
                x = int((1 - lm_x) * width)
                y = int(lm_y * height)
                painter.drawEllipse(x - 3, y - 3, 6, 6)
        
        painter.end()


class UIController:
    def __init__(self, app):  # pragma: no cover
        self.app_controller = app
        self.qt_app = QApplication.instance()
        if self.qt_app is None:
            self.qt_app = QApplication(sys.argv)

        self.is_tracking = False
        self.available_cameras = self._detect_cameras()

        self.window = QMainWindow()
        self.window.setWindowTitle("Wave Vision")
        self.window.setFixedSize(650, 750)

        self._setup_ui()

    def _detect_cameras(self) -> list[int]:  # pragma: no cover
        available = []
        for i in range(10):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                available.append(i)
                cap.release()
        return available if available else [0]

    def _setup_ui(self):  # pragma: no cover
        central_widget = QWidget()
        self.window.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Top bar with Help button
        top_bar = QHBoxLayout()
        top_bar.addStretch()
        self.help_button = QPushButton("Help")
        self.help_button.clicked.connect(self._on_help_clicked)
        top_bar.addWidget(self.help_button)
        main_layout.addLayout(top_bar)

        profile_group = QGroupBox("Profile")
        profile_layout = QVBoxLayout()

        profile_selector_row = QHBoxLayout()
        profile_label = QLabel("Profile:")
        self.profile_combo = QComboBox()
        self.profile_combo.currentIndexChanged.connect(self._on_profile_selected)
        profile_selector_row.addWidget(profile_label)
        profile_selector_row.addWidget(self.profile_combo)
        profile_selector_row.addStretch()

        profile_buttons_row = QHBoxLayout()
        self.new_profile_button = QPushButton("New")
        self.new_profile_button.clicked.connect(self._on_new_profile)
        self.save_profile_button = QPushButton("Save")
        self.save_profile_button.clicked.connect(self._on_save_profile)
        self.rename_profile_button = QPushButton("Rename")
        self.rename_profile_button.clicked.connect(self._on_rename_profile)
        self.delete_profile_button = QPushButton("Delete")
        self.delete_profile_button.clicked.connect(self._on_delete_profile)

        profile_buttons_row.addWidget(self.new_profile_button)
        profile_buttons_row.addWidget(self.save_profile_button)
        profile_buttons_row.addWidget(self.rename_profile_button)
        profile_buttons_row.addWidget(self.delete_profile_button)
        profile_buttons_row.addStretch()

        profile_layout.addLayout(profile_selector_row)
        profile_layout.addLayout(profile_buttons_row)
        profile_group.setLayout(profile_layout)
        main_layout.addWidget(profile_group)

        settings_group = QGroupBox("Settings")
        settings_layout = QVBoxLayout()

        camera_row = QHBoxLayout()
        camera_label = QLabel("Camera Index:")
        self.camera_combo = QComboBox()
        for cam in self.available_cameras:
            self.camera_combo.addItem(str(cam), cam)
        self.camera_combo.currentIndexChanged.connect(self._on_camera_selected)
        camera_row.addWidget(camera_label)
        camera_row.addWidget(self.camera_combo)
        camera_row.addStretch()

        sensitivity_row = QHBoxLayout()
        sensitivity_label = QLabel("Sensitivity:")
        self.sensitivity_spin = QDoubleSpinBox()
        self.sensitivity_spin.setRange(0.1, 5.0)
        self.sensitivity_spin.setSingleStep(0.1)
        self.sensitivity_spin.setValue(1.0)
        self.sensitivity_spin.valueChanged.connect(self._on_sensitivity_changed)
        sensitivity_row.addWidget(sensitivity_label)
        sensitivity_row.addWidget(self.sensitivity_spin)
        sensitivity_row.addStretch()

        smoothing_row = QHBoxLayout()
        smoothing_label = QLabel("Smoothing:")
        self.smoothing_spin = QDoubleSpinBox()
        self.smoothing_spin.setRange(0.0, 1.0)
        self.smoothing_spin.setSingleStep(0.05)
        self.smoothing_spin.setValue(0.3)
        self.smoothing_spin.valueChanged.connect(self._on_smoothing_changed)
        smoothing_row.addWidget(smoothing_label)
        smoothing_row.addWidget(self.smoothing_spin)
        smoothing_row.addStretch()

        pinch_row = QHBoxLayout()
        pinch_label = QLabel("Pinch Threshold:")
        self.pinch_spin = QDoubleSpinBox()
        self.pinch_spin.setRange(0.01, 0.2)
        self.pinch_spin.setSingleStep(0.01)
        self.pinch_spin.setValue(0.05)
        self.pinch_spin.valueChanged.connect(self._on_pinch_changed)
        pinch_row.addWidget(pinch_label)
        pinch_row.addWidget(self.pinch_spin)
        pinch_row.addStretch()

        settings_layout.addLayout(camera_row)
        settings_layout.addLayout(sensitivity_row)
        settings_layout.addLayout(smoothing_row)
        settings_layout.addLayout(pinch_row)
        settings_group.setLayout(settings_layout)
        main_layout.addWidget(settings_group)

        controls_group = QGroupBox("Tracking Controls")
        controls_layout = QHBoxLayout()

        self.start_button = QPushButton("Start Tracking")
        self.start_button.setMinimumWidth(150)
        self.start_button.clicked.connect(self._on_start_clicked)

        self.stop_button = QPushButton("Stop Tracking")
        self.stop_button.setMinimumWidth(150)
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self._on_stop_clicked)

        controls_layout.addWidget(self.start_button)
        controls_layout.addWidget(self.stop_button)
        controls_layout.addStretch()
        controls_group.setLayout(controls_layout)
        main_layout.addWidget(controls_group)

        # Area Mapping group with visualization
        area_group = QGroupBox("Area Mapping (drag edges to resize)")
        area_layout = QHBoxLayout()
        
        # Visualization widget on the left with drag-to-resize
        self.hand_viz = HandVisualizationWidget(on_bounds_changed=self._on_area_bounds_changed)
        area_layout.addWidget(self.hand_viz)
        
        # Buttons on the right
        area_buttons_layout = QVBoxLayout()
        
        self.reset_area_button = QPushButton("Reset Area")
        self.reset_area_button.clicked.connect(self._on_reset_area)
        
        area_buttons_layout.addWidget(self.reset_area_button)
        area_buttons_layout.addStretch()
        
        area_layout.addLayout(area_buttons_layout)
        area_group.setLayout(area_layout)
        main_layout.addWidget(area_group)

        status_group = QGroupBox("Status")
        status_layout = QVBoxLayout()

        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)
        self.status_text.setMinimumHeight(150)
        self.status_text.setFont(QFont("Courier", 10))

        status_layout.addWidget(self.status_text)
        status_group.setLayout(status_layout)
        main_layout.addWidget(status_group)

        main_layout.addStretch()

        self.update_status("Ready. Select camera and click 'Start Tracking'.")

    def _on_help_clicked(self):  # pragma: no cover
        help_text = (
            "How to use Wave Vision:\n\n"
            "1. Select a camera index under Settings.\n"
            "2. Adjust Sensitivity and Smoothing to your preference.\n"
            "3. Set the Pinch Threshold for click detection.\n"
            "4. Use Area Mapping to resize the active tracking area.\n"
            "5. Click 'Start Tracking' to begin. Move your hand to control the cursor.\n"
            "6. Pinch (move thumb to index) to perform a click.\n"
            "7. Click 'Stop Tracking' to end.\n\n"
            "Profiles:\n"
            "• Create, Save, Rename, and Delete profiles to store settings for later use.\n"
        )
        QMessageBox.information(self.window, "Wave Vision Help", help_text)

    def _on_profile_selected(self):  # pragma: no cover
        profile_name = self.profile_combo.currentText()
        if profile_name:
            self.app_controller.load_profile(profile_name)

    def _on_camera_selected(self):  # pragma: no cover
        camera_index = self.camera_combo.currentData()
        if not self.is_tracking:
            self.app_controller.update_camera(camera_index)

    def _on_sensitivity_changed(self, value: float):  # pragma: no cover
        self.app_controller.update_sensitivity(value)

    def _on_smoothing_changed(self, value: float):  # pragma: no cover
        self.app_controller.update_smoothing(value)

    def _on_pinch_changed(self, value: float):  # pragma: no cover
        self.app_controller.update_pinch_threshold(value)

    def _on_new_profile(self):  # pragma: no cover
        name, ok = QInputDialog.getText(self.window, "New Profile", "Profile name:")
        if ok and name:
            success = self.app_controller.create_profile(name)
            if not success:
                QMessageBox.warning(self.window, "Error", f"Profile '{name}' already exists.")

    def _on_save_profile(self):  # pragma: no cover
        self.app_controller.save_current_profile()
        self.update_status("Profile saved.")

    def _on_rename_profile(self):  # pragma: no cover
        current_name = self.profile_combo.currentText()
        name, ok = QInputDialog.getText(self.window, "Rename Profile", "New profile name:", text=current_name)
        if ok and name and name != current_name:
            success = self.app_controller.rename_profile(current_name, name)
            if not success:
                QMessageBox.warning(self.window, "Error", f"Profile '{name}' already exists.")

    def _on_delete_profile(self):  # pragma: no cover
        current_name = self.profile_combo.currentText()
        reply = QMessageBox.question(
            self.window,
            "Delete Profile",
            f"Are you sure you want to delete profile '{current_name}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            success = self.app_controller.delete_profile(current_name)
            if not success:
                QMessageBox.warning(self.window, "Error", "Cannot delete the last profile.")

    def _on_start_clicked(self):  # pragma: no cover
        self.app_controller.start_tracking()

    def _on_stop_clicked(self):  # pragma: no cover
        self.app_controller.stop_tracking()

    def _on_area_bounds_changed(self, bounds: tuple[float, float, float, float]):  # pragma: no cover
        """Called when the user drags the area bounds in the visualization widget."""
        self.app_controller.update_area_bounds(bounds)

    def _on_reset_area(self):  # pragma: no cover
        self.app_controller.reset_area()
        self._update_area_visualization()

    def _update_area_visualization(self):  # pragma: no cover
        bounds = self.app_controller.get_area_bounds()
        self.hand_viz.set_area_bounds(bounds)

    def update_hand_visualization(self, landmarks: list[tuple[float, float]] | None):  # pragma: no cover
        self.hand_viz.set_landmarks(landmarks)

    def load_profiles(self, profiles: list[str], current_profile: str):  # pragma: no cover
        self.profile_combo.clear()
        for profile in profiles:
            self.profile_combo.addItem(profile)
        index = self.profile_combo.findText(current_profile)
        if index >= 0:
            self.profile_combo.setCurrentIndex(index)

    def update_settings_ui(self, camera_index: int, sensitivity: float, smoothing: float, pinch_threshold: float):  # pragma: no cover
        for i in range(self.camera_combo.count()):
            if self.camera_combo.itemData(i) == camera_index:
                self.camera_combo.setCurrentIndex(i)
                break
        self.sensitivity_spin.setValue(sensitivity)
        self.smoothing_spin.setValue(smoothing)
        self.pinch_spin.setValue(pinch_threshold)

    def get_selected_camera(self) -> int:  # pragma: no cover
        return self.camera_combo.currentData()

    def set_tracking_state(self, is_tracking: bool):  # pragma: no cover
        self.is_tracking = is_tracking
        self.start_button.setEnabled(not is_tracking)
        self.stop_button.setEnabled(is_tracking)
        self.camera_combo.setEnabled(not is_tracking)

        if is_tracking:
            self.update_status("Tracking started. Hand tracking is active.")
        else:
            self.update_status("Tracking stopped.")

    def update_status(self, message: str):  # pragma: no cover
        self.status_text.append(message)
        self.status_text.verticalScrollBar().setValue(
            self.status_text.verticalScrollBar().maximum()
        )

    def show(self):  # pragma: no cover
        self.window.show()

    def update(self):  # pragma: no cover
        self.qt_app.processEvents()

    def is_closed(self) -> bool:  # pragma: no cover
        return not self.window.isVisible()

    def close(self):  # pragma: no cover
        self.window.close()
