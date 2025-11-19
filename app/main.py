from app.camera.CameraController import CameraController
from app.cursor.CursorController import CursorController
from app.system.SystemController import SystemController
from app.ui.UIController import UIController
from app.tracking.TrackingController import TrackingController
from app.tracking.TrackingParams import TrackingParams
from app.preferences.PreferencesController import PreferencesController, Profile


class Application:
    def __init__(self):
        self.preferences = PreferencesController()
        profiles = self.preferences.get_all_profiles()
        self.current_profile = profiles[0] if profiles else None

        self.tracking_controller = TrackingController(
            TrackingParams(
                area_size_x=640,
                area_size_y=480,
                model_path="models/hand_landmarker.task"
            )
        )
        self.cursor_controller = CursorController()
        self.camera_controller = CameraController(
            self.current_profile.camera_index,
            size=(640, 480),
            fps=60
        )
        self.system_controller = SystemController(
            camera_controller=self.camera_controller,
            tracking_controller=self.tracking_controller,
            cursor_controller=self.cursor_controller
        )

        self._apply_profile_settings()
        self.ui = UIController(self)
        self.ui.load_profiles(
            [p.name for p in profiles],
            self.current_profile.name
        )
        self.ui.update_settings_ui(
            self.current_profile.camera_index,
            self.current_profile.sensitivity,
            self.current_profile.smoothing,
            self.current_profile.pinch_threshold
        )

    def _apply_profile_settings(self):
        self.tracking_controller.alpha = self.current_profile.smoothing
        self.tracking_controller.sensitivity = self.current_profile.sensitivity
        self.tracking_controller.pinch_threshold = self.current_profile.pinch_threshold

    def load_profile(self, profile_name: str):
        profile = self.preferences.get_profile_by_name(profile_name)
        if profile:
            self.current_profile = profile
            self._apply_profile_settings()
            self.ui.update_settings_ui(
                profile.camera_index,
                profile.sensitivity,
                profile.smoothing,
                profile.pinch_threshold
            )
            self.switch_camera(profile.camera_index)

    def update_camera(self, camera_index: int):
        self.current_profile.camera_index = camera_index
        self.preferences.update_profile(self.current_profile)
        self.switch_camera(camera_index)

    def update_sensitivity(self, value: float):
        self.current_profile.sensitivity = value
        self.tracking_controller.sensitivity = value
        self.preferences.update_profile(self.current_profile)

    def update_smoothing(self, value: float):
        self.current_profile.smoothing = value
        self.tracking_controller.alpha = value
        self.preferences.update_profile(self.current_profile)

    def update_pinch_threshold(self, value: float):
        self.current_profile.pinch_threshold = value
        self.tracking_controller.pinch_threshold = value
        self.preferences.update_profile(self.current_profile)

    def create_profile(self, name: str) -> bool:
        if self.preferences.get_profile_by_name(name):
            return False

        new_profile = Profile(
            id=None,
            name=name,
            camera_index=self.current_profile.camera_index,
            sensitivity=self.current_profile.sensitivity,
            smoothing=self.current_profile.smoothing,
            pinch_threshold=self.current_profile.pinch_threshold
        )
        profile_id = self.preferences.create_profile(new_profile)
        new_profile.id = profile_id

        profiles = self.preferences.get_all_profiles()
        self.ui.load_profiles([p.name for p in profiles], name)
        self.current_profile = new_profile
        self.ui.update_status(f"Profile '{name}' created.")
        return True

    def save_current_profile(self):
        self.preferences.update_profile(self.current_profile)

    def rename_profile(self, old_name: str, new_name: str) -> bool:
        if self.preferences.get_profile_by_name(new_name):
            return False

        self.current_profile.name = new_name
        self.preferences.update_profile(self.current_profile)

        profiles = self.preferences.get_all_profiles()
        self.ui.load_profiles([p.name for p in profiles], new_name)
        self.ui.update_status(f"Profile renamed to '{new_name}'.")
        return True

    def delete_profile(self, name: str) -> bool:
        profiles = self.preferences.get_all_profiles()
        if len(profiles) <= 1:
            return False

        profile = self.preferences.get_profile_by_name(name)
        if profile and profile.id:
            self.preferences.delete_profile(profile.id)

            profiles = self.preferences.get_all_profiles()
            self.current_profile = profiles[0]
            self._apply_profile_settings()
            self.ui.load_profiles([p.name for p in profiles], self.current_profile.name)
            self.ui.update_settings_ui(
                self.current_profile.camera_index,
                self.current_profile.sensitivity,
                self.current_profile.smoothing,
                self.current_profile.pinch_threshold
            )
            self.switch_camera(self.current_profile.camera_index)
            self.ui.update_status(f"Profile '{name}' deleted.")
            return True
        return False

    def switch_camera(self, camera_index: int):
        try:
            was_running = self.system_controller.is_running
            if was_running:
                self.system_controller.stop()

            del self.camera_controller
            self.camera_controller = CameraController(camera_index, size=(640, 480), fps=60)
            self.system_controller = SystemController(
                camera_controller=self.camera_controller,
                tracking_controller=self.tracking_controller,
                cursor_controller=self.cursor_controller
            )

            if was_running:
                self.system_controller.start()

            self.ui.update_status(f"Switched to camera {camera_index}")
        except Exception as e:
            self.ui.update_status(f"Error switching to camera {camera_index}: {e}")

    def start_tracking(self):
        if self.camera_controller.is_open():
            self.system_controller.start()
            self.ui.set_tracking_state(True)
            self.ui.update_status("Tracking system started.")
        else:
            self.ui.update_status("Error: Camera not available.")

    def stop_tracking(self):
        self.system_controller.stop()
        self.ui.set_tracking_state(False)
        self.ui.update_status("Tracking system stopped.")

    def run(self):
        self.ui.show()

        try:
            while not self.ui.is_closed():
                self.ui.update()
                self.system_controller.update()
        except KeyboardInterrupt:
            print("\nShutting down...")
        finally:
            self.system_controller.stop()
            self.ui.close()
            self.preferences.close()


if __name__ == "__main__":
    Application().run()
