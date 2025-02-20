import pyautogui
import time

try:
    while True:
        x, y = pyautogui.position()
        print(f"X: {x}, Y: {y}", end="\r")  # \r overwrites the previous line
        time.sleep(0.1)  # Adjust the update frequency (lower = faster)
except KeyboardInterrupt:
    print("\nMouse position tracking stopped.")