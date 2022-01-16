import matplotlib.pyplot as plt
import matplotlib.patches as patches

import pyautogui
import keyboard

import numpy as np
import time

import numpy as np
import time
import pytesseract
from skimage import measure, morphology, feature, color, filters
from PIL import Image



from main import *

# https://stackoverflow.com/questions/50655738/how-do-i-resolve-a-tesseractnotfounderror
pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'



if __name__ == "__main__":
    print('Press Ctrl-C to quit.')
    DEBUG = False

    # for changing location
    something_there = False
    number_of_scrolls = 0
    x, y, w, h = -1, -1, -1, -1
    bot = Bot()
    try:
        while True:
            # set location of the app
            if keyboard.is_pressed('a'):
                print("KEY PRESSED") 
                if x == -1 or y == -1:
                    x, y = pyautogui.position()
                elif w == -1 or h == -1:
                    x_, y_ = pyautogui.position()
                    w = abs(x - x_)
                    h = abs(y - y_)
                    bot.set_app_loc(x, y, w, h)

            # take photo
            if bot.loc:
                background = np.array(pyautogui.screenshot(region=(bot.x, bot.y, bot.w, bot.h)))
                print(bot.detect_coins(background))


                plt.figure(1)
                plt.imshow(background)
                plt.show()


            time.sleep(0.1)
    except KeyboardInterrupt:
        print('\n')
