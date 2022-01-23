import matplotlib.pyplot as plt
import matplotlib.patches as patches

import pyautogui
import keyboard

import numpy as np
import time

import numpy as np
import time

from jw_bot import Bot

if __name__ == "__main__":
    print('Press Ctrl-C to quit.')
    DEBUG = False

    # for changing location
    something_there = False
    number_of_scrolls = 0
    max_scrolls = 10

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
                
                if keyboard.is_pressed("q"):
                    raise KeyboardInterrupt

                # get coins
                bot.collect_coin()

                # get supply drops
                bot.collect_supply_drop()                                 


                # get dinos
                bot.collect_dino()

                if number_of_scrolls > max_scrolls:
                    # move location
                    print("--"*10)
                    print("CHANGING LOCATION")
                    bot.change_location()
                    number_of_scrolls = 0
                    
                # if not something_there:
                print("--"*10)
                print("CHANGING VIEW")
                # print("--"*10)
                pyautogui.click(x=bot.x+bot.w//2, y=bot.y+bot.h//2)
                time.sleep(1)

                background = np.array(pyautogui.screenshot(region=(bot.x, bot.y, bot.w, bot.h)))
                pos = bot.locate_x_button(background)
                if pos:
                    pyautogui.click(x=bot.x+pos[1], y=bot.y+pos[0])
                    time.sleep(1)  


                pyautogui.moveTo(bot.x+bot.w//2, bot.y+bot.h//2, 0.1)
                pyautogui.scroll(90)
                time.sleep(1)
                number_of_scrolls += 1
                

            time.sleep(0.1)
    except KeyboardInterrupt:
        print('\n')
