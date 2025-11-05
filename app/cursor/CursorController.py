import pyautogui


# noinspection PyMethodMayBeStatic
class CursorController:
    def move_to(self, x: float, y: float):
        pyautogui.moveTo(x, y)

    def click(self):
        pyautogui.click()

    def grab(self):
        pyautogui.mouseDown()

    def release(self):
        pyautogui.mouseUp()