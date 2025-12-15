import pytest
import os

if "DISPLAY" not in os.environ:
    pytest.skip("No DISPLAY available", allow_module_level=True)

pyautogui = pytest.importorskip("pyautogui")

from app.cursor.CursorController import CursorController


def test_init_sets_pyautogui_timing_params():
    pyautogui.MINIMUM_DURATION = 0.1
    pyautogui.MINIMUM_SLEEP = 0.1
    pyautogui.PAUSE = 0.1

    CursorController()

    assert pyautogui.MINIMUM_DURATION == 0
    assert pyautogui.MINIMUM_SLEEP == 0
    assert pyautogui.PAUSE == 0


def test_move_to_calls_moveTo_and_handles_failsafe(monkeypatch):
    recorded = []

    def fake_move_to(x, y, *, duration=0, _pause=False):
        recorded.append((x, y, duration, _pause))

    monkeypatch.setattr(pyautogui, "moveTo", fake_move_to)

    ctrl = CursorController()
    ctrl.move_to(10, 20)

    assert recorded == [(10, 20, 0, False)]

    # Now simulate pyautogui's failsafe being triggered and ensure it is swallowed.
    def raise_failsafe(x, y, *, duration=0, _pause=False):
        raise pyautogui.FailSafeException()

    monkeypatch.setattr(pyautogui, "moveTo", raise_failsafe)

    # Should not raise
    ctrl.move_to(0, 0)


def test_click_calls_pyautogui_click(monkeypatch):
    calls = {"count": 0}

    def fake_click():
        calls["count"] += 1

    monkeypatch.setattr(pyautogui, "click", fake_click)

    ctrl = CursorController()
    ctrl.click()

    assert calls["count"] == 1


def test_grab_and_release_call_mouse_down_up(monkeypatch):
    calls = {"down": 0, "up": 0}

    def fake_down():
        calls["down"] += 1

    def fake_up():
        calls["up"] += 1

    monkeypatch.setattr(pyautogui, "mouseDown", fake_down)
    monkeypatch.setattr(pyautogui, "mouseUp", fake_up)

    ctrl = CursorController()
    ctrl.grab()
    ctrl.release()

    assert calls == {"down": 1, "up": 1}
