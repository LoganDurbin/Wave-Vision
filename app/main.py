from app.camera.CameraController import CameraController
from app.cursor.CursorController import CursorController
from app.system.SystemController import SystemController
from app.ui.UIController import UIController
from app.tracking.TrackingController import TrackingController
from app.tracking.TrackingParams import TrackingParams


class Application:
    def __init__(self, camera_index: int = 0):
        self.tracking_controller = TrackingController(
            TrackingParams(area_size_x=640, area_size_y=480, model_path="models/hand_landmarker.task")
        )
        self.cursor_controller = CursorController()
        self.camera_controller = CameraController(camera_index, size=(640, 480), fps=60)
        self.system_controller = SystemController(
            camera_controller=self.camera_controller,
            tracking_controller=self.tracking_controller,
            cursor_controller=self.cursor_controller
        )
        self.ui = UIController(self)

    def switch_camera(self, camera_index: int):
        try:
            was_running = self.system_controller.is_running
            if was_running:
                self.system_controller.stop()

            del self.camera_controller
            self.camera_controller = CameraController(camera_index, size=(1920, 1080), fps=30)
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


if __name__ == "__main__":
    Application().run()
