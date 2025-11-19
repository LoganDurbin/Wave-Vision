import cv2
import numpy as np


class CameraController:
    def __init__(self, index: int = 0, size: tuple[int, int] = (1920, 1080), fps: int = 30):
        self.index = index

        self.camera = cv2.VideoCapture(index)
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, size[0])
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, size[1])
        self.camera.set(cv2.CAP_PROP_FPS, fps)

    def get_frame(self) -> np.ndarray | None:
        ret, frame = self.camera.read()
        if not ret:
            return None
        return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    def is_open(self) -> bool:
        return self.camera.isOpened()

    def __del__(self):
        if self.camera.isOpened():
            self.camera.release()
