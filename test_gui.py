import subprocess
import time
import pyautogui
import pynput


# Lancer l'application
subprocess.Popen(['python', 'log2files.py'])

mouse = pynput.mouse.Controller()
button = pynput.mouse.Button
keyboard = pynput.keyboard.Controller()

# Attendre que l'application soit lancée
time.sleep(3)

trace_file_location = pyautogui.locateOnScreen('./test_datasets/trace_file.png', confidence=0.9)
x, y = pyautogui.center(trace_file_location)
pyautogui.moveTo(int(x/2),int(y/2))
mouse.click(button.left)
keyboard.type('./test_datasets/file.log')

time.sleep(1)

trace_file_location = pyautogui.locateOnScreen('./test_datasets/out_folder.png', confidence=0.9)
x, y = pyautogui.center(trace_file_location)
pyautogui.moveTo(int(x/2),int(y/2))
mouse.click(button.left)
keyboard.type('out')

time.sleep(1)

process_button_location = pyautogui.locateOnScreen('./test_datasets/process_button_image.png', confidence=0.9)

x, y = pyautogui.center(process_button_location)
pyautogui.moveTo(int(x/2),int(y/2))
mouse.click(button.left)

time.sleep(40)

ok_button_location = pyautogui.locateOnScreen('./test_datasets/ok_button.png', confidence=0.9)

x, y = pyautogui.center(ok_button_location)
pyautogui.moveTo(int(x/2),int(y/2))
mouse.click(button.left)
