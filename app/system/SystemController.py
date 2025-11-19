import time

from app.camera.CameraController import CameraController
from app.cursor.CursorController import CursorController
from app.tracking.TrackingController import TrackingController


class SystemController:
    def __init__(self, camera_controller: CameraController, tracking_controller: TrackingController, cursor_controller: CursorController):
        self.camera_controller = camera_controller
        self.tracking_controller = tracking_controller
        self.cursor_controller = cursor_controller
        self.is_running = False
        self.was_pressed = False

    def start(self):
        self.is_running = True

    def stop(self):
        self.is_running = False

    def update(self):
        if not self.is_running:
            return

        frame = self.camera_controller.get_frame()
        if frame is not None:
            timestamp_ms = int(time.time() * 1000)
            tracking_result = self.tracking_controller.track(frame, timestamp_ms)
            if tracking_result is not None:
                self.cursor_controller.move_to(tracking_result.cursor_position_x, tracking_result.cursor_position_y)

                if tracking_result.pressed and not self.was_pressed:
                    self.cursor_controller.grab()
                    self.was_pressed = True
                elif not tracking_result.pressed and self.was_pressed:
                    self.cursor_controller.release()
                    self.was_pressed = False
