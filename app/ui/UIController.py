from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                                QHBoxLayout, QLabel, QComboBox, QPushButton,
                                QTextEdit, QGroupBox)
from PySide6.QtGui import QFont
import cv2
import sys


class UIController:
    def __init__(self, app):
        self.app_controller = app
        self.qt_app = QApplication.instance()
        if self.qt_app is None:
            self.qt_app = QApplication(sys.argv)

        self.is_tracking = False
        self.available_cameras = self._detect_cameras()

        self.window = QMainWindow()
        self.window.setWindowTitle("Wave Vision")
        self.window.setFixedSize(500, 400)

        self._setup_ui()

    def _detect_cameras(self) -> list[int]:
        available = []
        for i in range(10):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                available.append(i)
                cap.release()
        return available if available else [0]

    def _setup_ui(self):
        central_widget = QWidget()
        self.window.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        camera_group = QGroupBox("Camera Selection")
        camera_layout = QHBoxLayout()

        camera_label = QLabel("Camera Index:")
        self.camera_combo = QComboBox()
        for cam in self.available_cameras:
            self.camera_combo.addItem(str(cam), cam)
        self.camera_combo.currentIndexChanged.connect(self._on_camera_selected)

        camera_layout.addWidget(camera_label)
        camera_layout.addWidget(self.camera_combo)
        camera_layout.addStretch()
        camera_group.setLayout(camera_layout)
        main_layout.addWidget(camera_group)

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

    def _on_camera_selected(self):
        camera_index = self.camera_combo.currentData()
        self.update_status(f"Camera {camera_index} selected.")
        if not self.is_tracking:
            self.app_controller.switch_camera(camera_index)

    def _on_start_clicked(self):
        self.app_controller.start_tracking()

    def _on_stop_clicked(self):
        self.app_controller.stop_tracking()

    def get_selected_camera(self) -> int:
        return self.camera_combo.currentData()

    def set_tracking_state(self, is_tracking: bool):
        self.is_tracking = is_tracking
        self.start_button.setEnabled(not is_tracking)
        self.stop_button.setEnabled(is_tracking)
        self.camera_combo.setEnabled(not is_tracking)

        if is_tracking:
            self.update_status("Tracking started. Hand tracking is active.")
        else:
            self.update_status("Tracking stopped.")

    def update_status(self, message: str):
        self.status_text.append(message)
        self.status_text.verticalScrollBar().setValue(
            self.status_text.verticalScrollBar().maximum()
        )

    def show(self):
        self.window.show()

    def update(self):
        self.qt_app.processEvents()

    def is_closed(self) -> bool:
        return not self.window.isVisible()

    def close(self):
        self.window.close()
