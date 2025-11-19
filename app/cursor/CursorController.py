import pyautogui
from pyautogui import FailSafeException


class CursorController:
    def __init__(self):
        pyautogui.MINIMUM_DURATION = 0
        pyautogui.MINIMUM_SLEEP = 0
        pyautogui.PAUSE = 0

    def move_to(self, x: float, y: float):
        try:
            pyautogui.moveTo(x, y, duration=0, _pause=False)
        except FailSafeException:
            pass

    def click(self):
        pyautogui.click()

    def grab(self):
        pyautogui.mouseDown()

    def release(self):
        pyautogui.mouseUp()