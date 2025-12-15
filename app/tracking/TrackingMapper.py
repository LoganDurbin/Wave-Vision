from __future__ import annotations

from dataclasses import dataclass

from app.tracking.TrackingResult import TrackingResult


@dataclass
class TrackingMapper:
    alpha: float = 0.3
    sensitivity: float = 1.0
    pinch_threshold: float = 0.05

    # normalized from 0.0 to 1.0
    area_top_left_x: float = 0.0
    area_top_left_y: float = 0.0
    area_bottom_right_x: float = 1.0
    area_bottom_right_y: float = 1.0

    # internal smoothing state
    _smoothed_x: float | None = None
    _smoothed_y: float | None = None

    def reset(self) -> None:
        self._smoothed_x = None
        self._smoothed_y = None

    def process_landmarks(
        self,
        thumb_xy: tuple[float, float],
        index_xy: tuple[float, float],
        screen_width: int,
        screen_height: int,
    ) -> TrackingResult:
        tx, ty = thumb_xy
        ix, iy = index_xy

        # Average fingertips
        x_norm = (tx + ix) / 2.0
        y_norm = (ty + iy) / 2.0

        area_width = self.area_bottom_right_x - self.area_top_left_x
        area_height = self.area_bottom_right_y - self.area_top_left_y

        if area_width > 0 and area_height > 0:
            x_in_area = (x_norm - self.area_top_left_x) / area_width
            y_in_area = (y_norm - self.area_top_left_y) / area_height
        else:
            x_in_area = x_norm
            y_in_area = y_norm

        # Clamp to [0, 1]
        x_in_area = max(0.0, min(1.0, x_in_area))
        y_in_area = max(0.0, min(1.0, y_in_area))

        # Map to screen coordinates (and mirror X)
        x_screen = (1.0 - x_in_area) * float(screen_width) * self.sensitivity
        y_screen = y_in_area * float(screen_height) * self.sensitivity

        x_screen = max(0.0, min(float(screen_width), x_screen))
        y_screen = max(0.0, min(float(screen_height), y_screen))

        # Exp smoothing
        if self._smoothed_x is None:
            self._smoothed_x = x_screen
            self._smoothed_y = y_screen
        else:
            a = self.alpha
            self._smoothed_x = a * x_screen + (1.0 - a) * self._smoothed_x
            self._smoothed_y = a * y_screen + (1.0 - a) * self._smoothed_y

        # Pinch detection
        dx = tx - ix
        dy = ty - iy
        distance = (dx * dx + dy * dy) ** 0.5
        pressed = distance < self.pinch_threshold

        return TrackingResult(
            cursor_position_x=int(self._smoothed_x),
            cursor_position_y=int(self._smoothed_y),
            pressed=pressed,
        )
