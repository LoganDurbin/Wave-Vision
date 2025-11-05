from dataclasses import dataclass


@dataclass
class TrackingParams:
    """
    :param area_size_x: Width in pixels of actual tracking box. Mapped to the full width of the monitor.
    :param area_size_y: Height in pixels of actual tracking box. Mapped to the full height of the monitor.
    :param model_path: Path to the hand landmarker model file.
    """
    area_size_x: float
    area_size_y: float
    model_path: str
