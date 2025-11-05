import time

from app.camera.CameraController import CameraController
from app.cursor.CursorController import CursorController
from app.tracking.TrackingController import TrackingController


class SystemController:
    def __init__(self, camera_controller: CameraController, tracking_controller: TrackingController, cursor_controller: CursorController):
        self.camera_controller = camera_controller
        self.tracking_controller = tracking_controller
        self.cursor_controller = cursor_controller

    def start(self):
        start = time.time()
        while True:
            frame = self.camera_controller.get_frame()
            if frame is not None:
                tracking_result = self.tracking_controller.track(frame, int((time.time() - start) * 1000))
                if tracking_result is not None:
                    self.cursor_controller.move_to(tracking_result.cursor_position_x, tracking_result.cursor_position_y)
