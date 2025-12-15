import pytest
from app.camera.CameraController import CameraController


def test_camera_is_not_open_for_invalid_index():
    cam = CameraController(index=-1)
    # On all platforms, an invalid index should not open.
    assert cam.is_open() is False


def test_get_frame_returns_none_when_camera_not_open():
    cam = CameraController(index=9999)
    # Attempt to read a frame; should return None if not opened.
    frame = cam.get_frame()
    assert frame is None


def test_get_size_is_non_negative_even_when_not_open():
    cam = CameraController(index=9999)
    w, h = cam.get_size()
    assert w >= 0 and h >= 0
