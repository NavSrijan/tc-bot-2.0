from selenium import webdriver
import time
import subprocess
import os
import signal
import pyautogui as py

driver = webdriver.Chrome()

driver.get("https://g.co/kgs/RsCZpD")


def start_spin():
    driver.find_element_by_id("t86JCe").click()
    driver.find_element_by_id("t86JCe").click()
    driver.find_element_by_id("t86JCe").click()
    driver.find_element_by_id("t86JCe").click()

time.sleep(10)
text = driver.find_element_by_class_name("gws-csf-spinner__dark-result-highlight").text
cmd = "ffmpeg -video_size 264x251 -framerate 25 -f x11grab -i :0.0+2296,385 {}.mp4"

for i in range(0, 1):
    pro = subprocess.Popen(cmd.format(i),
                           stdout=subprocess.PIPE,
                           shell=True,
                           preexec_fn=os.setsid)
    py.click(2431,662)

    time.sleep(10)

    os.killpg(os.getpgid(pro.pid), signal.SIGTERM)
    text = driver.find_element_by_class_name("gws-csf-spinner__dark-result-highlight").text
