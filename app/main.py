from app.camera.CameraController import CameraController
from app.cursor.CursorController import CursorController
from app.system.SystemController import SystemController
from app.ui.UIController import UIController
from app.tracking.TrackingController import TrackingController
from app.tracking.TrackingParams import TrackingParams
from app.preferences.PreferencesController import PreferencesController, Profile
from app.sound.SoundController import SoundController


class Application:
    def __init__(self):
        self.preferences = PreferencesController()
        profiles = self.preferences.get_all_profiles()
        self.current_profile = profiles[0] if profiles else None

        self.cursor_controller = CursorController()
        self.sound_controller = SoundController()
        self.camera_controller = CameraController(
            self.current_profile.camera_index,
            fps=60
        )

        camera_width, camera_height = self.camera_controller.get_size()
        self.tracking_controller = TrackingController(
            TrackingParams(
                area_size_x=camera_width,
                area_size_y=camera_height,
                model_path="models/hand_landmarker.task"
            )
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

        self.tracking_controller.area_top_left_x = self.current_profile.area_top_left_x
        self.tracking_controller.area_top_left_y = self.current_profile.area_top_left_y
        self.tracking_controller.area_bottom_right_x = self.current_profile.area_bottom_right_x
        self.tracking_controller.area_bottom_right_y = self.current_profile.area_bottom_right_y

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
            self.ui._update_area_visualization()
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

    def update_area_bounds(self, bounds: tuple[float, float, float, float]):
        top_left_x, top_left_y, bottom_right_x, bottom_right_y = bounds
        self.current_profile.area_top_left_x = top_left_x
        self.current_profile.area_top_left_y = top_left_y
        self.current_profile.area_bottom_right_x = bottom_right_x
        self.current_profile.area_bottom_right_y = bottom_right_y
        self.tracking_controller.area_top_left_x = top_left_x
        self.tracking_controller.area_top_left_y = top_left_y
        self.tracking_controller.area_bottom_right_x = bottom_right_x
        self.tracking_controller.area_bottom_right_y = bottom_right_y
        self.preferences.update_profile(self.current_profile)

    def reset_area(self):
        self.current_profile.area_top_left_x = 0.0
        self.current_profile.area_top_left_y = 0.0
        self.current_profile.area_bottom_right_x = 1.0
        self.current_profile.area_bottom_right_y = 1.0
        self.tracking_controller.area_top_left_x = 0.0
        self.tracking_controller.area_top_left_y = 0.0
        self.tracking_controller.area_bottom_right_x = 1.0
        self.tracking_controller.area_bottom_right_y = 1.0
        self.preferences.update_profile(self.current_profile)
        self.ui.update_status("Area reset to full view.")

    def get_area_bounds(self) -> tuple[float, float, float, float]:
        return (
            self.current_profile.area_top_left_x,
            self.current_profile.area_top_left_y,
            self.current_profile.area_bottom_right_x,
            self.current_profile.area_bottom_right_y
        )

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
            self.camera_controller = CameraController(camera_index, fps=60)

            camera_width, camera_height = self.camera_controller.get_size()
            self.tracking_controller.params.area_size_x = camera_width
            self.tracking_controller.params.area_size_y = camera_height
            
            self.system_controller = SystemController(
                camera_controller=self.camera_controller,
                tracking_controller=self.tracking_controller,
                cursor_controller=self.cursor_controller
            )

            if was_running:
                self.system_controller.start()

            self.ui.update_status(f"Switched to camera {camera_index} ({camera_width}x{camera_height})")
        except Exception as e:
            self.ui.update_status(f"Error switching to camera {camera_index}: {e}")

    def start_tracking(self):
        if self.camera_controller.is_open():
            self.system_controller.start()
            self.sound_controller.play_start_sound()
            self.ui.set_tracking_state(True)
            self.ui.update_status("Tracking system started.")
        else:
            self.ui.update_status("Error: Camera not available.")

    def stop_tracking(self):
        self.system_controller.stop()
        self.sound_controller.play_stop_sound()
        self.ui.set_tracking_state(False)
        self.ui.update_status("Tracking system stopped.")

    def run(self):
        self.ui.show()
        self.ui._update_area_visualization()

        try:
            while not self.ui.is_closed():
                self.ui.update()
                self.system_controller.update()

                self.ui.update_hand_visualization(self.tracking_controller.last_landmarks)
        except KeyboardInterrupt:
            print("\nShutting down...")
        finally:
            self.system_controller.stop()
            self.ui.close()
            self.preferences.close()


if __name__ == "__main__":
    Application().run()
