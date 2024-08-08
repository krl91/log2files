import os
import subprocess
import time
import pyautogui
import pynput
import shutil
import filecmp


def compare_directories(dir1, dir2):
    # Comparaison des dossiers
    comparison = filecmp.dircmp(dir1, dir2)
    
    # Liste pour stocker les différences
    differences = []

    # Vérification des fichiers et sous-dossiers différents
    if comparison.left_only:
        differences.extend([os.path.join(dir1, item) for item in comparison.left_only])
    if comparison.right_only:
        differences.extend([os.path.join(dir2, item) for item in comparison.right_only])
    if comparison.diff_files:
        differences.extend([os.path.join(dir1, item) for item in comparison.diff_files])
    
    # Comparaison récursive des sous-dossiers
    for subdir in comparison.common_dirs:
        subdir1 = os.path.join(dir1, subdir)
        subdir2 = os.path.join(dir2, subdir)
        differences.extend(compare_directories(subdir1, subdir2))
    
    return differences

# Lancer l'application
subprocess.Popen(['python', 'log2files.py'])

mouse = pynput.mouse.Controller()
button = pynput.mouse.Button
keyboard = pynput.keyboard.Controller()

OUT_DIR = "out"
OUT_DIR_REF = "./test_datasets/out.ref"
LOG_FILE_REF = "./test_datasets/file.log"

shutil.rmtree(OUT_DIR)

# Attendre que l'application soit lancée
time.sleep(3)

trace_file_location = pyautogui.locateOnScreen('./test_datasets/trace_file.png', confidence=0.9)
x, y = pyautogui.center(trace_file_location)
pyautogui.moveTo(int(x/2),int(y/2))
mouse.click(button.left)
keyboard.type(LOG_FILE_REF)

time.sleep(1)

trace_file_location = pyautogui.locateOnScreen('./test_datasets/out_folder.png', confidence=0.9)
x, y = pyautogui.center(trace_file_location)
pyautogui.moveTo(int(x/2),int(y/2))
mouse.click(button.left)
keyboard.type(OUT_DIR)

time.sleep(1)

process_button_location = pyautogui.locateOnScreen('./test_datasets/process_button_image.png', confidence=0.9)

x, y = pyautogui.center(process_button_location)
pyautogui.moveTo(int(x/2),int(y/2))
mouse.click(button.left)

time.sleep(60)

ok_button_location = pyautogui.locateOnScreen('./test_datasets/ok_button.png', confidence=0.9)

x, y = pyautogui.center(ok_button_location)
pyautogui.moveTo(int(x/2),int(y/2))
mouse.click(button.left)

keyboard.press(pynput.keyboard.Key.cmd)
keyboard.press('q')
keyboard.release('q')
keyboard.release(pynput.keyboard.Key.cmd)

if len(compare_directories(OUT_DIR, OUT_DIR_REF)) == 0:
    print("OK")
else:
    print("OK")