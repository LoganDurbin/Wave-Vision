from dataclasses import dataclass


@dataclass
class TrackingResult:
    cursor_position_x: float
    cursor_position_y: float
    pressed: bool