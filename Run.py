import os
import time

os.system("start app.py")
time.sleep(5)
os.system('start chrome.exe --app="http://127.0.0.1:5000"')