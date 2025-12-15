import numpy as np
import mediapipe as mp
import pyautogui
from mediapipe.tasks.python.vision.hand_landmarker import HandLandmarkerResult

from app.tracking.TrackingParams import TrackingParams
from app.tracking.TrackingResult import TrackingResult
from app.tracking.TrackingMapper import TrackingMapper


class TrackingController:
    def __init__(self, params: TrackingParams):
        self.params = params
        self.last_result = None
        self.last_landmarks = None

        # Pure mapping/smoothing component
        self.mapper = TrackingMapper()

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

            screen_width, screen_height = pyautogui.size()

            self.last_result = self.mapper.process_landmarks(
                (thumb_tip.x, thumb_tip.y),
                (index_tip.x, index_tip.y),
                screen_width,
                screen_height,
            )
        else:
            self.last_result = None
            self.last_landmarks = None

    def track(self, frame: np.ndarray, timestamp_ms: int) -> TrackingResult | None:
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
        self.landmarker.detect_async(mp_image, timestamp_ms)
        return self.last_result
