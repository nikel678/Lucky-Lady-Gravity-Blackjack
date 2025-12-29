import pyautogui
import time

print('Press Ctrl-C to quit.')
try:
	while True:
		x, y = pyautogui.position()
		print(f"Current mouse position: x = {x}, y = {y}")
		time.sleep(1)
except KeyboardInterrupt:
	print('\nDone.')