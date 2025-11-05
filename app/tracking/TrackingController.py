import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python.vision.hand_landmarker import HandLandmarkerResult

from app.tracking.TrackingParams import TrackingParams
from app.tracking.TrackingResult import TrackingResult


class TrackingController:
    def __init__(self, params: TrackingParams):
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
            result_callback=lambda result, img, time_ms: self.process_result(result, img, time_ms)
        )

        self.landmarker = hand_landmarker.create_from_options(options)
        self.last_result = None


    def process_result(self, result: HandLandmarkerResult, frame: mp.Image, timestamp_ms: int):
        print(f"Detected {len(result.hand_landmarks)} hands.")

        cv2.namedWindow("Image", cv2.WINDOW_NORMAL)
        cv2.imshow("Image", np.copy(frame.numpy_view()))

        if len(result.hand_landmarks) > 0:
            landmarks = result.hand_landmarks[0]
            x_sum = sum(landmark.x for landmark in landmarks)
            y_sum = sum(landmark.y for landmark in landmarks)
            x_avg = x_sum / len(landmarks)
            y_avg = y_sum / len(landmarks)

            self.last_result = TrackingResult(
                cursor_position_x=int(x_avg),
                cursor_position_y=int(y_avg),
                pressed=False
            )

    def track(self, frame: np.ndarray, timestamp_ms: int) -> TrackingResult | None:
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
        self.landmarker.detect_async(mp_image, timestamp_ms)
        return self.last_result
