import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python.vision.hand_landmarker import HandLandmarkerResult

from app.tracking.TrackingParams import TrackingParams
from app.tracking.TrackingResult import TrackingResult


class TrackingController:
    def __init__(self, params: TrackingParams):
        print("Foo")
        self.params = params

        base_options = mp.tasks.BaseOptions
        hand_landmarker = mp.tasks.vision.HandLandmarker
        hand_landmarker_options = mp.tasks.vision.HandLandmarkerOptions
        vision_running_mode = mp.tasks.vision.RunningMode

        options = hand_landmarker_options(
            base_options=base_options(
                model_asset_path=self.params.model_path
            ),
            num_hands=1,
            running_mode=vision_running_mode.LIVE_STREAM,
            result_callback=lambda result, _, __: self.process_result(result)
        )

        self.landmarker = hand_landmarker.create_from_options(options)
        self.last_result = None

    def process_result(self, result: HandLandmarkerResult):
        print(len(result.hand_landmarks))

    def track(self, frame: np.ndarray, timestamp_ms: int) -> TrackingResult | None:
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
        self.landmarker.detect_async(mp_image, timestamp_ms)
        return self.last_result
