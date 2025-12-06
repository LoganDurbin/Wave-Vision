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
        self.last_landmarks = None
        self.smoothed_x = None
        self.smoothed_y = None
        self.alpha = 0.3
        self.sensitivity = 1.0
        self.pinch_threshold = 0.05
        
        # normalized from 0.0-1.0
        self.area_top_left_x = 0.0
        self.area_top_left_y = 0.0
        self.area_bottom_right_x = 1.0
        self.area_bottom_right_y = 1.0

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

            self.last_landmarks = [(lm.x, lm.y) for lm in landmarks]

            thumb_tip = landmarks[4]
            index_tip = landmarks[8]

            x_norm = (thumb_tip.x + index_tip.x) / 2
            y_norm = (thumb_tip.y + index_tip.y) / 2

            # Map coordinates within custom area bounds
            area_width = self.area_bottom_right_x - self.area_top_left_x
            area_height = self.area_bottom_right_y - self.area_top_left_y
            
            # Normalize position within the custom area (0.0-1.0)
            if area_width > 0 and area_height > 0:
                x_in_area = (x_norm - self.area_top_left_x) / area_width
                y_in_area = (y_norm - self.area_top_left_y) / area_height
            else:
                x_in_area = x_norm
                y_in_area = y_norm
            
            # Clamp to 0.0-1.0 range
            x_in_area = max(0.0, min(1.0, x_in_area))
            y_in_area = max(0.0, min(1.0, y_in_area))

            screen_width, screen_height = pyautogui.size()

            # Map to screen coordinates (and thus mirror x because the camera flips it)
            x_screen = (1 - x_in_area) * screen_width * self.sensitivity
            y_screen = y_in_area * screen_height * self.sensitivity

            x_screen = max(0, min(screen_width, x_screen))
            y_screen = max(0, min(screen_height, y_screen))

            if self.smoothed_x is None:
                self.smoothed_x = x_screen
                self.smoothed_y = y_screen
            else:
                self.smoothed_x = self.alpha * x_screen + (1 - self.alpha) * self.smoothed_x
                self.smoothed_y = self.alpha * y_screen + (1 - self.alpha) * self.smoothed_y

            distance = ((thumb_tip.x - index_tip.x) ** 2 + (thumb_tip.y - index_tip.y) ** 2) ** 0.5
            pressed = distance < self.pinch_threshold

            self.last_result = TrackingResult(
                cursor_position_x=int(self.smoothed_x),
                cursor_position_y=int(self.smoothed_y),
                pressed=pressed
            )
        else:
            self.last_result = None
            self.last_landmarks = None

    def track(self, frame: np.ndarray, timestamp_ms: int) -> TrackingResult | None:
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
        self.landmarker.detect_async(mp_image, timestamp_ms)
        return self.last_result
