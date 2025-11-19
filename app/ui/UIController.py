from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                                QHBoxLayout, QLabel, QComboBox, QPushButton,
                                QTextEdit, QGroupBox, QDoubleSpinBox, QInputDialog,
                                QMessageBox)
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
        self.window.setFixedSize(600, 550)

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

    def _on_profile_selected(self):
        profile_name = self.profile_combo.currentText()
        if profile_name:
            self.app_controller.load_profile(profile_name)

    def _on_camera_selected(self):
        camera_index = self.camera_combo.currentData()
        if not self.is_tracking:
            self.app_controller.update_camera(camera_index)

    def _on_sensitivity_changed(self, value: float):
        self.app_controller.update_sensitivity(value)

    def _on_smoothing_changed(self, value: float):
        self.app_controller.update_smoothing(value)

    def _on_pinch_changed(self, value: float):
        self.app_controller.update_pinch_threshold(value)

    def _on_new_profile(self):
        name, ok = QInputDialog.getText(self.window, "New Profile", "Profile name:")
        if ok and name:
            success = self.app_controller.create_profile(name)
            if not success:
                QMessageBox.warning(self.window, "Error", f"Profile '{name}' already exists.")

    def _on_save_profile(self):
        self.app_controller.save_current_profile()
        self.update_status("Profile saved.")

    def _on_rename_profile(self):
        current_name = self.profile_combo.currentText()
        name, ok = QInputDialog.getText(self.window, "Rename Profile", "New profile name:", text=current_name)
        if ok and name and name != current_name:
            success = self.app_controller.rename_profile(current_name, name)
            if not success:
                QMessageBox.warning(self.window, "Error", f"Profile '{name}' already exists.")

    def _on_delete_profile(self):
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

    def _on_start_clicked(self):
        self.app_controller.start_tracking()

    def _on_stop_clicked(self):
        self.app_controller.stop_tracking()

    def load_profiles(self, profiles: list[str], current_profile: str):
        self.profile_combo.clear()
        for profile in profiles:
            self.profile_combo.addItem(profile)
        index = self.profile_combo.findText(current_profile)
        if index >= 0:
            self.profile_combo.setCurrentIndex(index)

    def update_settings_ui(self, camera_index: int, sensitivity: float, smoothing: float, pinch_threshold: float):
        for i in range(self.camera_combo.count()):
            if self.camera_combo.itemData(i) == camera_index:
                self.camera_combo.setCurrentIndex(i)
                break
        self.sensitivity_spin.setValue(sensitivity)
        self.smoothing_spin.setValue(smoothing)
        self.pinch_spin.setValue(pinch_threshold)

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
