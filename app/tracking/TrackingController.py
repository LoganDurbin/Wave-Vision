import numpy as np
import mediapipe as mp
import pyautogui
from mediapipe.tasks.python.vision.hand_landmarker import HandLandmarkerResult

from app.tracking.TrackingParams import TrackingParams
from app.tracking.TrackingResult import TrackingResult


class TrackingController:
    def __init__(self, params: TrackingParams):
        self.params = params
        self.last_result = None
        self.screen_width, self.screen_height = pyautogui.size()
        self.smoothed_x = None
        self.smoothed_y = None
        self.alpha = 0.3

        options = mp.tasks.vision.HandLandmarkerOptions(
            base_options=mp.tasks.BaseOptions(model_asset_path=params.model_path),
            num_hands=1,
            running_mode=mp.tasks.vision.RunningMode.LIVE_STREAM,
            result_callback=self.process_result
        )

        self.landmarker = mp.tasks.vision.HandLandmarker.create_from_options(options)

    def process_result(self, result: HandLandmarkerResult, frame: mp.Image, timestamp_ms: int):
        if result.hand_landmarks:
            landmarks = result.hand_landmarks[0]

            thumb_tip = landmarks[4]
            index_tip = landmarks[8]

            x_norm = (thumb_tip.x + index_tip.x) / 2
            y_norm = (thumb_tip.y + index_tip.y) / 2

            x_screen = (1 - x_norm) * self.screen_width
            y_screen = y_norm * self.screen_height

            if self.smoothed_x is None:
                self.smoothed_x = x_screen
                self.smoothed_y = y_screen
            else:
                self.smoothed_x = self.alpha * x_screen + (1 - self.alpha) * self.smoothed_x
                self.smoothed_y = self.alpha * y_screen + (1 - self.alpha) * self.smoothed_y

            distance = ((thumb_tip.x - index_tip.x) ** 2 + (thumb_tip.y - index_tip.y) ** 2) ** 0.5
            pressed = distance < 0.10

            self.last_result = TrackingResult(
                cursor_position_x=int(self.smoothed_x),
                cursor_position_y=int(self.smoothed_y),
                pressed=pressed
            )
        else:
            self.last_result = None

    def track(self, frame: np.ndarray, timestamp_ms: int) -> TrackingResult | None:
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
        self.landmarker.detect_async(mp_image, timestamp_ms)
        return self.last_result
